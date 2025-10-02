# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LibraryFine(models.Model):
    _name = 'library.fine'
    _description = 'LlibraryFine'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='ID Denda', readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean(default=True)
    borrow_id = fields.Many2one('library.borrow', required=True, ondelete='restrict')
    member_id = fields.Many2one(related='borrow_id.member_id', readonly=True, copy=False, store=True)
    amount_paid = fields.Float('Jumlah Dibayar', required=True)
    payment_date = fields.Date('Payment Date', default=fields.Date.today())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('library.fine.sequence') or 'New'
        return super(LibraryFine, self).create(vals)

    def action_pay(self):
        self.ensure_one()
        if self.amount_paid <= 0:
            raise UserError(_("Jumlah yang dibayar harus lebih dari 0."))

        self.write({'state': 'paid'})
        self.borrow_id.message_post(body=_("Pembayaran denda sebesar %s telah dilunasi.") % (self.amount_paid))

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancelled'})
        self.borrow_id.message_post(body=_("Denda telah dibatalkan."))
