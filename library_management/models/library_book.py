# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'LibraryBook'
    _inherit = ['mail.thread', 'mail.render.mixin', 'mail.activity.mixin']

    name = fields.Char(string='Book Name', required=True)
    active = fields.Boolean(default=True)
    image_1920 = fields.Image('Book Image')
    isbn = fields.Char('ISBN')
    publication_year = fields.Char('Publication Year')
    stock = fields.Integer('Stock')
    is_available = fields.Boolean('Is Available', compute='_compute_is_available', store=True)
    author_ids = fields.Many2many('library.author', string='Authors')
    genre_ids = fields.Many2many('library.genre', string='Genres')
    publisher_id = fields.Many2one('library.publisher', string='Publisher')
    category_id = fields.Many2one('library.category', string='Category')

    @api.depends('stock')
    def _compute_is_available(self):
        for rec in self:
            rec.is_available = rec.stock > 0