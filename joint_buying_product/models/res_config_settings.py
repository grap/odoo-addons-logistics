# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    end_date_near_day = fields.Integer(
        string="Number of Day 'Near'",
        required=True,
        config_parameter="joint_buying_product.end_date_near_day",
        help="Number of days below which the end of the order is near.",
    )

    end_date_imminent_day = fields.Integer(
        string="Number of Day 'Imminent'",
        required=True,
        config_parameter="joint_buying_product.end_date_imminent_day",
        help="Number of days below which the end of the order is imminent.",
    )

    new_product_day = fields.Integer(
        string="Number of Day 'Product new'",
        required=True,
        config_parameter="joint_buying_product.new_product_day",
        help="Number of days after which a product will no longer be marked as new.",
    )
