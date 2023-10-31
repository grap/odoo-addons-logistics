# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingPurchaseOrder(models.Model):
    _name = "joint.buying.purchase.order"
    _description = "Joint Buying Purchase Order"
    _inherit = ["joint.buying.check.access.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "end_date desc, supplier_id, customer_id"

    _check_access_can_create = True

    _PURCHASE_STATE = [
        ("draft", "Draft"),
        ("done", "Confirmed"),
        ("skipped", "Skipped"),
    ]

    _PURCHASE_OK_SELECTION = [
        ("no_line", "No Lines"),
        ("no_minimum_amount", "Minimum Amount Not reached"),
        ("no_minimum_weight", "Minimum Weight Not reached"),
        ("null_amount", "Null Amount"),
        ("ok", "OK"),
    ]

    _sql_constraints = [
        (
            "group_order_customer_uniq",
            "unique (grouped_order_id,customer_id)",
            "Customer can have only one purchase for this grouped order !",
        )
    ]

    name = fields.Char(
        string="Number", compute="_compute_name", store=True, compute_sudo=True
    )

    grouped_order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order.grouped",
        string="Grouped Order",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )

    start_date = fields.Datetime(
        related="grouped_order_id.start_date", string="Start Date", store=True
    )

    end_date = fields.Datetime(
        related="grouped_order_id.end_date", string="End Date", store=True
    )

    deposit_date = fields.Datetime(
        related="grouped_order_id.deposit_date", string="Deposit Date", store=True
    )

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        related="grouped_order_id.supplier_id",
        string="Supplier",
        readonly=True,
        store=True,
        index=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    supplier_comment = fields.Text(related="supplier_id.comment")

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        readonly=True,
        index=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    state = fields.Selection(
        related="grouped_order_id.state", string="State", store=True
    )

    purchase_state = fields.Selection(
        selection=_PURCHASE_STATE, required=True, default="draft", track_visibility=True
    )

    request_id = fields.Many2one(
        comodel_name="joint.buying.transport.request",
        string="Transport Request",
        readonly=True,
    )

    request_arrival_date = fields.Datetime(
        string="Final Delivery Date",
        related="request_id.arrival_date",
    )

    pivot_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Pivot Company",
        related="grouped_order_id.pivot_company_id",
        store=True,
    )

    deposit_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Deposit Partner",
        related="grouped_order_id.deposit_partner_id",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    minimum_unit_amount = fields.Float(
        string="Minimum amount",
        related="grouped_order_id.minimum_unit_amount",
        store=True,
    )

    minimum_unit_weight = fields.Float(
        string="Minimum Unit Weight",
        related="grouped_order_id.minimum_unit_weight",
        store=True,
    )

    purchase_ok = fields.Selection(
        string="Purchase OK ?",
        selection=_PURCHASE_OK_SELECTION,
        compute="_compute_purchase_ok",
        store=True,
    )

    line_ids = fields.One2many(
        "joint.buying.purchase.order.line", inverse_name="order_id"
    )

    line_qty = fields.Integer(
        string="Lines Quantity", compute="_compute_line_qty", store=True
    )

    amount_untaxed = fields.Float(
        string="Total Untaxed Amount",
        compute="_compute_amount",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    total_weight = fields.Float(
        string="Total Brut Weight",
        compute="_compute_total_weight",
        store=True,
        digits=dp.get_precision("Stock Weight"),
    )

    is_mine_customer = fields.Boolean(
        compute="_compute_is_mine_customer", search="_search_is_mine_customer"
    )

    is_mine_supplier = fields.Boolean(
        compute="_compute_is_mine_supplier", search="_search_is_mine_supplier"
    )

    is_mine_pivot = fields.Boolean(
        compute="_compute_is_mine_pivot", search="_search_is_mine_pivot"
    )

    has_image = fields.Boolean(compute="_compute_has_image")

    @api.multi
    def _joint_buying_check_access(self):
        # We allow access to customer and to pivot company of the related supplier
        return len(
            self.filtered(lambda x: x.is_mine_customer or x.is_mine_pivot)
        ) == len(self)

    # Compute Section
    @api.depends("line_ids.product_id.image")
    def _compute_has_image(self):
        for order in self:
            order.has_image = any(order.mapped("line_ids.product_id.image"))

    @api.depends(
        "amount_untaxed",
        "minimum_unit_amount",
        "minimum_unit_weight",
        "total_weight",
        "line_qty",
    )
    def _compute_purchase_ok(self):
        for order in self:
            if not order.line_qty:
                order.purchase_ok = "no_line"
            elif order.amount_untaxed == 0.0:
                order.purchase_ok = "null_amount"
            elif (
                order.minimum_unit_amount
                and order.minimum_unit_amount > order.amount_untaxed
            ):
                order.purchase_ok = "no_minimum_amount"
            elif (
                order.minimum_unit_weight
                and order.minimum_unit_weight > order.total_weight
            ):
                order.purchase_ok = "no_minimum_weight"
            else:
                order.purchase_ok = "ok"

    @api.depends("grouped_order_id", "customer_id")
    def _compute_name(self):
        for order in self:
            order.name = "{}-{}".format(
                order.grouped_order_id.name,
                order.customer_id.joint_buying_company_id.code,
            )

    def _compute_is_mine_customer(self):
        current_partner = self.env.user.company_id.joint_buying_partner_id
        for order in self:
            order.is_mine_customer = order.customer_id == current_partner

    def _search_is_mine_customer(self, operator, value):
        current_partner = self.env.user.company_id.joint_buying_partner_id
        if (operator == "=" and value) or (operator == "!=" and not value):
            search_operator = "in"
        else:
            search_operator = "not in"
        return [
            (
                "id",
                search_operator,
                self.search([("customer_id", "=", current_partner.id)]).ids,
            )
        ]

    def _compute_is_mine_supplier(self):
        current_partner = self.env.user.company_id.joint_buying_partner_id
        for order in self:
            order.is_mine_supplier = order.supplier_id == current_partner

    def _search_is_mine_supplier(self, operator, value):
        current_partner = self.env.user.company_id.joint_buying_partner_id
        if (operator == "=" and value) or (operator == "!=" and not value):
            search_operator = "in"
        else:
            search_operator = "not in"
        return [
            (
                "id",
                search_operator,
                self.search([("supplier_id", "=", current_partner.id)]).ids,
            )
        ]

    def _compute_is_mine_pivot(self):
        current_company = self.env.user.company_id
        for order in self:
            order.is_mine_pivot = order.pivot_company_id == current_company

    def _search_is_mine_pivot(self, operator, value):
        current_company = self.env.user.company_id
        if (operator == "=" and value) or (operator == "!=" and not value):
            search_operator = "in"
        else:
            search_operator = "not in"
        return [
            (
                "id",
                search_operator,
                self.search([("pivot_company_id", "=", current_company.id)]).ids,
            )
        ]

    @api.depends("line_ids")
    def _compute_line_qty(self):
        for order in self:
            order.line_qty = len(order.line_ids)

    @api.depends("line_ids.amount_untaxed")
    def _compute_amount(self):
        for order in self:
            order.amount_untaxed = sum(order.mapped("line_ids.amount_untaxed"))

    @api.depends("line_ids.total_weight")
    def _compute_total_weight(self):
        for order in self:
            order.total_weight = sum(order.mapped("line_ids.total_weight"))

    # Custom Section
    @api.model
    def _prepare_order_vals(self, supplier, customer, categories):
        OrderLine = self.env["joint.buying.purchase.order.line"]
        res = {"customer_id": customer.id, "line_ids": []}
        for product in supplier._get_joint_buying_products(categories):
            vals = OrderLine._prepare_line_vals(product)
            res["line_ids"].append((0, 0, vals))
        return res

    def _hook_state_changed(self):
        # Create transport requests:
        # - if not exists,
        # - if state != closed / deposited or is not null
        # - if deposit place != customer_id
        orders_request_to_create = self.filtered(
            lambda x: (
                x.state not in ["closed", "deposited"]
                or (x.total_weight or x.amount_untaxed)
            )
            and not x.request_id
            and x.deposit_partner_id != x.customer_id
        )
        if orders_request_to_create:
            vals_list = [{"order_id": x.id} for x in orders_request_to_create]
            requests = self.env["joint.buying.transport.request"].create(vals_list)
            for (order, request) in zip(orders_request_to_create, requests):
                order.write({"request_id": request.id})

        # Unlink transport request:
        # - if exist
        # - state == closed / deposited
        # - is null (no weight and no amount untaxed)
        orders_request_to_unlink = self.filtered(
            lambda x: x.state in ["closed", "deposited"]
            and not (x.total_weight or x.amount_untaxed)
        )
        if orders_request_to_unlink:
            orders_request_to_unlink.mapped("request_id").unlink()

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._hook_state_changed()
        return orders

    def action_confirm_purchase(self):
        for order in self.filtered(lambda x: x.purchase_state == "draft"):
            if order.purchase_ok == "no_line":
                raise ValidationError(
                    _("You can not confirm an order without any lines.")
                )
            elif order.purchase_ok == "null_amount":
                raise ValidationError(
                    _("You can not confirm an order with null amount.")
                )
            elif order.purchase_ok == "no_minimum_amount":
                raise ValidationError(
                    _(
                        "You cannot confirm an order for which you have"
                        " not reached the minimum purchase amount."
                    )
                )
            elif order.purchase_ok == "no_minimum_weight":
                raise ValidationError(
                    _(
                        "You cannot confirm an order for which you have"
                        " not reached the minimum weight."
                    )
                )
            order.purchase_state = "done"

    def action_draft_purchase(self):
        for order in self.filtered(lambda x: x.purchase_state != "draft"):
            order.purchase_state = "draft"

    def action_skip_purchase(self):
        for order in self.filtered(lambda x: x.purchase_state == "draft"):
            order.purchase_state = "skipped"

    def button_see_order(self):
        self.ensure_one()
        form = self.env.ref(
            "joint_buying_product.view_joint_buying_purchase_order_form"
        )
        action = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_all"
        ).read()[0]
        action.update({"res_id": self.id, "views": [(form.id, "form")]})
        return action

    def button_reopen_order(self):
        self.write({"purchase_state": "draft"})

    def correct_purchase_state(self):
        for order in self.filtered(lambda x: x.purchase_state == "draft"):
            if order.grouped_order_id.state in ["closed", "deposited"]:
                if order.amount_untaxed == 0:
                    order.action_skip_purchase()
                else:
                    try:
                        order.action_confirm_purchase()
                    except ValidationError:
                        pass

    @api.multi
    def button_see_request(self):
        self.ensure_one()
        xml_action = "joint_buying_product.action_joint_buying_transport_request"
        xml_view = "joint_buying_product.view_joint_buying_transport_request_form"
        action = self.env.ref(xml_action).read()[0]
        action["views"] = [(self.env.ref(xml_view).id, "form")]
        action["res_id"] = self.request_id.id
        return action

    @api.multi
    def get_url_purchase_order(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        action_id = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_to_place_my"
        ).id
        menu_id = self.env.ref("joint_buying_base.menu_root").id
        return (
            "{base_url}/web?"
            "#id={id}"
            "&action={action_id}"
            "&model=joint.buying.purchase.order"
            "&view_type=form"
            "&menu_id={menu_id}".format(
                base_url=base_url,
                id=self.id,
                action_id=action_id,
                menu_id=menu_id,
            )
        )
