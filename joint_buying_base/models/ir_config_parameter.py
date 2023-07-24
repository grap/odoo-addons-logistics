# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        joint_buying_config = self.search(
            [("key", "=", "joint_buying_base.group_name")]
        )
        if joint_buying_config:
            if joint_buying_config[0].id in self.ids:
                ResCompany = self.env["res.company"].with_context(active_test=False)
                ResCompany.search([]).update_joint_buying_partners()
        return res
