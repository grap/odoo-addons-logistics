# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError

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
    )

    purchase_qty = fields.Float(readonly=True)

    purchase_price_unit = fields.Float(readonly=True)

    purchase_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        related="joint_buying_local_product_id.uom_po_id",
        readonly=True,
    )

    def _prepare_purchase_order_line_vals(self, purchase_order):
        self.ensure_one()
        product_lang = self.joint_buying_local_product_id.with_context(
            lang=purchase_order.partner_id.lang,
            partner_id=purchase_order.partner_id.id,
            supplier_info_name=True,
        )
        return {
            "order_id": purchase_order.id,
            "date_planned": purchase_order.date_planned,
            "name": product_lang.display_name,
            "product_id": self.joint_buying_local_product_id.id,
            "product_qty": self.purchase_qty,
            "product_uom": self.purchase_uom_id.id,
            "price_unit": self.purchase_price_unit,
        }

    def _check_values(self):
        for line in self:
            if not line.joint_buying_local_product_id:
                raise ValidationError(
                    _(
                        "You should define a local product for the line %s"
                        % line.joint_buying_global_product_id.display_name
                    )
                )
