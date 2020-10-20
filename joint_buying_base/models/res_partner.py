# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = ["res.partner", "joint.buying.mixin"]
    _name = "res.partner"

    is_joint_buying_customer = fields.Boolean(
        default=False, string="Is a customer for joint buying"
    )
    is_joint_buying_supplier = fields.Boolean(
        default=False, string="Is a supplier for joint buying"
    )
