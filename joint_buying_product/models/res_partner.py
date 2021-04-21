# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    joint_buying_product_ids = fields.One2many(
        "product.product", inverse_name="joint_buying_partner_id"
    )

    joint_buying_product_qty = fields.Integer(
        compute="_compute_joint_buying_product_qty"
    )

    joint_buying_frequency = fields.Integer(string="Days between orders")

    joint_buying_next_date_deposit = fields.Date(string="Next Deposit Date")

    joint_buying_next_date_begin = fields.Date(string="Next Purchase Begin Date")
    joint_buying_next_date_end = fields.Datetime(string="Next Purchase End Date")

    @api.depends("joint_buying_product_ids")
    def _compute_joint_buying_product_qty(self):
        for partner in self:
            partner.joint_buying_product_qty = len(partner.joint_buying_product_ids)
