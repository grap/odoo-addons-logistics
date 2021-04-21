# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingWizardCreateOrderLine(models.TransientModel):
    _name = "joint.buying.wizard.create.order.line"
    _description = "Joint Buying Wizard Create Order Line"

    wizard_id = fields.Many2one(comodel_name="joint.buying.wizard.create.order")

    partner_id = fields.Many2one(
        required=True,
        string="Customer",
        comodel_name="res.partner",
        domain="[('is_joint_buying', '=', True), ('customer', '=', True)]",
    )
