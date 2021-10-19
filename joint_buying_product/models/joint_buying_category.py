# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingCategory(models.Model):
    _name = "joint.buying.category"
    _description = "Joint Buying Categories"
    _inherit = ["mail.thread"]

    # code = fields.Char(string="Code", required=True)

    name = fields.Char(string="Name", required=True)

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        required=True,
    )

    product_qty = fields.Integer(
        string="Products Quantity", compute="_compute_product_qty", store=True
    )

    # Compute Section
    @api.depends("supplier_id.joint_buying_product_ids.joint_buying_category_id")
    def _compute_product_qty(self):
        for category in self:
            category.product_qty = len(
                category.mapped("supplier_id.joint_buying_product_ids").filtered(
                    lambda x: x.joint_buying_category_id == category
                )
            )
