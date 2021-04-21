from datetime import timedelta

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

    joint_buying_next_date_availability = fields.Date(string="Next Availability Date")

    joint_buying_delay_begin = fields.Integer(string="Delay before Purchase Begin")

    joint_buying_delay_end = fields.Integer(string="Delay before Purchase End")

    joint_buying_next_date_begin = fields.Date(
        string="Next Purchase Begin Date",
        compute="_compute_next_date_begin",
        store=True,
    )
    joint_buying_next_date_end = fields.Date(
        string="Next Purchase End Date", compute="_compute_next_date_end", store=True
    )

    @api.depends("joint_buying_next_date_availability", "joint_buying_delay_begin")
    def _compute_next_date_begin(self):
        for partner in self.filtered(lambda x: x.joint_buying_next_date_availability):
            partner.joint_buying_next_date_begin = (
                partner.joint_buying_next_date_availability
                + timedelta(days=-partner.joint_buying_delay_begin)
            )

    @api.depends("joint_buying_next_date_availability", "joint_buying_delay_end")
    def _compute_next_date_end(self):
        for partner in self.filtered(lambda x: x.joint_buying_next_date_availability):
            partner.joint_buying_next_date_end = (
                partner.joint_buying_next_date_availability
                + timedelta(days=-partner.joint_buying_delay_end)
            )

    @api.depends("joint_buying_product_ids")
    def _compute_joint_buying_product_qty(self):
        for partner in self:
            partner.joint_buying_product_qty = len(partner.joint_buying_product_ids)
