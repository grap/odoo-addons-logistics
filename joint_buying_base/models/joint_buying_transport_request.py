# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import _, api, fields, models

from odoo.addons import decimal_precision as dp

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingTransportRequest(models.Model):
    _name = "joint.buying.transport.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Joint Buying Transport Request"
    _order = "availability_date desc, supplier_id"

    _INVALIDATE_VALS = {
        "start_date": False,
        "arrival_date": False,
        "state": "to_compute",
        "line_ids": [(5,)],
    }

    _INVALIDATE_FIELDS = [
        "manual_availability_date",
        "manual_start_partner_id",
        "manual_arrival_partner_id",
    ]

    name = fields.Char(compute="_compute_name", store=True)

    request_type = fields.Selection(
        selection=[("manual", "Manual")],
        compute="_compute_request_type",
        store=True,
    )

    origin = fields.Char(compute="_compute_origin", store=True)

    state = fields.Selection(
        selection=[
            ("to_compute", "To Compute"),
            ("computed", "Computed"),
            ("not_computable", "Not Computable"),
        ],
        required=True,
        readonly=True,
        default="to_compute",
        track_visibility=True,
    )

    manual_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        compute="_compute_supplier_id",
        store=True,
        track_visibility=True,
    )

    manual_availability_date = fields.Datetime(string="Availability Date (Manual)")

    availability_date = fields.Datetime(
        string="Availability Date",
        compute="_compute_availability_date",
        store=True,
        track_visibility=True,
    )

    manual_start_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Start Partner (Manual)",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        domain="[('is_joint_buying_stage', '=', True)]",
    )

    start_partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_start_partner_id",
        string="Start Partner",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        track_visibility=True,
    )

    manual_arrival_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Arrival Partner (Manual)",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        domain="[('is_joint_buying_stage', '=', True)]",
    )

    arrival_partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_arrival_partner_id",
        string="Arrival Partner",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        track_visibility=True,
    )

    manual_amount_untaxed = fields.Float(
        string="Untaxed Amount (Manual)",
        digits=dp.get_precision("Product Price"),
    )

    amount_untaxed = fields.Float(
        string="Untaxed Amount",
        compute="_compute_amount_untaxed",
        store=True,
        digits=dp.get_precision("Product Price"),
        track_visibility=True,
    )

    manual_total_weight = fields.Float(
        string="Weight (Manual)",
        digits=dp.get_precision("Stock Weight"),
    )

    total_weight = fields.Float(
        string="Weight",
        compute="_compute_total_weight",
        store=True,
        digits=dp.get_precision("Stock Weight"),
        compute_sudo=True,
        track_visibility=True,
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.transport.request.line",
        string="Transport Lines",
        inverse_name="request_id",
        readonly=True,
    )

    start_date = fields.Datetime(string="Start Date", readonly=True)

    arrival_date = fields.Datetime(string="Arrival Date", readonly=True)

    manual_description = fields.Html()

    description = fields.Html(compute="_compute_description")

    can_change_date = fields.Boolean(compute="_compute_can_change")

    can_change_extra_data = fields.Boolean(compute="_compute_can_change")

    can_change_partners = fields.Boolean(compute="_compute_can_change")

    tour_qty = fields.Integer(compute="_compute_tour_qty")

    def write(self, vals):
        if "state" not in vals.keys() and set(vals.keys()).intersection(
            self._INVALIDATE_FIELDS
        ):
            vals.update(self._INVALIDATE_VALS)
        return super().write(vals)

    def _get_depends_request_type(self):
        return ["state"]  # fake, to make dependency working

    def _get_depends_can_change(self):
        return ["state"]  # fake, to make dependency working

    def _get_depends_origin(self):
        return ["state"]  # fake, to make dependency working

    def _get_depends_supplier_id(self):
        return ["manual_supplier_id"]

    def _get_depends_availability_date(self):
        return ["manual_availability_date"]

    def _get_depends_start_partner_id(self):
        return ["manual_start_partner_id"]

    def _get_depends_arrival_partner_id(self):
        return ["manual_arrival_partner_id"]

    def _get_depends_amount_untaxed(self):
        return ["manual_amount_untaxed"]

    def _get_depends_total_weight(self):
        return ["manual_total_weight"]

    def _get_depends_description(self):
        return ["manual_description"]

    @api.depends("start_partner_id", "arrival_partner_id", "availability_date")
    def _compute_name(self):
        for request in self:
            request.name = (
                f"{request.start_partner_id.joint_buying_code}"
                f" -> {request.arrival_partner_id.joint_buying_code}"
                f" ({request.availability_date})"
            )

    @api.depends("line_ids.tour_line_id.tour_id")
    def _compute_tour_qty(self):
        for request in self:
            request.tour_qty = len(request.mapped("line_ids.tour_line_id.tour_id"))

    @api.depends(lambda x: x._get_depends_origin())
    def _compute_origin(self):
        for request in self:
            request.origin = _("Manual")

    @api.depends(lambda x: x._get_depends_request_type())
    def _compute_request_type(self):
        for request in self:
            request.request_type = "manual"

    @api.depends(lambda x: x._get_depends_supplier_id())
    def _compute_supplier_id(self):
        for request in self:
            request.supplier_id = request.manual_supplier_id

    @api.depends(lambda x: x._get_depends_availability_date())
    def _compute_availability_date(self):
        for request in self:
            request.availability_date = request.manual_availability_date

    @api.depends(lambda x: x._get_depends_start_partner_id())
    def _compute_start_partner_id(self):
        for request in self:
            request.start_partner_id = request.manual_start_partner_id

    @api.depends(lambda x: x._get_depends_arrival_partner_id())
    def _compute_arrival_partner_id(self):
        for request in self:
            request.arrival_partner_id = request.manual_arrival_partner_id

    @api.depends(lambda x: x._get_depends_amount_untaxed())
    def _compute_amount_untaxed(self):
        for request in self:
            request.amount_untaxed = request.manual_amount_untaxed

    @api.depends(lambda x: x._get_depends_total_weight())
    def _compute_total_weight(self):
        for request in self:
            request.total_weight = request.manual_total_weight

    @api.depends(lambda x: x._get_depends_description())
    def _compute_description(self):
        for request in self:
            request.description = request.manual_description

    @api.depends(lambda x: x._get_depends_can_change())
    def _compute_can_change(self):
        for request in self:
            request.can_change_date = True
            request.can_change_extra_data = True
            request.can_change_partners = True

    def _set_tour_lines(self, tour_lines):
        self.ensure_one()
        # If lines are valid
        if tour_lines and tour_lines[-1].arrival_point_id == self.arrival_partner_id:
            line_vals = []
            previous_tour_id = False
            for i, tour_line in enumerate(tour_lines):
                # Compute if it is a loading at the beginning of the tour line
                if previous_tour_id != tour_line.tour_id.id:
                    start_action_type = "loading"
                else:
                    start_action_type = "no"
                previous_tour_id = tour_line.tour_id.id

                # Compute if it is an unloading at the end of the tour line
                if i < len(tour_lines) - 1:
                    if tour_line.tour_id != tour_lines[i + 1].tour_id:
                        arrival_action_type = "unloading"
                    else:
                        arrival_action_type = "no"
                else:
                    arrival_action_type = "unloading"
                line_vals.append(
                    {
                        "start_action_type": start_action_type,
                        "arrival_action_type": arrival_action_type,
                        "tour_line_id": tour_line.id,
                    }
                )

            self.write(
                {
                    "start_date": min(tour_lines.mapped("start_date")),
                    "arrival_date": max(tour_lines.mapped("arrival_date")),
                    "state": "computed",
                    "line_ids": [(5,)] + [(0, 0, x) for x in line_vals],
                }
            )
        else:
            vals = self._INVALIDATE_VALS.copy()
            vals["state"] = "not_computable"
            self.write(vals)

    def _invalidate(self):
        self.write(self._INVALIDATE_VALS)

    def button_compute_tour(self):
        Wizard = self.env["joint.buying.wizard.find.route"]
        results = Wizard.compute_tours(self)
        for request in self:
            request._set_tour_lines(results[request][1])

    @api.multi
    def button_see_tours(self):
        self.ensure_one()
        res = self.env["ir.actions.act_window"].for_xml_id(
            "joint_buying_base", "action_joint_buying_tour_all"
        )
        tours = self.mapped("line_ids.tour_line_id.tour_id")
        res.update(
            {
                "domain": [("id", "in", tours.ids)],
                "view_mode": "tree,calendar,form",
                "views": [(False, "tree"), (False, "calendar"), (False, "form")],
            }
        )
        return res

    def cron_compute_tour(self, delay):
        max_write_date = fields.datetime.now() - timedelta(minutes=delay)
        requests = self.search(
            [
                ("state", "in", ["to_compute", "not_computable"]),
                ("write_date", "<", max_write_date),
            ],
            order="write_date",
            limit=1000,
        )
        requests.button_compute_tour()

    def _get_report_tour_data(self):
        def _prepare_base_data(self):
            return {
                "request_id": self.id,
                "recipient_partner": self.arrival_partner_id,
                "origin_partner": self.start_partner_id,
                "weight": self.total_weight,
            }

        self.ensure_one()
        func = getattr(self, "_get_report_tour_data_%s" % self.request_type)
        res = func()
        for item in res:
            item.update(_prepare_base_data(self))
        return res

    def _get_report_tour_data_manual(self):
        self.ensure_one()
        return [
            {
                "product_category": "",
                "supplier_partner": False,
                "description": self.description,
            }
        ]
