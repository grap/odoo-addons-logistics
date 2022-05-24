# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingPurchaseOrder(models.Model):
    _inherit = "joint.buying.purchase.order"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        help="Related sale order in the local database of the"
        " supplier for the related customer.",
    )

    def create_sale_order(self):
        self.ensure_one()
        SaleOrder = self.env["sale.order"]
        SaleOrderLine = self.env["sale.order.line"]
        order_vals = self._prepare_sale_order_vals()
        sale_order = SaleOrder.create(order_vals)
        for line in self.line_ids.filtered(lambda x: x.qty > 0):
            order_line_vals = line._prepare_sale_order_line_vals(sale_order)
            SaleOrderLine.create(order_line_vals)
        self.sale_order_id = sale_order.id

    def _prepare_sale_order_vals(self):
        self.ensure_one()
        partner = self.customer_id.get_joint_buying_local_partner_id()
        return {
            "partner_id": partner.id,
            "company_id": self.env.user.company_id.id,
            "pricelist_id": partner.property_product_pricelist.id,
            "fiscal_position_id": partner.property_account_position_id
            and partner.property_account_position_id.id,
            "commitment_date": self.grouped_order_id.deposit_date,
        }
