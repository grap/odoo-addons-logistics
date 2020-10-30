from odoo import api, fields, models


class JointBuyingPurchaseOrder(models.Model):
    _name = "joint.buying.purchase.order"
    _description = "Joint buying purchase order"
    _rec_name = "supplier_id"

    tour_id = fields.Many2one(
        "joint.buying.tour", string="Tour", required=True, ondelete="cascade"
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer for joint buying",
        required=True,
        domain=[("is_joint_buying_customer", "=", True)],
    )

    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier for joint buying",
        required=True,
        domain=[("is_joint_buying_supplier", "=", True)],
    )

    line_ids = fields.One2many(
        "joint.buying.purchase.order.line",
        inverse_name="order_id",
        string="Lines for each customer",
    )

    pivot_activity = fields.Char(compute="_compute_get_pivot_activity")

    @api.depends("supplier_id")
    def _compute_get_pivot_activity(self):
        for rec in self:
            if rec.supplier_id.activity_id:
                rec.pivot_activity = rec.supplier_id.activity_id.name

    @api.onchange("supplier_id")
    def populate_line_ids(self):
        if self.supplier_id:
            self.update(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": supplier.product_id.id,
                                "quantity": 0.0,
                                "order_id": self.id,
                            },
                        )
                        for supplier in self.env["product.supplierinfo"].search(
                            [("name", "=", self.supplier_id.id)]
                        )
                    ]
                }
            )
