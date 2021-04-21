# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    joint_buying_product_ids = fields.One2many(
        "product.product", inverse_name="joint_buying_partner_id"
    )

    joint_buying_product_qty = fields.Integer(
        compute="_compute_joint_buying_product_qty"
    )

    joint_buying_frequency = fields.Integer(string="Days between orders")

    joint_buying_next_date_start = fields.Date(string="Next Order Start Date")

    joint_buying_next_date_end = fields.Datetime(string="Next Order End Date")

    joint_buying_next_date_deposit = fields.Date(string="Next Deposit Date")

    @api.constrains(
        "joint_buying_frequency",
        "joint_buying_next_date_deposit",
        "joint_buying_next_date_start",
        "joint_buying_next_date_end",
    )
    def _check_joint_buying_correct_date(self):
        if not self.joint_buying_frequency:
            return
        if (
            not self.joint_buying_next_date_start
            or not self.joint_buying_next_date_end
            or not self.joint_buying_next_date_deposit
        ):
            raise ValidationError(
                _("You should define Start, End and deposit Date for recurring orders.")
            )
        elif (
            datetime.combine(self.joint_buying_next_date_start, time(0, 0))
            < self.joint_buying_next_date_end
        ):
            raise ValidationError(_("the start date must be less than the end date"))
        elif (
            datetime.combine(self.joint_buying_next_date_end, time(0, 0))
            < self.joint_buying_next_date_deposit
        ):
            raise ValidationError(_("the end date must be less than the deposit date"))

    @api.depends("joint_buying_product_ids")
    def _compute_joint_buying_product_qty(self):
        for partner in self:
            partner.joint_buying_product_qty = len(partner.joint_buying_product_ids)
