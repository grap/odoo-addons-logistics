# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons.joint_buying_product.models.product_product import (
    _JOINT_BUYING_PRODUCT_CONTEXT,
)


class JointBuyingCreatePurchaseOrderWizardLine(models.TransientModel):
    _name = "joint.buying.create.purchase.order.wizard.line"
    _description = "Joint Buying Wizard Line to create Purchase Orders"

    wizard_id = fields.Many2one(
        comodel_name="joint.buying.create.purchase.order.wizard",
        ondelete="cascade",
        required=True,
    )

    joint_buying_purchase_order_line_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order.line",
        string="Line",
        required=True,
        readonly=True,
    )

    joint_buying_global_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Joint Buying Product",
        context=_JOINT_BUYING_PRODUCT_CONTEXT,
        required=True,
        readonly=True,
    )

    joint_buying_local_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Local Product",
        required=True,
    )

    purchase_qty = fields.Float(
        required=True,
    )

    purchase_price_unit = fields.Float(
        required=True,
    )

    purchase_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="joint_buying_local_product_id.uom_po_id",
        readonly=True,
    )

    def _prepare_purchase_order_line_vals(self, purchase_order):
        self.ensure_one()
        return {
            "order_id": purchase_order.id,
            "date_planned": purchase_order.date_planned,
            "name": "/",
            "product_id": self.joint_buying_local_product_id.id,
            "product_qty": self.purchase_qty,
            "product_uom": self.purchase_uom_id.id,
            "price_unit": self.purchase_price_unit,
        }
