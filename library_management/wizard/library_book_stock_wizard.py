# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LibraryBookStockWizard(models.TransientModel):
    _name = 'library.book.stock.wizard'
    _description = 'Library Update Stock Book'

    book_id = fields.Many2one('library.book', 'Book', required=True)
    operation = fields.Selection([
           ('add', 'Add Stock'),
           ('remove', 'Remove Stock'),
      ], string='Tipe Operasi', default='add')
    amount = fields.Integer('Jumlah', required=True, default=1)
    note = fields.Text('Catatan', help='Catatan update stock')

    def action_confirm_update(self):
        self.ensure_one()
        book = self.book_id

        if self.amount <= 0:
            raise UserError(_('Jumlah harus lebih dari 0.'))

        if self.operation == 'add':
            book.stock += self.amount
            message = _("➕ Ditambahkan %d stok untuk buku '%s'.") % (self.amount, book.name)
        else:
            if book.stock < self.amount:
                raise UserError(_("Stok buku '%s' tidak mencukupi untuk pengurangan.") % book.name)
            book.stock -= self.amount
            message = _("➖ Dikurangi %d stok dari buku '%s'.") % (self.amount, book.name)

        book._compute_remaining_stock()
        book._compute_is_available()

        if self.note:
            message += "<br/>📝 Catatan: %s" % self.note
        book.message_post(body=message)

        return {"type": "ir.actions.act_window_close"}
