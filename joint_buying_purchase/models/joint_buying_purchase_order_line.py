from odoo import fields, models
from odoo.addons import decimal_precision as dp


class JointBuyingPurchaseOrderLine(models.Model):
    _name = "joint.buying.purchase.order.line"
    _description = "Joint buying purchase order line"

    order_id = fields.Many2one(
        "joint.buying.purchase.order",
        string="Order",
        ondelete='cascade',
        required=True
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("is_joint_buying", "=", True)],
        ondelete='cascade',
        required=True
    )
    quantity = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True
    )
