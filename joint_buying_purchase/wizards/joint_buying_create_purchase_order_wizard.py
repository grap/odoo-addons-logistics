# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingCreatePurchaseOrderWizard(models.TransientModel):
    _name = "joint.buying.create.purchase.order.wizard"
    _description = "Joint Buying Wizard to create Purchase Orders"

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        required=True,
        readonly=True,
        default=lambda x: x._default_order_id(),
    )

    date_planned = fields.Datetime(
        required=True,
        default=lambda x: x._default_date_planned(),
    )

    joint_buying_global_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Joint Buying Supplier",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        related="order_id.supplier_id",
        required=True,
        readonly=True,
    )

    joint_buying_local_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Local Supplier",
        required=True,
        default=lambda x: x._default_joint_buying_local_supplier_id(),
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.create.purchase.order.wizard.line",
        default=lambda x: x._default_line_ids(),
        inverse_name="wizard_id",
    )

    def _default_date_planned(self):
        # TODO: With LOG2, recovered the delivery date
        return False

    def _default_order_id(self):
        return self.env.context.get("active_id")

    def _default_joint_buying_local_supplier_id(self):
        order = self.env["joint.buying.purchase.order"].browse(
            self.env.context.get("active_id")
        )
        return order and order.supplier_id.get_joint_buying_local_partner_id() or False

    def _default_line_ids(self):

        line_vals = []

        order = self.env["joint.buying.purchase.order"].browse(
            self.env.context.get("active_id")
        )

        lines = order.mapped("line_ids").filtered(lambda x: x.qty)
        if not lines:
            raise UserError(_("There are no lines with not null quantity."))

        for line in lines:
            local_product = line.product_id.get_joint_buying_local_product_id()
            vals = {
                "joint_buying_purchase_order_line_id": line.id,
                "joint_buying_global_product_id": line.product_id.id,
                "joint_buying_local_product_id": local_product and local_product.id,
                "purchase_qty": 0.0,  # TODO
                "purchase_uom_id": local_product and local_product.uom_po_id.id,
            }
            line_vals.append((0, 0, vals))

        return line_vals

    def create_purchase_order(self):
        self.ensure_one()

        # Save local supplier
        self.joint_buying_global_supplier_id.set_joint_buying_local_partner_id(
            self.joint_buying_local_supplier_id
        )

        # Save local products
        for line in self.line_ids:
            line.product_id.set_joint_buying_local_product_id(
                line.joint_buying_local_product_id
            )

        # Create Purchase Order
        self._create_purchase_order()

        # return the form / tree view of the purchase orders created
        result = self.env.ref("purchase.purchase_order_action_generic").read()[0]
        form_view = self.env.ref("purchase.purchase_order_form").id
        result.update(
            {
                "views": [(form_view, "form")],
                "res_id": self.order_id.purchase_order_id.id,
            }
        )
        return result

    def _create_purchase_order(self):
        self.ensure_one()
        PurchaseOrder = self.env["purchase.order"]
        PurchaseOrderLine = self.env["purchase.order.line"]
        order_vals = self._prepare_purchase_order_vals()
        purchase_order = PurchaseOrder.create(order_vals)
        for line in self.line_ids:
            order_line_vals = line._prepare_purchase_order_line_vals(purchase_order)
            PurchaseOrderLine.create(order_line_vals)
        self.order_id.purchase_order_id = purchase_order.id

    def _prepare_purchase_order_vals(self):
        self.ensure_one()
        partner = self.joint_buying_local_supplier_id
        return {
            "partner_id": partner.id,
            "date_planned": self.date_planned,
            "company_id": self.env.user.company_id.id,
            "fiscal_position_id": partner.property_account_position_id
            and partner.property_account_position_id.id,
        }
