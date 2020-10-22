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
        string="The activity that manages my stocks",
        domain=[
            ("is_joint_buying", "=", True),
            ("is_joint_buying_supplier", "=", True),
        ],
    )

    # Customer
    supplier_ids = fields.One2many(
        "res.partner",
        inverse_name="activity_id",
        strings=(
            "Suppliers to manage, if there are one or more company,"
            " then this is a pivot activity"
        ),
        domain=[
            ("is_joint_buying", "=", True),
            ("is_joint_buying_supplier", "=", True),
        ],
    )
