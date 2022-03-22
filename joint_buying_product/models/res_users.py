# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    joint_buying_send_pivot_email_in_progress = fields.Boolean(
        compute="_compute_joint_buying_send_pivot_email_in_progress",
        inverse="_inverse_joint_buying_send_pivot_email_in_progress",
        string="Send email when opening Grouped Order",
    )

    joint_buying_send_pivot_email_closed = fields.Boolean(
        string="Send email when closing Grouped Order",
        compute="_compute_joint_buying_send_pivot_email_closed",
        inverse="_inverse_joint_buying_send_pivot_email_closed",
    )

    def __init__(self, pool, cr):
        """Override of __init__ to add access rights.
        Access rights are disabled by default, but allowed on some specific
        fields defined in self.SELF_WRITEABLE_FIELDS.
        """
        super().__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(
            [
                "joint_buying_send_pivot_email_in_progress",
                "joint_buying_send_pivot_email_closed",
            ]
        )

    def _compute_joint_buying_send_pivot_email_in_progress(self):
        for user in self:
            user.joint_buying_send_pivot_email_in_progress = (
                user.company_id.joint_buying_send_pivot_email_in_progress
            )

    def _inverse_joint_buying_send_pivot_email_in_progress(self):
        for user in self:
            user.company_id.joint_buying_send_pivot_email_in_progress = (
                user.joint_buying_send_pivot_email_in_progress
            )

    def _compute_joint_buying_send_pivot_email_closed(self):
        for user in self:
            user.joint_buying_send_pivot_email_closed = (
                user.company_id.joint_buying_send_pivot_email_closed
            )

    def _inverse_joint_buying_send_pivot_email_closed(self):
        for user in self:
            user.company_id.joint_buying_send_pivot_email_closed = (
                user.joint_buying_send_pivot_email_closed
            )
