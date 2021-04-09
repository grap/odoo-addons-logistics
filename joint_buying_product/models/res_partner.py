from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    joint_buying_product_ids = fields.One2many(
        "product.product", inverse_name="joint_buying_partner_id"
    )

    joint_buying_product_qty = fields.Integer(
        compute="_compute_joint_buying_product_qty"
    )

    @api.depends("joint_buying_product_ids")
    def _compute_joint_buying_product_qty(self):
        for partner in self:
            partner.joint_buying_product_qty = len(partner.joint_buying_product_ids)
