# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingWizardCreateOrder(models.TransientModel):
    _name = "joint.buying.wizard.create.order"
    _description = "Joint Buying Wizard Create Order"

    supplier_id = fields.Many2one(
        required=True,
        string="Supplier",
        comodel_name="res.partner",
        domain="[('is_joint_buying', '=', True), ('supplier', '=', True)]",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        default=lambda x: x._default_partner(),
        ondelete="cascade",
    )

    start_date = fields.Datetime(
        string="Start Date", required=True, default=lambda x: x._default_start_date()
    )

    end_date = fields.Datetime(string="End Date", required=True)

    deposit_date = fields.Datetime(string="Deposit Date", required=True)

    pivot_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Pivot Company",
        required=True,
        default=lambda x: x._default_partner().joint_buying_pivot_company_id,
    )

    deposit_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Deposit Place",
        required=True,
        domain="[('is_joint_buying_stage', '=', True)]",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    minimum_amount = fields.Float(
        string="Minimum Amount",
        default=lambda x: x._default_partner().joint_buying_minimum_amount,
    )

    minimum_unit_amount = fields.Float(
        string="Minimum Unit Amount",
        default=lambda x: x._default_partner().joint_buying_minimum_unit_amount,
    )

    minimum_weight = fields.Float(
        string="Minimum Weight",
        default=lambda x: x._default_partner().joint_buying_minimum_weight,
    )

    minimum_unit_weight = fields.Float(
        string="Minimum Unit Weight",
        default=lambda x: x._default_partner().joint_buying_minimum_unit_weight,
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.wizard.create.order.line",
        required=True,
        default=lambda x: x._default_line_ids(),
        inverse_name="wizard_id",
    )

    product_qty = fields.Integer(
        string="Product Quantity", compute="_compute_product_qty"
    )

    overlap_message = fields.Html(compute="_compute_overlap_message")

    use_joint_buying_category = fields.Boolean(
        compute="_compute_use_joint_buying_category"
    )

    category_ids = fields.Many2many(
        string="Joint Buying Categories",
        comodel_name="joint.buying.category",
        domain="[('supplier_id', '=', supplier_id)]",
    )

    # Default Section
    def _default_partner(self):
        return self.env["res.partner"].browse(self.env.context.get("active_id"))

    def _default_start_date(self):
        return fields.datetime.now()

    def _default_line_ids(self):
        partner = self.env["res.partner"].browse(self.env.context.get("active_id"))
        line_vals = []
        for partner in partner.mapped(
            "joint_buying_subscribed_company_ids.joint_buying_partner_id"
        ):
            line_vals.append((0, 0, {"customer_id": partner.id}))
        return line_vals

    # Compute Section
    @api.depends("supplier_id.joint_buying_category_ids")
    def _compute_use_joint_buying_category(self):
        self.ensure_one()
        self.use_joint_buying_category = bool(
            self.supplier_id.joint_buying_category_ids
        )

    @api.depends(
        "category_ids",
        "supplier_id.joint_buying_product_ids.purchase_ok",
        "supplier_id.joint_buying_product_ids.joint_buying_category_id",
    )
    def _compute_product_qty(self):
        self.ensure_one()
        self.product_qty = len(
            self.supplier_id._get_joint_buying_products(self.category_ids)
        )

    @api.depends("start_date", "end_date")
    def _compute_overlap_message(self):
        self.ensure_one()
        overload_grouped_orders = self.env[
            "joint.buying.purchase.order.grouped"
        ].search(
            [
                ("supplier_id", "=", self.supplier_id.id),
                ("start_date", "<", self.end_date),
                ("end_date", ">", self.start_date),
            ]
        )
        if overload_grouped_orders:
            self.overlap_message = _(
                "There are already one or more group orders open for this period."
                " Are you sure you want to open another one ?<br/><br/> - %s"
                % (
                    "<br/> - ".join(
                        [
                            _("%s (Start : %s ; End : %s)")
                            % (x.name, x.start_date, x.end_date)
                            for x in overload_grouped_orders
                        ]
                    )
                )
            )

    @api.multi
    def create_order_grouped(self):
        self.ensure_one()
        OrderGrouped = self.env["joint.buying.purchase.order.grouped"]
        order_grouped = OrderGrouped.create(
            OrderGrouped._prepare_order_grouped_vals(
                self.supplier_id,
                self.mapped("line_ids.customer_id"),
                self.start_date,
                self.end_date,
                self.deposit_date,
                self.pivot_company_id,
                self.deposit_partner_id,
                self.minimum_amount,
                self.minimum_unit_amount,
                self.minimum_weight,
                self.minimum_unit_weight,
                self.category_ids,
            )
        )

        form_view = self.env.ref(
            "joint_buying_product.view_joint_buying_purchase_order_grouped_form"
        )

        action = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_grouped_all"
        ).read()[0]
        action.update({"res_id": order_grouped.id, "views": [(form_view.id, "form")]})
        return action
