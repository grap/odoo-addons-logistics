# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    joint_buying_product_ids = fields.One2many(
        "product.product", inverse_name="joint_buying_partner_id"
    )

    joint_buying_product_qty = fields.Integer(
        compute="_compute_joint_buying_product_qty"
    )

    joint_buying_grouped_order_ids = fields.One2many(
        "joint.buying.purchase.order.grouped", inverse_name="supplier_id"
    )

    joint_buying_grouped_order_qty = fields.Integer(
        compute="_compute_joint_buying_grouped_order_qty"
    )

    joint_buying_frequency_ids = fields.One2many(
        string="Joint Buying Order Frequencies",
        comodel_name="joint.buying.frequency",
        inverse_name="partner_id",
    )

    joint_buying_frequency_qty = fields.Integer(
        compute="_compute_joint_buying_frequency_qty"
    )

    joint_buying_frequency_description = fields.Char(
        string="Joint Buying Order Frequencies Description",
        compute="_compute_joint_buying_frequency_description",
    )

    joint_buying_category_ids = fields.One2many(
        string="Joint Buying Categories",
        comodel_name="joint.buying.category",
        inverse_name="supplier_id",
    )

    joint_buying_use_category = fields.Boolean(
        string="Use Order Categories", default=False
    )

    joint_buying_use_punctual_grouped_order = fields.Boolean(
        string="One-time Grouped Order", default=False
    )

    joint_buying_minimum_amount = fields.Float(
        string="Minimum Amount For Grouped Order"
    )

    joint_buying_minimum_weight = fields.Float(
        string="Minimum Weight For Grouped Order"
    )

    joint_buying_minimum_unit_amount = fields.Float(
        string="Minimum Amount For Unit Order"
    )

    joint_buying_minimum_unit_weight = fields.Float(
        string="Minimum Weight For Unit Order"
    )

    # Compute Section
    @api.depends("joint_buying_frequency_ids.frequency")
    def _compute_joint_buying_frequency_description(self):
        for partner in self.filtered(lambda x: x.joint_buying_frequency_ids):
            partner.joint_buying_frequency_description = " + ".join(
                [str(x) for x in partner.mapped("joint_buying_frequency_ids.frequency")]
            )

    @api.depends("joint_buying_product_ids")
    def _compute_joint_buying_product_qty(self):
        for partner in self:
            partner.joint_buying_product_qty = len(partner.joint_buying_product_ids)

    @api.depends("joint_buying_frequency_ids")
    def _compute_joint_buying_frequency_qty(self):
        for partner in self:
            partner.joint_buying_frequency_qty = len(partner.joint_buying_frequency_ids)

    @api.depends("joint_buying_grouped_order_ids")
    def _compute_joint_buying_grouped_order_qty(self):
        for partner in self:
            partner.joint_buying_grouped_order_qty = len(
                partner.joint_buying_grouped_order_ids
            )

    # Custom Section
    def _get_joint_buying_products(self, categories):
        self.ensure_one()
        return self.with_context(joint_buying=1).joint_buying_product_ids.filtered(
            lambda x: x.purchase_ok
            and x.active
            and (
                x.joint_buying_category_id.id in categories.ids
                or not x.joint_buying_category_id
            )
        )
