from odoo import api, fields, models


class JointBuyingTour(models.Model):
    _name = "joint.buying.tour"
    _description = "Joint buying tour"
    _rec_name = "date"

    date = fields.Date(primary=True, required=True)
    tour_template_id = fields.Many2one(
        "joint.buying.tour.template", required=True, ondelete="set null"
    )
    joint_buying_purchase_ids = fields.One2many(
        "joint.buying.purchase.order",
        inverse_name="tour_id",
        string="Joint buying purchase orders peer supplier",
    )
    generate = fields.Boolean(default=False)

    total_orders = fields.Integer(compute="_compute_total_orders", store=True)

    @api.depends("joint_buying_purchase_ids")
    def _compute_total_orders(self):
        for rec in self:
            rec.total_orders = len(rec.joint_buying_purchase_ids)
