# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = ["product.product", "joint.buying.mixin"]
    _name = "product.product"

    is_joint_buying = fields.Boolean(
        string="For Joint Buying",
        related="product_tmpl_id.is_joint_buying",
        store=True,
        readonly=True,
    )

    joint_buying_partner_id = fields.Many2one(
        string="Joint Buying Supplier",
        comodel_name="res.partner",
        related="product_tmpl_id.joint_buying_partner_id",
        store=True,
        readonly=False,
    )

    # joint_buying_product_id = fields.Many2one(
    #     string="Joint Buying Product",
    #     comodel_name="product.product")
