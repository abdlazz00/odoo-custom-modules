# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class LibraryFineAdjustment(models.Model):
    _name = "library.fine.adjustment"
    _description = "Penyesuaian Denda"

    name = fields.Char(string="ID Fine Adjustment", readonly=True, required=True, copy=False, default="New")
    borrow_id = fields.Many2one("library.borrow", string="Peminjaman", required=True, ondelete="restrict")
    member_id = fields.Many2one('res.partner', 'Member', related='borrow_id.member_id', readonly=True, copy=False, store=True)
    borrow_date = fields.Date('Borrow Date', related='borrow_id.borrow_date', readonly=True, copy=False, store=True)
    return_due_date = fields.Date('Return Due Date', related='borrow_id.return_due_date', readonly=True, copy=False, store=True)
    current_fine = fields.Float('Current Fine', related='borrow_id.total_fine', readonly=True)
    adjustment_date = fields.Date(string="Adjustment Date", required=True, default=fields.Date.today())
    reason = fields.Text(string="Alasan", required=True)
    adjusted_fine = fields.Float(string="Adjust To", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Disetujui"),
        ],string="Status", default="draft",)

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("library.fine.adjustment.sequence")or "New")
        return super(LibraryFineAdjustment, self).create(vals)

    def action_apply_adjustment(self):
        for rec in self:
            if rec.borrow_id:
                borrow = rec.borrow_id
                before = borrow.total_fine
                after = rec.adjusted_fine

                borrow.write({'total_fine': after})
                rec.state = "approved"
                borrow.message_post(
                    body=_(
                        "💰 Penyesuaian denda: dari Rp %s menjadi Rp %s.<br/>Alasan: %s"
                    ) % (before, after, rec.reason)
                )
                self.message_post(
                    body=_("Penyesuaian denda disetujui untuk peminjaman %s.") % borrow.name
                )
