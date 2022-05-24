# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingCreateSaleOrderWizardLine(models.TransientModel):
    _name = "joint.buying.create.sale.order.wizard.line"
    _description = "Joint Buying Wizard Line to create Sale Orders"

    wizard_id = fields.Many2one(
        comodel_name="joint.buying.create.sale.order.wizard",
        ondelete="cascade",
        required=True,
    )

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Order",
        required=True,
        readonly=True,
    )

    amount_untaxed = fields.Float(
        string="Total Untaxed Amount",
        compute="_compute_amount",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    joint_buying_global_customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Joint Buying Customer",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        required=True,
        readonly=True,
    )

    joint_buying_local_customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Local Customer",
    )
