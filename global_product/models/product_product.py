# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = ["product.product", "global.mixin"]
    _name = "product.product"

    is_global = fields.Boolean(
        compute=False, related="product_tmpl_id.is_global", store=True
    )
