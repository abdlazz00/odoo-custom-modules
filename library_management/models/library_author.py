# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LibraryAuthorBook(models.Model):
    _name = 'library.author'
    _description = 'LibraryAuthor'

    name = fields.Char('Author Name', required=True)
