# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'LibraryBook'
    _inherit = ['mail.thread', 'mail.render.mixin', 'mail.activity.mixin']

    name = fields.Char(string='Book Name', required=True)
    active = fields.Boolean(default=True)
    image_1920 = fields.Image('Book Image')
    isbn = fields.Char('ISBN')
    publication_year = fields.Char('Publication Year')
    stock = fields.Integer('Total Stock', tracking=True)
    remaining_stock = fields.Integer('Sisa Stock', tracking=True, compute='_compute_remaining_stock', store=True)
    borrowed_stock = fields.Integer('Terpinjam', tracking=True, compute='_compute_borrowed_stock', store=True)
    is_available = fields.Boolean('Is Available', compute='_compute_is_available', store=True)
    author_ids = fields.Many2many('library.author', string='Authors')
    genre_ids = fields.Many2many('library.genre', string='Genres')
    publisher_id = fields.Many2one('library.publisher', string='Publisher')
    category_id = fields.Many2one('library.category', string='Category')
    borrow_line_ids = fields.One2many(
        'library.borrow.lines', 'book_id', string='Borrow Lines', readonly=True
    )

    def action_open_stock_wizard(self):
        self.ensure_one()
        return {
            "name": "Update Stock Buku",
            "type": "ir.actions.act_window",
            "res_model": "library.book.stock.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_book_id": self.id},
        }

    def write(self, vals):
        res = super().write(vals)
        if "stock" in vals:
            for rec in self:
                rec.message_post(
                    body=_("📦 Stok buku diperbarui menjadi %s eksemplar.") % rec.stock
                )
        return res

    @api.depends('stock', 'borrowed_stock')
    def _compute_remaining_stock(self):
        for rec in self:
            total = rec.stock or 0
            borrowed = rec.borrowed_stock or 0
            rec.remaining_stock = total - borrowed

    @api.depends('remaining_stock')
    def _compute_is_available(self):
        for rec in self:
            rec.is_available = rec.remaining_stock > 0

    @api.depends('borrow_line_ids.borrow_id.state', 'borrow_line_ids.quantity')
    def _compute_borrowed_stock(self):
        for rec in self:
            borrowed_lines = (
                self.env["library.borrow.lines"].sudo().search([
                        ("book_id", "=", rec.id),
                        ("borrow_id.state", "=", "borrowed"),
                    ]))
            rec.borrowed_stock = sum(borrowed_lines.mapped("quantity"))
