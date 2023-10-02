# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingCarrier(models.Model):
    _name = "joint.buying.carrier"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Joint Buying Carrier"
    _order = "name"

    name = fields.Char(required=True)

    is_provider = fields.Boolean(string="Is a Provider", default=False)

    tour_ids = fields.One2many(
        comodel_name="joint.buying.tour", inverse_name="carrier_id"
    )

    payload = fields.Integer()

    hourly_cost = fields.Monetary(currency_field="currency_id")

    kilometer_cost = fields.Monetary(currency_field="currency_id")

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        default=lambda x: x._default_currency_id(),
    )

    def _default_currency_id(self):
        return self.env.ref("base.EUR")
