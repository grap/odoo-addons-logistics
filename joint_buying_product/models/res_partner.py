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

    joint_buying_grouped_order_ids = fields.One2many(
        "joint.buying.purchase.order.grouped", inverse_name="supplier_id"
    )

    joint_buying_grouped_order_qty = fields.Integer(
        compute="_compute_joint_buying_grouped_order_qty"
    )

    joint_buying_minimum_amount = fields.Float(
        string="Minimum Amount For Grouped Order"
    )

    joint_buying_minimum_unit_amount = fields.Float(
        string="Minimum Amount For Unit Order"
    )

    joint_buying_minimum_weight = fields.Float(
        string="Minimum Weight For Grouped Order"
    )

    joint_buying_minimum_unit_weight = fields.Float(
        string="Minimum Weight For Unit Order"
    )

    joint_buying_frequency = fields.Integer(string="Days between orders")

    joint_buying_next_start_date = fields.Datetime(string="Next Order Start Date")

    joint_buying_next_end_date = fields.Datetime(string="Next Order End Date")

    joint_buying_next_deposit_date = fields.Datetime(string="Next Deposit Date")

    joint_buying_category_ids = fields.One2many(
        string="Joint Buying Categories",
        comodel_name="joint.buying.category",
        inverse_name="supplier_id",
    )

    joint_buying_use_category = fields.Boolean(
        string="Use Order Categories", default=False
    )

    # constrains Section
    @api.constrains(
        "joint_buying_frequency",
        "joint_buying_next_start_date",
        "joint_buying_next_end_date",
        "joint_buying_next_deposit_date",
    )
    def _check_joint_buying_correct_date(self):
        if not self.joint_buying_frequency:
            return
        if self.joint_buying_frequency % 7:
            raise ValidationError(_("Frequency should be a multiple of 7."))
        if (
            not self.joint_buying_next_start_date
            or not self.joint_buying_next_end_date
            or not self.joint_buying_next_deposit_date
        ):
            raise ValidationError(
                _("You should define Start, End and deposit Date for recurring orders.")
            )
        elif (
            datetime.combine(self.joint_buying_next_start_date, time(0, 0))
            >= self.joint_buying_next_end_date
        ):
            raise ValidationError(_("The start date must be less than the end date."))
        elif self.joint_buying_next_end_date >= datetime.combine(
            self.joint_buying_next_deposit_date, time(0, 0)
        ):
            raise ValidationError(_("The end date must be less than the deposit date."))

    # Compute Section
    @api.depends("joint_buying_product_ids")
    def _compute_joint_buying_product_qty(self):
        for partner in self:
            partner.joint_buying_product_qty = len(partner.joint_buying_product_ids)

    @api.depends("joint_buying_grouped_order_ids")
    def _compute_joint_buying_grouped_order_qty(self):
        for partner in self:
            partner.joint_buying_grouped_order_qty = len(
                partner.joint_buying_grouped_order_ids
            )

    # Custom Section
    def _get_joint_buying_products(self, categories):
        self.ensure_one()
        return self.with_context(joint_buying=1).joint_buying_product_ids.filtered(
            lambda x: x.purchase_ok
            and x.active
            and (
                x.joint_buying_category_id.id in categories.ids
                or not x.joint_buying_category_id
            )
        )
