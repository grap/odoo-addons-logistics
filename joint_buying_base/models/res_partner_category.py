# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartnerCategory(models.Model):
    _inherit = ["res.partner.category", "joint.buying.mixin"]
    _name = "res.partner.category"
