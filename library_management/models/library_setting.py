# -*- coding: utf-8 -*-
from odoo import api, fields, models


class LibrarySetting(models.TransientModel):
    _inherit = 'res.config.settings'

    daily_fine_amount = fields.Float('Fine Amount', config_parameter='library_management.daily_fine_amount', default=1000.0)