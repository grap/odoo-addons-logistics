# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class JointBuyingCreateSaleOrderWizard(models.TransientModel):
    _name = "joint.buying.create.sale.order.wizard"
    _description = "Joint Buying Wizard to create Sale Orders"

    grouped_order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order.grouped",
        required=True,
        readonly=True,
        default=lambda x: x._default_grouped_order_id(),
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.create.sale.order.wizard.line",
        default=lambda x: x._default_line_ids(),
        inverse_name="wizard_id",
    )

    def _default_grouped_order_id(self):
        return self.env.context.get("active_id")

    def _default_line_ids(self):

        line_vals = []

        grouped_order = self.env["joint.buying.purchase.order.grouped"].browse(
            self.env.context.get("active_id")
        )

        orders = grouped_order.mapped("order_ids").filtered(
            lambda x: x.purchase_ok not in ["no_line", "null_amount"]
        )
        if not orders:
            raise UserError(_("There are no orders with valid amount."))

        orders = orders.filtered(lambda x: not x.sale_order_id)
        if not orders:
            raise UserError(_("All the sale orders have still been created."))

        for order in orders:
            local_partner = order.customer_id.get_joint_buying_local_partner_id()
            line_vals.append(
                (
                    0,
                    0,
                    {
                        "order_id": order.id,
                        "amount_untaxed": order.amount_untaxed,
                        "joint_buying_global_customer_id": order.customer_id.id,
                        "joint_buying_local_customer_id": local_partner
                        and local_partner.id,
                    },
                )
            )

        return line_vals

    def create_sale_order(self):
        self.ensure_one()

        # Save local customers, if the value has changed
        for line in self.line_ids:
            if not line.joint_buying_local_customer_id:
                raise ValidationError(
                    _(
                        "You should define the customer in your local partners database"
                        " to create a sale order for him."
                    )
                )
            line.order_id.customer_id.set_joint_buying_local_partner_id(
                line.joint_buying_local_customer_id
            )

        # Create Sale orders
        for order in self.line_ids.mapped("order_id"):
            order.create_sale_order()

        # return the form / tree view of the sale orders created
        result = self.env.ref("sale.action_orders").read()[0]
        form_view = self.env.ref("sale.view_order_form").id
        sale_order_ids = self.line_ids.mapped("order_id.sale_order_id").ids
        if len(sale_order_ids) == 1:
            result.update({"views": [(form_view, "form")], "res_id": sale_order_ids[0]})
        else:
            result["domain"] = "[('id','in',%s)]" % (sale_order_ids)
        return result
