# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    joint_buying_auto_subscribe = fields.Boolean(
        string="Automatic Supplier Subscription",
        compute="_compute_joint_buying_auto_subscribe",
        inverse="_inverse_joint_buying_auto_subscribe",
        help="Check this box if you want to subscribe automatically"
        " to new suppliers.",
    )

    def __init__(self, pool, cr):
        """Override of __init__ to add access rights.
        Access rights are disabled by default, but allowed on some specific
        fields defined in self.SELF_WRITEABLE_FIELDS.
        """
        super().__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(["joint_buying_auto_subscribe"])

    def _compute_joint_buying_auto_subscribe(self):
        for user in self:
            user.joint_buying_auto_subscribe = (
                user.company_id.joint_buying_auto_subscribe
            )

    def _inverse_joint_buying_auto_subscribe(self):
        for user in self:
            user.company_id.joint_buying_auto_subscribe = (
                user.joint_buying_auto_subscribe
            )
