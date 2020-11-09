from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import Warning


class JointBuyingTourTemplate(models.Model):
    _name = "joint.buying.tour.template"
    _description = "Joint buying tour template"

    name = fields.Char(string="Name of tour template")
    step_ids = fields.One2many(
        "res.partner",
        inverse_name="tour_template_id",
        string="These activities can be steps for this touring template",
        domain=[("is_joint_buying", "=", True)],
    )
    tour_ids = fields.One2many(
        "joint.buying.tour", inverse_name="tour_template_id", order="date"
    )
    deadline = fields.Integer(
        default=0, string="Tours creation time before departure.", required=True
    )
    period = fields.Integer(
        default=0, string="Period between each tour.", required=True
    )
    init_period_date = fields.Date(
        string="Initial date to start the periods between each tour.", required=True
    )

    total_step_suppliers = fields.Integer(
        compute="_compute_total_step_suppliers", store=True
    )
    total_tours = fields.Integer(compute="_compute_total_tours", store=True)

    @api.depends("step_ids")
    def _compute_total_step_suppliers(self):
        for rec in self:
            rec.total_step_suppliers = len(rec.step_ids)

    @api.depends("tour_ids")
    def _compute_total_tours(self):
        for rec in self:
            rec.total_tours = len(rec.tour_ids)

    def _generate_tour_ids_data(
        self, today, date, index, customer_ids, supplier_ids, tour_data
    ):
        filter_supplier_ids = [
            supplier
            for supplier in supplier_ids
            # Index corresponds to the number of already existing periods.
            # Here, we make a multiplication of the period with the index.
            # With the index, we can synchronise the progress of tour dates
            # and producer orders dates.
            if supplier.init_period_date + timedelta(days=(supplier.period * index))
            == date
        ]
        tour_data["tour_ids"].append(
            (
                0,
                0,
                {
                    "date": date,
                    "generate": True,
                    "joint_buying_purchase_ids": [
                        (
                            0,
                            0,
                            {
                                "customer_id": customer_id.id,
                                "supplier_id": supplier_id.id,
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
                                    for supplier in self.env[
                                        "product.supplierinfo"
                                    ].search([("name", "=", supplier_id.id)])
                                ],
                            },
                        )
                        for customer_id in customer_ids
                        for supplier_id in filter_supplier_ids
                    ],
                },
            )
        )
        date = date + timedelta(days=self.period)
        if today >= (date - timedelta(days=self.deadline)):
            index += 1
            self._generate_tour_ids_data(
                today, date, index, customer_ids, supplier_ids, tour_data
            )

    @api.multi
    def generate_tour(self):
        for rec in self:
            today = datetime.today().date()
            if not rec.tour_ids:
                date = rec.init_period_date
                index = 0
            else:
                date = rec.tour_ids.search(
                    [("tour_template_id", "=", rec.id), ("generate", "=", True)]
                )[-1].date + timedelta(days=rec.period)
                index = len(rec.tour_ids)

            tour_data = {"tour_ids": []}
            customer_ids = (
                self.env["res.partner"]
                .with_context({"joint_buying": "1"})
                .search([("is_joint_buying_customer", "=", True)])
            )
            supplier_ids = (
                self.env["res.partner"]
                .with_context({"joint_buying": "1"})
                .search([("is_joint_buying_supplier", "=", True)])
            )
            if today >= date - timedelta(days=rec.deadline):
                rec._generate_tour_ids_data(
                    today, date, index, customer_ids, supplier_ids, tour_data
                )
                rec.update(tour_data)
            else:
                raise Warning(
                    f"The next tour is planned in : "
                    f"{-(today - (date - timedelta(days=rec.deadline))).days} "
                    "days"
                )
