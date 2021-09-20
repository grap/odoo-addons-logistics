# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    joint_buying_send_pivot_email_in_progress = fields.Boolean(
        string="Send email when opening Grouped Order",
        related="company_id.joint_buying_send_pivot_email_in_progress",
    )

    joint_buying_send_pivot_email_closed = fields.Boolean(
        string="Send email when closing Grouped Order",
        related="company_id.joint_buying_send_pivot_email_closed",
    )
