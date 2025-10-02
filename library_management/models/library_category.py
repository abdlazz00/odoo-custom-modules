# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'LibraryCategory'

    name = fields.Char('Category Name', required=True)