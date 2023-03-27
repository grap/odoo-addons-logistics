# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_joint_buying_product(self, action):
        vals = super()._prepare_joint_buying_product(action)
        vals.update(
            {
                "label_ids": [
                    (6, 0, self.label_ids.filtered(lambda x: not x.company_id).ids)
                ]
            }
        )
        return vals
