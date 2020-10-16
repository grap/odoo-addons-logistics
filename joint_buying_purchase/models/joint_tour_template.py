from odoo import fields, models


class JointBuyingTourTemplate(models.Model):
    _name = "joint.buying.tour.template"
    _description = "Joint buying tour template"

    name = fields.Char(string="Name of tour template")
    step_ids = fields.One2many(
        "res.partner",
        inverse_name="tour_template_id",
        string="These activities can be steps for this touring template",
        domain=[("is_joint_buying", "=", True)]
    )
