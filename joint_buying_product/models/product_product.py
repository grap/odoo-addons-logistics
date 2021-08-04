# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)

_JOINT_BUYING_PRODUCT_CONTEXT = {
    "joint_buying": 1,
    "form_view_ref": "joint_buying_product.view_product_product_form_joint_buying",
    "tree_view_ref": "joint_buying_product.view_product_product_tree_joint_buying",
}


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = [
        "product.product",
        "joint.buying.mixin",
        "joint.buying.check.access.mixin",
    ]

    _check_write_access_company_field_id = (
        "joint_buying_partner_id.joint_buying_pivot_company_id"
    )

    is_joint_buying = fields.Boolean(
        string="For Joint Buying",
        related="product_tmpl_id.is_joint_buying",
        store=True,
        readonly=True,
    )

    joint_buying_partner_id = fields.Many2one(
        name="Joint Buying Supplier",
        domain="[('supplier', '=', True)]",
        comodel_name="res.partner",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    display_joint_buying_propagation = fields.Boolean(
        string="Display Joint Buying Propagation button",
        help="Technical field to know if the button to create or see"
        " the joint buying products is visible",
        related="company_id.is_joint_buying_customer",
        store=True,
    )

    joint_buying_product_id = fields.Many2one(
        string="Joint Buying Product",
        comodel_name="product.product",
        readonly=True,
        context=_JOINT_BUYING_PRODUCT_CONTEXT,
    )

    @api.constrains(
        "is_joint_buying", "joint_buying_partner_id", "display_joint_buying_propagation"
    )
    def _check_joint_buying_partner_id(self):
        if self.filtered(lambda x: x.is_joint_buying and not x.joint_buying_partner_id):
            raise ValidationError(
                _("You should set a Joint Buying Supplier for Joint Buying Products")
            )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if self.env.context.get("joint_buying", False) and not self.env.context.get(
            "joint_buying_local_to_global", False
        ):
            if res.joint_buying_partner_id.joint_buying_company_id:
                raise ValidationError(
                    _(
                        "You can not create a Joint buying Product for this supplier."
                        " Please ask to the saler to do it by clicking on"
                        " 'Offer For Joint Buying' on him product."
                    )
                )
        return res

    @api.multi
    def write(self, vals):
        if vals.get("joint_buying_partner_id", False):
            for product in self:
                if product.joint_buying_partner_id.id != vals.get(
                    "joint_buying_partner_id"
                ):
                    raise ValidationError(
                        _("You can not change the value of the Joint buying partner.")
                    )
        return super().write(vals)

    def create_joint_buying_product(self):
        products = self.filtered(
            lambda x: (
                not x.joint_buying_product_id and x.display_joint_buying_propagation
            )
        )
        for product in products:
            vals = product._prepare_joint_buying_product()
            product.joint_buying_product_id = self.with_context(
                joint_buying=True, joint_buying_local_to_global=True
            ).create(vals)

    def _prepare_joint_buying_product(self):
        self.ensure_one()
        vals = {
            "name": self.name,
            "weight": self.weight,
            "barcode": self.barcode,
            "categ_id": self.env.ref("joint_buying_product.product_category").id,
            "joint_buying_partner_id": self.company_id.joint_buying_partner_id.id,
        }
        return vals
