# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class JointBuyingPurchaseOrderLine(models.Model):
    _inherit = "joint.buying.purchase.order.line"

    local_product_qty_description = fields.Char(
        string="Local Quantity",
        comodel_name="product.product",
        compute="_compute_local_product_id",
    )

    @api.depends("product_id")
    def _compute_local_product_id(self):
        super()._compute_local_product_id()
        for line in self.filtered(lambda x: not x.local_product_id):
            line.local_product_qty_description = ""

        for line in self.filtered(lambda x: x.local_product_id):
            qty_available = line.local_product_id.qty_available
            qty_virtual_available = line.local_product_id.virtual_available
            if qty_available == qty_virtual_available:
                line.local_product_qty_description = "(%s %s)" % (
                    qty_available,
                    line.local_product_id.uom_name,
                )
            else:
                line.local_product_qty_description = "(%s %s / %s %s)" % (
                    qty_available,
                    line.local_product_id.uom_name,
                    qty_virtual_available,
                    line.local_product_id.uom_name,
                )
