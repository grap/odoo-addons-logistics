from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    vendor_ids = fields.One2many("product.supplierinfo", inverse_name="name")

    total_joint_buying_product = fields.Integer(
        compute="_compute_total_joint_buying_product"
    )

    @api.depends("vendor_ids")
    def _compute_total_joint_buying_product(self):
        for rec in self:
            rec.total_joint_buying_product = len(rec.vendor_ids)
