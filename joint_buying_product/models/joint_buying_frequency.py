# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingFrequency(models.Model):
    _name = "joint.buying.frequency"
    _description = "Joint Buying Frequencies"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        required=True,
        ondelete="cascade",
    )

    frequency = fields.Integer(string="Frequency (Days)", required=True)

    next_start_date = fields.Datetime(string="Next Start Date", required=True)

    next_end_date = fields.Datetime(string="Next End Date", required=True)

    next_deposit_date = fields.Datetime(string="Next Deposit Date", required=True)

    deposit_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Deposit Place",
        help="Place that will serve as a deposit for this supplier",
        required=True,
        domain="[('is_joint_buying_stage', '=', True)]",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    minimum_amount = fields.Float(string="Minimum Amount For Grouped Order")

    minimum_weight = fields.Float(string="Minimum Weight For Grouped Order")

    minimum_unit_amount = fields.Float(string="Minimum Amount For Unit Order")

    minimum_unit_weight = fields.Float(string="Minimum Weight For Unit Order")

    category_ids = fields.Many2many(
        string="Categories",
        comodel_name="joint.buying.category",
        domain="[('supplier_id', '=', parent.id)]",
    )

    # constrains Section
    @api.constrains(
        "frequency", "next_start_date", "next_end_date", "next_deposit_date"
    )
    def _check_correct_date(self):
        if self.frequency % 7:
            raise ValidationError(_("Frequency should be a multiple of 7."))
        elif datetime.combine(self.next_start_date, time(0, 0)) >= self.next_end_date:
            raise ValidationError(_("The start date must be less than the end date."))
        elif self.next_end_date >= datetime.combine(self.next_deposit_date, time(0, 0)):
            raise ValidationError(_("The end date must be less than the deposit date."))
