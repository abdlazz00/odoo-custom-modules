# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LibraryPublisherBook(models.Model):
    _name = 'library.publisher'
    _description = 'LibraryPublisher'

    name = fields.Char('Publisher Name', required=True)