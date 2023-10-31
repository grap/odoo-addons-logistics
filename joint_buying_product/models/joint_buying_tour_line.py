# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingTourLine(models.Model):
    _inherit = "joint.buying.tour.line"

    transport_request_ids = fields.Many2many(
        comodel_name="joint.buying.transport.request",
        string="Transport Requests",
    )
