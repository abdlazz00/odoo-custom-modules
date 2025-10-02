# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LibraryBorrow(models.Model):
    _name = 'library.borrow'
    _description = 'Peminjaman Buku'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='ID Peminjaman', readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True)
    member_id = fields.Many2one('res.partner', string='Anggota', required=True)
    borrow_date = fields.Date(string='Tanggal Pinjam', required=True, default=fields.Date.today)
    return_due_date = fields.Date(string='Tanggal Jatuh Tempo', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Dipinjam'),
        ('returned', 'Dikembalikan'),
        ('overdue', 'Terlambat'),
        ('cancelled', 'Dibatalkan'),
    ], default='draft', string='Status')

    is_overdue = fields.Boolean(string='Terlambat', default=False, store=True)
    total_books = fields.Integer(string='Total Buku', compute='_compute_total_books', store=True)
    total_fine = fields.Float(string='Total Denda', store=True)
    borrow_line_ids = fields.One2many(
        'library.borrow.lines', 'borrow_id', string='Detail Buku')
    fine_adjustment_ids = fields.One2many('library.fine.adjustment', 'borrow_id', string='Detail Denda')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('library.borrow.sequence') or 'New'
        return super(LibraryBorrow, self).create(vals)

    @api.depends('borrow_line_ids.book_id')
    def _compute_total_books(self):
        for rec in self:
            rec.total_books = len(rec.borrow_line_ids)

    @api.model
    def check_overdue_and_calculate_fine(self):
        overdue_borrows = self.search([('state', '=', 'borrowed'),
                                       ('return_due_date', '<', fields.Date.today())
                                       ])
        daily_fine = self.env['ir.config_parameter'].sudo().get_param('library_management.daily_fine_amount', 1000.0)
        for borrow in overdue_borrows:
            days_overdue = (fields.Date.today() - borrow.return_due_date).days
            total_fine = days_overdue * float(daily_fine)

            borrow.write({
                'is_overdue': True,
                'total_fine': total_fine,
            })
            borrow.message_post(body=_(f"Denda otomatis dihitung. Total denda: {total_fine}"))

    def action_borrow(self):
        for rec in self:
            if not rec.borrow_line_ids:
                raise UserError(_('Anda tidak bisa meminjam tanpa buku.'))
            for line in rec.borrow_line_ids:
                if line.book_id.stock < line.quantity:
                    raise UserError(_("Stok buku '%s' tidak mencukupi untuk peminjaman ini. Stok tersedia: %d") % (line.book_id.name, line.book_id.stock))

                line.book_id.stock -= line.quantity
                line.book_id._compute_is_available()

            rec.state = 'borrowed'
            rec.message_post(body=_("Peminjaman berhasil dikonfirmasi."))
        return True

    def action_return(self):
        for rec in self:
            for line in rec.borrow_line_ids:
                if not line.is_returned:
                    line.is_returned = True
                    line.book_id.stock += line.quantity
                    line.book_id._compute_is_available()

            if rec.total_fine > 0:
                self.env['library.fine'].create({
                    'borrow_id': rec.id,
                    'amount_paid': rec.total_fine,
                    'state': 'draft',
                })
            rec.state = 'returned'
            rec.message_post(body=_("Semua buku telah dikembalikan. Transaksi selesai."))


class LibraryBorrowLines(models.Model):
    _name = 'library.borrow.lines'
    _description = 'Detail Peminjaman Buku'

    borrow_id = fields.Many2one('library.borrow', required=True)
    book_id = fields.Many2one('library.book', required=True)
    quantity = fields.Integer('Jumlah', default=1)
    is_returned = fields.Boolean(string='Is Returned', default=False)
    fine_amount = fields.Float(string='Denda')
