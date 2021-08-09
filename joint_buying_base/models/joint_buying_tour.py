# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingTour(models.Model):
    _name = "joint.buying.tour"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Joint buying tour"
    _order = "date_tour, name"

    name = fields.Char(required=True)

    distance = fields.Float(
        compute="_compute_distance",
        store=True,
        help="Distance as the crow flies, in kilometer",
    )

    carrier_id = fields.Many2one(
        comodel_name="joint.buying.carrier", string="Carrier", required=True
    )

    date_tour = fields.Datetime(required=True, track_visibility=True)

    starting_point_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_points",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    arrival_point_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_points",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    complete_name = fields.Char(compute="_compute_complete_name", store=True)

    line_ids = fields.One2many(
        comodel_name="joint.buying.tour.line",
        inverse_name="tour_id",
        readonly=True,
        copy=True,
        auto_join=True,
    )

    line_qty = fields.Char(
        string="Step Quantity", compute="_compute_line_qty", store=True
    )

    is_loop = fields.Boolean(string="Is a Loop", compute="_compute_is_loop", store=True)

    # Compute Section
    @api.depends("name", "date_tour")
    def _compute_complete_name(self):
        for tour in self:
            tour.complete_name = "{} - {}".format(tour.date_tour, tour.name)

    @api.depends("starting_point_id", "arrival_point_id")
    def _compute_is_loop(self):
        for tour in self:
            tour.is_loop = tour.starting_point_id == tour.arrival_point_id

    @api.depends("line_ids.distance")
    def _compute_distance(self):
        for tour in self:
            tour.distance = sum(tour.mapped("line_ids.distance"))

    @api.depends("line_ids")
    def _compute_line_qty(self):
        for tour in self:
            tour.line_qty = len(tour.line_ids)

    @api.depends(
        "line_ids.starting_point_id", "line_ids.sequence", "line_ids.arrival_point_id"
    )
    def _compute_points(self):
        for tour in self:
            if not tour.line_ids:
                continue
            tour.starting_point_id = tour.line_ids[0].starting_point_id
            tour.arrival_point_id = tour.line_ids[-1].arrival_point_id

    # Overload Section
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default["name"] = _("%s (copy)") % self.name
        return super().copy(default)

    # Custom Section
    @api.multi
    def change_tour_lines(self, wizard_lines):
        self.ensure_one()
        TourLine = self.env["joint.buying.tour.line"]

        # TODO, raise an event, to cancel all previous moves associated to
        # orders

        self.line_ids.unlink()

        for i in range(len(wizard_lines))[:-1]:
            TourLine.create(
                {
                    "sequence": i,
                    "tour_id": self.id,
                    "starting_point_id": wizard_lines[i].point_id.id,
                    "arrival_point_id": wizard_lines[i + 1].point_id.id,
                }
            )