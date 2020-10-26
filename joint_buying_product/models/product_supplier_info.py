# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    max_qty = fields.Float(
        "Maximal Quantity",
        default=0.0,
        required=True,
        help=(
            "The maximal quantity to purchase from this vendor, "
            "expressed in the vendor Product Unit of Measure if not any, "
            "in the default unit of measure of the product otherwise."
        ),
    )
