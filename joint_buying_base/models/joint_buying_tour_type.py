# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingTourType(models.Model):
    _name = "joint.buying.tour.type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Joint Buying Tour Type"
    _order = "name"

    name = fields.Char(required=True)

    tour_ids = fields.One2many(
        comodel_name="joint.buying.tour", inverse_name="carrier_id"
    )

    carrier_id = fields.Many2one(comodel_name="joint.buying.carrier")

    tour_ids = fields.One2many(comodel_name="joint.buying.tour", inverse_name="type_id")
