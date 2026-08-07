# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    joint_buying_end_date_near_day = fields.Integer(
        string="Number of Day 'Near'",
        required=True,
        config_parameter="joint_buying_product.end_date_near_day",
        help="Number of days below which the end of the order is near.",
    )

    joint_buying_end_date_imminent_day = fields.Integer(
        string="Number of Day 'Imminent'",
        required=True,
        config_parameter="joint_buying_product.end_date_imminent_day",
        help="Number of days below which the end of the order is imminent.",
    )

    joint_buying_new_product_day = fields.Integer(
        string="Number of Day 'Product new'",
        required=True,
        config_parameter="joint_buying_product.new_product_day",
        help="Number of days after which a product will no longer be marked as new.",
    )

    joint_buying_send_pivot_email_in_progress = fields.Boolean(
        string="Send email when opening Grouped Order",
        related="company_id.joint_buying_send_pivot_email_in_progress",
        readonly=False,
    )

    joint_buying_send_pivot_email_closed = fields.Boolean(
        string="Send email when closing Grouped Order",
        related="company_id.joint_buying_send_pivot_email_closed",
        readonly=False,
    )

    joint_buying_pricelist_id = fields.Many2one(
        string="Joint Buying Pricelist",
        comodel_name="product.pricelist",
        related="company_id.joint_buying_pricelist_id",
        readonly=False,
    )
