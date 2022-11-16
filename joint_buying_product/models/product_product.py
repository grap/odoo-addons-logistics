# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)

_JOINT_BUYING_PRODUCT_CONTEXT = {
    "joint_buying": 1,
    "form_view_ref": "joint_buying_product.view_product_product_form",
    "tree_view_ref": "joint_buying_product.view_product_product_tree",
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

    joint_buying_display_propagation = fields.Boolean(
        string="Display Joint Buying Propagation button",
        help="Technical field to know if the button to create or see"
        " the joint buying products is visible",
        compute="_compute_joint_buying_display_propagation",
    )

    joint_buying_product_id = fields.Many2one(
        string="Joint Buying Product",
        comodel_name="product.product",
        readonly=True,
        context=_JOINT_BUYING_PRODUCT_CONTEXT,
        copy=False,
    )

    joint_buying_category_id = fields.Many2one(
        string="Joint Buying Category",
        comodel_name="joint.buying.category",
        domain="[('supplier_id', '=', parent.id)]",
    )

    joint_buying_is_new = fields.Boolean(
        string="Is New",
        help="Check this box if the product is new."
        " This box will be automatically unchecked by cron task"
        " after a given number of days.",
        default=lambda x: x._default_joint_is_new(),
    )

    joint_buying_purchase_order_line_ids = fields.One2many(
        comodel_name="joint.buying.purchase.order.line",
        inverse_name="product_id",
        string="Order Lines",
    )

    joint_buying_is_sold = fields.Boolean(
        compute="_compute_joint_buying_is_sold",
    )

    # Default Section
    def _default_joint_is_new(self):
        return self.env.context.get("joint_buying", False)

    # Constrains Sections
    @api.constrains("is_joint_buying", "joint_buying_partner_id")
    def _check_joint_buying_partner_id(self):
        if self.filtered(lambda x: x.is_joint_buying and not x.joint_buying_partner_id):
            raise ValidationError(
                _("You should set a Joint Buying Supplier for Joint Buying Products")
            )

    # compute section
    @api.depends("joint_buying_purchase_order_line_ids.product_id")
    def _compute_joint_buying_is_sold(self):
        for product in self.filtered(lambda x: x.is_joint_buying):
            product.joint_buying_is_sold = len(
                product.joint_buying_purchase_order_line_ids
            )

    @api.depends("company_id.is_joint_buying_supplier")
    def _compute_joint_buying_display_propagation(self):
        for product in self:
            product.joint_buying_display_propagation = (
                product.company_id.is_joint_buying_supplier
            )

    # Overload Section
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

    # custom Section
    def get_joint_buying_local_product_id(self):
        """Return the local product of a global product, if exists"""
        self.ensure_one()
        products = self.with_context(active_test=False, joint_buying=False).search(
            [
                ("joint_buying_product_id", "=", self.id),
                ("company_id", "=", self.env.user.company_id.id),
            ]
        )
        return products and products[0] or False

    @api.model
    def joint_byuing_cron_check_new(self):
        """This cron function will unflag the field 'joint_buying_is_new'
        for product that are not new anymore"""
        new_product_day = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("joint_buying_product.new_product_day")
        )
        threshold_old_date = fields.datetime.now() + timedelta(days=-new_product_day)
        products = self.with_context(joint_buying=True).search(
            [
                ("create_date", "<", threshold_old_date),
                ("joint_buying_is_new", "=", True),
            ]
        )
        products.write({"joint_buying_is_new": False})

    def create_joint_buying_product(self):
        products = self.filtered(
            lambda x: (
                not x.joint_buying_product_id and x.joint_buying_display_propagation
            )
        )
        for product in products:
            vals = product._prepare_joint_buying_product("create")
            product.joint_buying_product_id = self.with_context(
                joint_buying=True, joint_buying_local_to_global=True
            ).create(vals)
        return products.mapped("joint_buying_product_id")

    def update_joint_buying_product(self):
        products = self.filtered(lambda x: (x.joint_buying_product_id))
        for product in products:
            vals = product._prepare_joint_buying_product("update")
            global_product = product.joint_buying_product_id.with_context(
                joint_buying=True, joint_buying_local_to_global=True
            )
            global_product.write(vals)

    def _prepare_joint_buying_product(self, action):
        self.ensure_one()
        pricelist = self.company_id.joint_buying_pricelist_id
        if pricelist:
            price = self.with_context(pricelist=pricelist.id).price
        else:
            price = self.lst_price
        vals = {
            "name": self.name,
            "image": self.image,
            "default_code": self.default_code,
            "weight": self.weight,
            "barcode": self.barcode,
            "lst_price": price,
        }
        if action == "create":
            vals.update(
                {
                    "uom_id": self.uom_id.id,
                    "uom_po_id": self.uom_id.id,
                    "categ_id": self.env.ref(
                        "joint_buying_product.product_category"
                    ).id,
                    "joint_buying_partner_id": self.company_id.joint_buying_partner_id.id,
                }
            )
        return vals
