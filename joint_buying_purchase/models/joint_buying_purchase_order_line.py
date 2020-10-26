from odoo import api, fields, models

from odoo.addons import decimal_precision as dp


class JointBuyingPurchaseOrderLine(models.Model):
    _name = "joint.buying.purchase.order.line"
    _description = "Joint buying purchase order line"

    order_id = fields.Many2one(
        "joint.buying.purchase.order", string="Order", ondelete="cascade", required=True
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("is_joint_buying", "=", True)],
        ondelete="cascade",
        required=True,
    )
    quantity = fields.Float(
        string="Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )
    quantity_validation = fields.Integer(compute="_compute_quantity_validation")

    _sql_constraints = [
        ("product_id_unique", "unique(product_id)", "It's on product peer line")
    ]

    @api.onchange("quantity")
    def _compute_quantity_validation(self):
        """
        Check if the quantity of lines not exceeded the
        quantity allowed for the product or is supperior
        to minimum quantity of supplier.
        """
        if not self.product_id:
            return

        supplier_id = self.product_id.seller_ids.search(
            [("name", "=", self.order_id.supplier_id.id)]
        )
        # Critical case: If the current product have multiple
        # seller_ids with the same supplier
        quantity_allowed = supplier_id.max_qty
        minimum_quantity = supplier_id.min_qty
        if self.quantity > quantity_allowed:
            self.update({"quantity_validation": 2})
        elif self.quantity < minimum_quantity:
            self.update({"quantity_validation": 1})
        else:
            self.update({"quantity_validation": 0})
