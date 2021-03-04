from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    tour_template_id = fields.Many2one(
        "joint.buying.tour.template", string="Tour template"
    )
    supplier_order_ids = fields.One2many(
        "joint.buying.purchase.order", inverse_name="supplier_id"
    )
    customer_order_ids = fields.One2many(
        "joint.buying.purchase.order", inverse_name="customer_id"
    )

    total_supplier_orders = fields.Integer(
        compute="_compute_total_supplier_orders", store=True
    )
    total_customer_orders = fields.Integer(
        compute="_compute_total_customer_orders", store=True
    )

    @api.depends("supplier_order_ids")
    def _compute_total_supplier_orders(self):
        for rec in self:
            rec.total_supplier_orders = len(rec.supplier_order_ids)

    @api.depends("supplier_order_ids")
    def _compute_total_customer_orders(self):
        for rec in self:
            rec.total_customer_orders = len(rec.customer_order_ids)

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        is_activity_key = self.env.context.get("is_activity_key", False)
        if is_activity_key:
            current_partner_id = (
                self.env["res.users"]
                .with_context({"joint_buying": "1"})
                .browse(self.env.context["uid"])
                .partner_id
            )
            args += [("activity_id", "=", current_partner_id.id)]
        return super()._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
