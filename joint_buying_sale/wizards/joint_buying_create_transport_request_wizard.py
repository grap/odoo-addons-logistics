# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingCreateTransportRequestWizard(models.TransientModel):
    _name = "joint.buying.create.transport.request.wizard"
    _description = "Joint Buying Wizard to create Transport Request From Sale Orders"

    availability_date = fields.Datetime(
        string="Availability Date",
        required=True,
    )

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        required=True,
        readonly=True,
        default=lambda x: x._default_sale_order_id(),
        ondelete="cascade",
    )

    start_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Origin",
        required=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    arrival_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Destination",
        required=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="joint_buying_create_transport_request_wizard_product_rel",
        default=lambda x: x._default_product_ids(),
    )

    def _default_sale_order_id(self):
        sale_order_id = self.env.context.get("active_id")
        JointBuyingPurchaseOrder = self.env["joint.buying.purchase.order"]

        purchase_orders = JointBuyingPurchaseOrder.search(
            [("sale_order_id", "=", sale_order_id)]
        )
        if purchase_orders:
            raise UserError(
                _(
                    "Your Sale Order has been generated from a Joint Buying Purchase Order."
                    " A transport request has still been generated."
                    " There is no need to create a new one."
                )
            )

        return sale_order_id

    def _default_product_ids(self):

        sale_order = self.env["sale.order"].browse(self.env.context.get("active_id"))
        products = (
            sale_order.mapped("order_line")
            .filtered(lambda x: x.product_id.type != "service")
            .mapped("product_id")
        )
        if not products:
            raise UserError(_("There are no products to deliver."))

        return products.ids

    def create_transport_request(self):
        self.ensure_one()

        if self.sale_order_id.joint_buying_transport_request_id:
            raise UserError(_("There is already a transport demand for this sale."))

        if self.product_ids.filtered(lambda x: x.weight == 0):
            raise UserError(_("Please set a weight for all products."))

        self.sale_order_id.recalculate_weight()

        # Create new transport request
        request_vals = {
            "sale_order_id": self.sale_order_id.id,
            "manual_availability_date": self.availability_date,
            "manual_start_partner_id": self.start_partner_id.id,
            "manual_arrival_partner_id": self.arrival_partner_id.id,
        }

        request = self.env["joint.buying.transport.request"].create(request_vals)

        # Try to find a route, if possible
        request.button_compute_tour()

        # Display the new created transport request
        res = self.env["ir.actions.act_window"].for_xml_id(
            "joint_buying_base", "action_joint_buying_transport_request"
        )
        res.update(
            {
                "views": [(False, "form"), (False, "tree")],
                "res_id": request.id,
            }
        )
        return res
