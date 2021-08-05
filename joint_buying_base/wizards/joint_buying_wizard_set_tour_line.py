# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from ..models.res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingWizardSetTourLine(models.TransientModel):
    _name = "joint.buying.wizard.set.tour.line"
    _description = "Joint Buying Wizard Set Tour Line"
    _order = "sequence"

    sequence = fields.Integer()

    wizard_id = fields.Many2one(
        comodel_name="joint.buying.wizard.set.tour", ondelete="cascade", required=True
    )

    point_id = fields.Many2one(
        required=True,
        string="Step",
        comodel_name="res.partner",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        domain="[('is_joint_buying_stage', '=', True)]",
    )
