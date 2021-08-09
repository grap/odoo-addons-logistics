# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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

    line_ids = fields.One2many(
        comodel_name="joint.buying.wizard.set.tour.line",
        required=True,
        default=lambda x: x._default_line_ids(),
        inverse_name="wizard_id",
    )

    def _default_tour_id(self):
        return self.env.context.get("active_id")

    def _default_line_ids(self):
        tour = self.env["joint.buying.tour"].browse(self.env.context.get("active_id"))
        line_vals = []
        if not tour.line_ids:
            return []
        else:
            line_vals.append(
                (0, 0, {"point_id": tour.line_ids[0].starting_point_id.id})
            )
        for line in tour.line_ids:
            line_vals.append((0, 0, {"point_id": line.arrival_point_id.id}))
        return line_vals

    @api.multi
    def set_tour(self):
        self.ensure_one()
        self.tour_id.change_tour_lines(self.line_ids)
        return True
