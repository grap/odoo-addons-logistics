# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    joint_buying_commission_product_id = fields.Many2one(
        comodel_name="product.product",
        name="Joint Buying Commission Product",
        related="company_id.joint_buying_commission_product_id",
        readonly=False,
    )
