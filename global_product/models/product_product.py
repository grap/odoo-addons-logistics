# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PrductProduct(models.Model):
    _inherit = "product.product"

    is_global_product = fields.Boolean(
        compute="_compute_is_global_product", string="Is Global Product", store=True
    )

    @api.depends("company_id")
    def _compute_is_global_product(self):
        for product in self:
            product.is_global_product = product.company_id is False
