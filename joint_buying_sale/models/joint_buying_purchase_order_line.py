# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class JointBuyingPurchaseOrderLine(models.Model):
    _inherit = "joint.buying.purchase.order.line"

    def _prepare_sale_order_line_vals(self, sale_order):
        self.ensure_one()
        return {
            "order_id": sale_order.id,
            "product_id": self.product_id.get_joint_buying_local_partner_id().id,
            "product_uom_qty": self.qty,
            "product_uom": self.uom_id.id,
        }
