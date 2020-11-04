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
    total_quantity = fields.Float(
        compute="_compute_total_quantity",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    min_quantity = fields.Float(
        compute="_compute_min_quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        store=True,
    )
    max_quantity = fields.Float(
        compute="_compute_max_quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        store=True,
    )
    quantity_validation = fields.Float(
        compute="_compute_quantity_validation",
        digits=dp.get_precision("Product Unit of Measure"),
        invisible=True,
    )
    total_price = fields.Float(compute="_compute_total_price")

    @api.depends("product_id")
    def _compute_min_quantity(self):
        for rec in self:
            supplier_id = rec.product_id.seller_ids.search(
                [("name", "=", rec.order_id.supplier_id.id)]
            )
            rec.min_quantity = supplier_id.min_qty

    @api.depends("product_id")
    def _compute_max_quantity(self):
        for rec in self:
            supplier_id = rec.product_id.seller_ids.search(
                [("name", "=", rec.order_id.supplier_id.id)]
            )
            rec.max_quantity = supplier_id.max_qty

    @api.depends("quantity")
    def _compute_total_quantity(self):
        for rec in self:
            rec.total_quantity = sum(
                line.quantity
                for order in rec.order_id.tour_id.joint_buying_purchase_ids.search(
                    [("supplier_id", "=", rec.order_id.supplier_id.id)]
                )
                for line in order.line_ids.search(
                    [
                        ("product_id", "=", rec.product_id.id),
                        ("order_id", "=", order.id),
                    ]
                )
            )

    @api.depends("quantity")
    def _compute_total_price(self):
        for rec in self:
            supplier_id = rec.product_id.seller_ids.search(
                [("name", "=", rec.order_id.supplier_id.id)]
            )
            rec.total_price = supplier_id.price * rec.quantity

    @api.depends("quantity")
    def _compute_quantity_validation(self):
        """
        Check if the quantity of lines not exceeded the
        quantity allowed for the product or is supperior
        to minimum quantity of supplier.
        """
        for rec in self:
            if rec.total_quantity > rec.max_quantity:
                rec.quantity_validation = 2
            elif rec.total_quantity < rec.min_quantity:
                rec.quantity_validation = 1
            else:
                rec.quantity_validation = 0
