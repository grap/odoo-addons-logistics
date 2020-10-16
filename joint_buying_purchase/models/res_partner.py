from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    tour_template_id = fields.Many2one(
        "joint.buying.tour.template", string="Tour template"
    )

    is_joint_buying_customer = fields.Boolean(
        default=False, string="Is a customer for joint buying"
    )
    is_joint_buying_supplier = fields.Boolean(
        default=False, string="Is a supplier for joint buying"
    )

    # Supplier
    activity_id = fields.Many2one(
        "res.partner", string="The activity that manages my stocks"
    )

    # Customer
    supplier_ids = fields.One2many(
        "res.partner",
        inverse_name="activity_id",
        strings=(
            "Suppliers to manage, if there are one or more company,"
            " then this is a pivot activity"
        ),
        domain=[('is_joint_buying', '=', True)]
    )
