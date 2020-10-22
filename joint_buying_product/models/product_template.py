# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "joint.buying.mixin"]
    _name = "product.template"

    joint_buying_seller_ids = fields.One2many("product.supplierinfo", "product_tmpl_id")
    joint_buying_variant_seller_ids = fields.One2many(
        "product.supplierinfo", "product_tmpl_id"
    )
