# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from ..models.res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingWizardSetTour(models.TransientModel):
    _name = "joint.buying.wizard.set.tour"
    _description = "Joint Buying Wizard Set Tour"

    tour_id = fields.Many2one(
        string="Tour",
        comodel_name="joint.buying.tour",
        default=lambda x: x._default_tour_id(),
        required=True,
        ondelete="cascade",
    )

    starting_point_id = fields.Many2one(
        required=True,
        string="Starting Point",
        comodel_name="res.partner",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        domain="[('is_joint_buying_stage', '=', True)]",
        default=lambda x: x._default_starting_point_id(),
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.wizard.set.tour.line",
        required=True,
        default=lambda x: x._default_line_ids(),
        inverse_name="wizard_id",
    )

    def _default_tour_id(self):
        return self.env.context.get("active_id")

    def _default_starting_point_id(self):
        tour = self.env["joint.buying.tour"].browse(self.env.context.get("active_id"))
        journey_lines = tour.line_ids.filtered(lambda x: x.sequence_type == "journey")
        if journey_lines:
            return journey_lines[0].starting_point_id

    def _default_line_ids(self):
        tour = self.env["joint.buying.tour"].browse(self.env.context.get("active_id"))
        line_vals = []
        if not tour.line_ids:
            return []
        for line in tour.line_ids:
            _vals = {
                "sequence": line.sequence,
                "sequence_type": line.sequence_type,
                "point_id": line.arrival_point_id.id,
                "duration": line.duration,
                "distance": line.distance,
            }
            line_vals.append((0, 0, _vals))
        return line_vals

    @api.multi
    def set_tour(self):
        self.ensure_one()
        # TODO - Optimize. do not delete lines, if lines are the same
        self.tour_id.line_ids.unlink()
        current_starting_point = self.starting_point_id
        line_vals = []
        for i, wizard_line in enumerate(self.line_ids):

            line_vals.append(
                (
                    0,
                    0,
                    {
                        "tour_id": self.tour_id.id,
                        "sequence": i,
                        "sequence_type": wizard_line.sequence_type,
                        "starting_point_id": current_starting_point.id,
                        "arrival_point_id": wizard_line.point_id.id,
                        "duration": wizard_line.duration,
                        "distance": wizard_line.distance,
                    },
                )
            )
            if wizard_line.point_id:
                current_starting_point = wizard_line.point_id
        if line_vals:
            self.tour_id.write({"line_ids": line_vals})
        return True
