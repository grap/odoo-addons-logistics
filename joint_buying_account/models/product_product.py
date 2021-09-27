# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_joint_buying_product(self):
        vals = super()._prepare_joint_buying_product()

        taxes = self.taxes_id

        price = self.env["account.tax"]._fix_tax_included_price(self.lst_price, taxes)

        # TODO
        price = price
        return vals
