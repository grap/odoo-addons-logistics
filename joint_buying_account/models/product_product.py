# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_joint_buying_product(self, action):
        res = super()._prepare_joint_buying_product(action)
        taxes = self.taxes_id.compute_all(res["lst_price"], False, 1, product=self)
        res["lst_price"] = taxes["total_excluded"]
        return res
