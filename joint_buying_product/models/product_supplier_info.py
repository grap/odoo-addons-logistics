# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    joint_buying_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="name.joint_buying_partner_id",
        store=True,
    )

    joint_buying_product_id = fields.Many2one(
        comodel_name="product.product",
        domain="[('joint_buying_partner_id', '=', joint_buying_partner_id)]")
