# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    joint_buying_auto_favorite = fields.Boolean(
        related="company_id.joint_buying_auto_favorite", string="Automatic Bookmarking"
    )
