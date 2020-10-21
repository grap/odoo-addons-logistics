from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    tour_template_id = fields.Many2one(
        "joint.buying.tour.template", string="Tour template"
    )
