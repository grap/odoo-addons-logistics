# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = ["product.product", "joint.buying.mixin"]
    _name = "product.product"

    is_joint_buying = fields.Boolean(
        string="For Joint Buying",
        related="product_tmpl_id.is_joint_buying",
        store=True,
        readonly=True,
    )

    joint_buying_partner_id = fields.Many2one(
        string="Joint Buying Supplier",
        comodel_name="res.partner",
        related="product_tmpl_id.joint_buying_partner_id",
        store=True,
        readonly=False,
    )

    joint_buying_product_id = fields.Many2one(
        string="Joint Buying Product", comodel_name="product.product", readonly=True
    )

    def _check_create_joint_buying_product(self):
        pass
        # Check product company are all the same
        # check if the company is a supplier company for joint Buying
        # check if the product doesn't have a joint_buying_product
        return self.filtered(lambda x: not x.joint_buying_product_id)

    def create_joint_buying_product(self):
        products = self._check_create_joint_buying_product()
        for product in products:
            vals = product._prepare_joint_buying_product()
            self.create(vals)

    def _prepare_joint_buying_product(self):
        self.ensure_one()
        vals = {
            "name": self.name,
            "weight": self.weight,
            "barcode": self.barcode,
            "categ_id": self.env.ref("joint_buying_product.product_category").id,
            "company_id": False,
            "is_joint_buying": False,
            "joint_buying_partner_id": self.company_id.joint_buying_partner_id.id,
        }
        return vals
