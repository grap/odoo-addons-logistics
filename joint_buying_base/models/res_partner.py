# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = ["res.partner", "joint.buying.mixin"]
    _name = "res.partner"

    is_joint_buying_customer = fields.Boolean(
        default=False, string="Is a customer for joint buying"
    )
    is_joint_buying_supplier = fields.Boolean(
        default=False, string="Is a supplier for joint buying"
    )

    # Supplier
    activity_id = fields.Many2one(
        "res.partner",
        string="Activity key",
        domain=[
            ("is_joint_buying", "=", True),
            ("is_joint_buying_supplier", "=", True),
        ],
    )
    delay = fields.Integer(
        default=0, string="Timeframes for preparations before order."
    )
    period = fields.Integer(default=0, string="Period between each order")
    init_period_date = fields.Date(
        string="Initial date to start the periods between each order."
    )

    # Customer
    supplier_ids = fields.One2many(
        "res.partner",
        inverse_name="activity_id",
        string=("Suppliers to manage"),
        domain=[
            ("is_joint_buying", "=", True),
            ("is_joint_buying_supplier", "=", True),
        ],
    )
