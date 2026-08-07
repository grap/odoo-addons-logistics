# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "joint.buying.mixin"]

    @api.constrains("uom_id", "uom_po_id", "uom_package_id")
    def _check_joint_buying_uom(self):
        if self.filtered(
            lambda x: x.is_joint_buying and x.uom_po_id != x.uom_id and x.uom_package_id
        ):
            raise ValidationError(
                _(
                    "You can not set UoM Weight / Unit if the product"
                    " has a invoice supplier UoM different of the main UoM."
                )
            )

    @api.constrains("uom_id", "uom_measure_type")
    def _check_joint_buying_measure_type(self):
        if self.filtered(
            lambda x: x.is_joint_buying and x.uom_measure_type not in ["unit", "weight"]
        ):
            raise ValidationError(
                _(
                    "Only Weight and Unit are correct main UoM"
                    " in a joint buying purchase context."
                )
            )
