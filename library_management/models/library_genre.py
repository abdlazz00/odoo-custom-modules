# -*- coding: utf-8 -*-
from odoo import api, fields, models

class LibraryGenre(models.Model):
    _name = 'library.genre'
    _description = 'LibraryGenre'

    name = fields.Char('Genre Name', required=True)