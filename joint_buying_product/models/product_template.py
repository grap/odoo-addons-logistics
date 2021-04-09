# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = ["product.template", "joint.buying.mixin"]
    _name = "product.template"

    joint_buying_partner_id = fields.Many2one(
        name="Joint Buying Supplier",
        domain="[('is_joint_buying', '=', True), ('supplier', '=', True)]",
        comodel_name="res.partner",
    )

    @api.constrains("is_joint_buying", "joint_buying_partner_id")
    def _check_joint_buying_partner_id(self):
        if self.filtered(lambda x: x.is_joint_buying and not x.joint_buying_partner_id):
            raise ValidationError(
                _("You should set a Joint Buying Supplier" " for Joint Buying Products")
            )
