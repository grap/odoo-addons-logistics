# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons import decimal_precision as dp


class JointBuyingPurchaseOrderGroupedLine(models.TransientModel):
    _name = "joint.buying.purchase.order.grouped.line"
    _description = "Joint Buying Grouped Purchase Order Grouped Line"
    _order = "product_id"

    product_id = fields.Many2one(comodel_name="product.product")

    product_uom_package_id = fields.Many2one(comodel_name="uom.uom")

    product_uom_package_qty = fields.Float(
        digits=dp.get_precision("Product Unit of Measure")
    )

    product_uom_qty = fields.Float(digits=dp.get_precision("Product Unit of Measure"))

    product_uom_id = fields.Many2one(comodel_name="uom.uom")

    price_unit = fields.Float(digits=dp.get_precision("Product Price"))

    amount_untaxed = fields.Float(digits=dp.get_precision("Product Price"))

    total_weight = fields.Float(digits=dp.get_precision("Product Price"))
