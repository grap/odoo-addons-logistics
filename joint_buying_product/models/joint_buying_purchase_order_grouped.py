# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingPurchaseOrderGrouped(models.Model):
    _name = "joint.buying.purchase.order.grouped"
    _description = "Joint Buying Grouped Order"
    _inherit = ["joint.buying.check.access.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "end_date desc, supplier_id"

    _check_access_can_create = True

    _STATE_SELECTION = [
        ("futur", "Futur"),
        ("in_progress", "In Progress"),
        ("in_progress_near", "In Progress (Near Closing Date)"),
        ("in_progress_imminent", "In Progress (Imminent Closing Date)"),
        ("closed", "Closed"),
        ("deposited", "Deposited Products"),
    ]

    _PURCHASE_OK_SELECTION = [
        ("no_order", "No Orders"),
        ("no_minimum_amount", "Minimum Amount Not reached"),
        ("no_minimum_weight", "Minimum Weight Not reached"),
        ("null_amount", "Null Amount"),
        ("ok", "OK"),
    ]

    name = fields.Char(
        string="Number", required=True, copy=False, default=lambda x: x._default_name()
    )

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=True,
        domain="[('supplier', '=', True)]",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    supplier_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Related company of the supplier",
        help="Odoo Company related to the supplier (if any)",
        related="supplier_id.joint_buying_company_id",
    )

    supplier_comment = fields.Text(related="supplier_id.comment")

    state = fields.Selection(
        index=True,
        selection=_STATE_SELECTION,
        string="State",
        readonly=True,
        track_visibility=True,
    )

    purchase_ok = fields.Selection(
        selection=_PURCHASE_OK_SELECTION, compute="_compute_purchase_ok", store=True
    )

    pivot_company_id = fields.Many2one(
        comodel_name="res.company", string="Pivot Company", required=True
    )

    deposit_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Deposit Partner",
        required=True,
        domain="[('is_joint_buying_stage', '=', True)]",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    start_date = fields.Datetime(index=True, string="Start Date", required=True)

    end_date = fields.Datetime(index=True, string="End Date", required=True)

    deposit_date = fields.Datetime(index=True, string="Deposit Date", required=True)

    order_ids = fields.One2many(
        "joint.buying.purchase.order", inverse_name="grouped_order_id", readonly=True
    )

    order_qty = fields.Integer(
        string="Orders Quantity", compute="_compute_order_qty", store=True
    )

    category_ids = fields.Many2many(
        string="Order Categories", comodel_name="joint.buying.category"
    )

    entry_rate_description = fields.Char(
        string="Entry Rate", compute="_compute_entry_rate_description", store=True
    )

    is_mail_sent = fields.Boolean(string="Mail Sent", default=False)

    minimum_amount = fields.Float(string="Minimum Amount")

    minimum_unit_amount = fields.Float(string="Minimum Unit Amount")

    minimum_weight = fields.Float(string="Minimum Weight")

    minimum_unit_weight = fields.Float(string="Minimum Unit Weight")

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

    summary_line_ids = fields.One2many(
        comodel_name="joint.buying.purchase.order.grouped.line",
        compute="_compute_summary_line_ids",
    )

    current_order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order", compute="_compute_current_order_id"
    )

    is_mine_pivot = fields.Boolean(
        compute="_compute_is_mine_pivot", search="_search_is_mine_pivot"
    )

    @api.multi
    def _joint_buying_check_access(self):
        return set(self.mapped("pivot_company_id").ids) == {self.env.user.company_id.id}

    # Constraint Section
    @api.constrains("start_date", "end_date", "deposit_date")
    def _check_dates(self):
        if self.filtered(
            lambda x: x.start_date >= x.end_date or x.end_date >= x.deposit_date
        ):
            raise ValidationError(
                _(
                    "Incorrect setting:\n\n"
                    " * start date should be less than end date\n"
                    " * end date should be less that deposit date"
                )
            )

    # Default Section
    def _default_name(self):
        return self.env["ir.sequence"].next_by_code(
            "joint.buying.purchase.order.grouped"
        )

    # Compute Section
    @api.depends(
        "amount_untaxed",
        "minimum_amount",
        "minimum_weight",
        "total_weight",
        "order_qty",
    )
    def _compute_purchase_ok(self):
        for grouped_order in self:
            if not grouped_order.order_qty:
                grouped_order.purchase_ok = "no_order"
            elif grouped_order.amount_untaxed == 0.0:
                grouped_order.purchase_ok = "null_amount"
            elif (
                grouped_order.minimum_amount
                and grouped_order.minimum_amount > grouped_order.amount_untaxed
            ):
                grouped_order.purchase_ok = "no_minimum_amount"
            elif (
                grouped_order.minimum_weight
                and grouped_order.minimum_weight > grouped_order.total_weight
            ):
                grouped_order.purchase_ok = "no_minimum_weight"
            else:
                grouped_order.purchase_ok = "ok"

    @api.depends("order_ids")
    def _compute_order_qty(self):
        for grouped_order in self:
            grouped_order.order_qty = len(grouped_order.order_ids)

    @api.depends("order_ids.purchase_ok", "order_qty")
    def _compute_entry_rate_description(self):
        for grouped_order in self:
            grouped_order.entry_rate_description = "%d / %d" % (
                len(
                    [
                        x
                        for x in grouped_order.order_ids.mapped("purchase_ok")
                        if x != "null_amount"
                    ]
                ),
                grouped_order.order_qty,
            )

    @api.depends("order_ids.amount_untaxed")
    def _compute_amount(self):
        for grouped_order in self:
            grouped_order.amount_untaxed = sum(
                grouped_order.mapped("order_ids.amount_untaxed")
            )

    @api.depends("order_ids.total_weight")
    def _compute_total_weight(self):
        for grouped_order in self:
            grouped_order.total_weight = sum(
                grouped_order.mapped("order_ids.total_weight")
            )

    def _compute_is_mine_pivot(self):
        current_company = self.env.user.company_id
        for grouped_order in self:
            grouped_order.is_mine_pivot = (
                grouped_order.pivot_company_id == current_company
            )

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

    # On the Fly Compute Section
    def _compute_summary_line_ids(self):
        def _get_keys(line):
            return tuple(
                [
                    line.product_id.id,
                    line.uom_id.id,
                    line.product_weight,
                    line.price_unit,
                ]
            )

        for grouped_order in self:
            res = {}
            lines = grouped_order.mapped("order_ids.line_ids").filtered(lambda x: x.qty)
            for line in lines:
                key = _get_keys(line)
                if key not in res:
                    res[key] = {
                        "product_id": line.product_id.id,
                        "uom_id": line.uom_id.id,
                        "product_weight": line.product_weight,
                        "product_uom_package_qty": 0.0,
                        "price_unit": line.price_unit,
                        "qty": 0.0,
                        "amount_untaxed": 0.0,
                    }
                res[key].update(
                    {
                        "product_uom_package_qty": res[key]["product_uom_package_qty"]
                        + line.product_uom_package_qty,
                        "qty": res[key]["qty"] + line.qty,
                        "amount_untaxed": res[key]["amount_untaxed"]
                        + line.amount_untaxed,
                    }
                )
            grouped_order.summary_line_ids = [(0, 0, v) for k, v in res.items()]

    def _compute_current_order_id(self):
        for grouped_order in self:
            grouped_order.current_order_id = grouped_order.order_ids.filtered(
                lambda x: x.is_mine_customer
            )

    # Overload Section
    @api.model
    def create(self, vals):
        grouped_order = super().create(vals)
        grouped_order.update_state_value()
        return grouped_order

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("update_state_value"):
            self.update_state_value()
        return res

    @api.multi
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get("mark_as_sent"):
            self.write({"is_mail_sent": True})
        return super(
            JointBuyingPurchaseOrderGrouped,
            self.with_context(mail_post_autofollow=True),
        ).message_post(**kwargs)

    # Custom Section
    @api.model
    def cron_check_state(self):
        self.update_state_value(check_all=True)

    @api.model
    def cron_create_purchase_order_grouped(self):
        now = fields.datetime.now()
        frequencies = self.env["joint.buying.frequency"].search(
            [("frequency", "!=", 0), ("next_start_date", "<", now)]
        )
        for frequency in frequencies.filtered(lambda x: x.partner_id.active):
            # Create Grouped order
            wizard = (
                self.env["joint.buying.wizard.create.order"]
                .with_context(active_id=frequency.partner_id.id)
                .create(frequency._prepare_wizard_values())
            )
            wizard.create_order_grouped()

            # Add frequency to all dates
            vals = {}
            delta = timedelta(days=frequency.frequency)
            for field in ["next_start_date", "next_end_date", "next_deposit_date"]:
                vals[field] = getattr(frequency, field) + delta
            frequency.write(vals)

    @api.multi
    def update_state_value(self, check_all=False):
        end_date_near_day = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("joint_buying_product.end_date_near_day")
        )
        end_date_imminent_day = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("joint_buying_product.end_date_imminent_day")
        )
        now = datetime.now()
        right_settings = {
            "futur": [("start_date", ">", now)],
            "in_progress": [
                ("start_date", "<=", now),
                ("end_date", ">", now + timedelta(days=end_date_near_day)),
            ],
            "in_progress_near": [
                ("start_date", "<=", now),
                ("end_date", "<=", now + timedelta(days=end_date_near_day)),
                ("end_date", ">", now + timedelta(days=end_date_imminent_day)),
            ],
            "in_progress_imminent": [
                ("start_date", "<=", now),
                ("end_date", "<=", now + timedelta(days=end_date_imminent_day)),
                ("end_date", ">", now),
            ],
            "closed": [("end_date", "<=", now), ("deposit_date", ">", now)],
            "deposited": [("deposit_date", "<", now)],
        }
        for correct_state, domain in right_settings.items():
            domain = expression.AND(
                [domain, ["|", ("state", "!=", correct_state), ("state", "=", False)]]
            )
            if not check_all:
                domain = expression.AND([domain, [("id", "in", self.ids)]])
            grouped_orders = self.search(domain)
            for grouped_order in grouped_orders:
                previous_state = grouped_order.state or ""
                grouped_order.with_context(update_state_value=True).write(
                    {"state": correct_state}
                )
                if correct_state == "closed":
                    grouped_order.mapped("order_ids").correct_purchase_state()

                # Send email to pivot company if required
                grouped_order.send_mail_to_pivot_company(previous_state)

    @api.multi
    def send_mail_to_pivot_company(self, previous_state):
        """
        Send an email to the pivot company if the current state and the previous state
        require to send an email, and if the pivot company want to receive email,
        depending on it configuration.
        """
        self.ensure_one()
        # Send 'In Progress' mail (if it was not in progress before)
        if (
            self.state.startswith("in_progress")
            and not previous_state.startswith("in_progress")
            and self.pivot_company_id.joint_buying_send_pivot_email_in_progress
        ):
            template = self.env.ref(
                "joint_buying_product.email_template_pivot_company_in_progress"
            )
            template.send_mail(self.id, force_send=True)

        # Send 'Closed' mail (if it was not deposited before)
        # (rare case where pivot company change date manually)
        if (
            self.state == "closed"
            and previous_state != "deposited"
            and self.pivot_company_id.joint_buying_send_pivot_email_closed
        ):
            template = self.env.ref(
                "joint_buying_product.email_template_pivot_company_closed"
            )
            template.send_mail(self.id, force_send=True)

    @api.multi
    def update_product_list(self):
        OrderLine = self.env["joint.buying.purchase.order.line"]

        for grouped_order in self:
            products = grouped_order.supplier_id._get_joint_buying_products(
                categories=grouped_order.category_ids
            )
            lines_vals = [OrderLine._prepare_line_vals(x) for x in products]

            product_ids = [x["product_id"] for x in lines_vals]
            for order in grouped_order.order_ids:
                # First remove product that should not be sold
                to_remove_lines = order.line_ids.filtered(
                    lambda x: x.product_id.id not in product_ids
                )
                to_remove_lines.unlink()

                for line_vals in lines_vals:
                    line = order.line_ids.filtered(
                        lambda x: x.product_id.id == line_vals["product_id"]
                    )
                    if line:
                        # Update the line
                        current_vals = {
                            k: v
                            for k, v in line_vals.items()
                            if k
                            not in [
                                "qty",
                                "product_qty",
                                "amount_untaxed",
                                "total_weight",
                            ]
                        }
                        # TODO, for the time being, it is rewriting all the values
                        # maybe we could check if the value changed
                        # before calling the write
                        line.write(current_vals)
                    else:
                        # create a new line
                        order.write({"line_ids": [(0, 0, line_vals)]})

    @api.model
    def _prepare_order_grouped_vals(
        self,
        supplier,
        customers,
        start_date,
        end_date,
        deposit_date,
        pivot_company,
        deposit_partner,
        minimum_amount,
        minimum_unit_amount,
        minimum_weight,
        minimum_unit_weight,
        categories,
    ):
        Order = self.env["joint.buying.purchase.order"]
        vals = {
            "supplier_id": supplier.id,
            "deposit_partner_id": deposit_partner.id,
            "pivot_company_id": pivot_company.id,
            "start_date": start_date,
            "end_date": end_date,
            "deposit_date": deposit_date,
            "minimum_amount": minimum_amount,
            "minimum_unit_amount": minimum_unit_amount,
            "minimum_weight": minimum_weight,
            "minimum_unit_weight": minimum_unit_weight,
            "order_ids": [],
            "category_ids": [(6, 0, categories.ids)],
        }
        if not customers:
            customers = supplier.mapped(
                "joint_buying_subscribed_company_ids.joint_buying_partner_id"
            )
        for customer in customers:
            vals["order_ids"].append(
                (0, 0, Order._prepare_order_vals(supplier, customer, categories))
            )
        return vals

    @api.multi
    def action_send_email_for_supplier(self):
        self.ensure_one()
        IrModelData = self.env["ir.model.data"]
        template_id = IrModelData.get_object_reference(
            "joint_buying_product", "email_template_purchase_order_grouped_for_supplier"
        )[1]
        compose_form_id = IrModelData.get_object_reference(
            "mail", "email_compose_message_wizard_form"
        )[1]
        ctx = dict(self.env.context) or {}
        ctx.update(
            {
                "model_description": _("Grouped Order"),
                "default_model": "joint.buying.purchase.order.grouped",
                "default_res_id": self.ids[0],
                "default_use_template": True,
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "force_email": True,
                "mark_as_sent": True,
            }
        )

        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    def action_send_email_for_pivot_in_progress(self):
        return self._action_send_email_for_pivot(
            "email_template_pivot_company_in_progress"
        )

    def action_send_email_for_pivot_closed(self):
        return self._action_send_email_for_pivot("email_template_pivot_company_closed")

    def _action_send_email_for_pivot(self, email_template):
        self.ensure_one()
        IrModelData = self.env["ir.model.data"]
        template_id = IrModelData.get_object_reference(
            "joint_buying_product", email_template
        )[1]
        compose_form_id = IrModelData.get_object_reference(
            "mail", "email_compose_message_wizard_form"
        )[1]
        ctx = dict(self.env.context) or {}
        ctx.update(
            {
                "model_description": _("Grouped Order"),
                "default_model": "joint.buying.purchase.order.grouped",
                "default_res_id": self.ids[0],
                "default_use_template": True,
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "force_email": True,
            }
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    def see_current_order(self):
        result = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_to_place_my"
        ).read()[0]
        form_view = self.env.ref(
            "joint_buying_product.view_joint_buying_purchase_order_form"
        ).id
        order_ids = self.mapped("current_order_id").ids
        if len(order_ids) == 1:
            result.update({"views": [(form_view, "form")], "res_id": order_ids[0]})
        else:
            result["domain"] = "[('id','in',%s)]" % (order_ids)
        result["context"] = {
            "form_view_initial_mode": "edit",
            "force_detailed_view": "true",
        }
        return result

    def create_current_order(self):
        self.ensure_one()
        # Create order
        Order = self.env["joint.buying.purchase.order"]
        current_customer_partner = self.env.user.company_id.joint_buying_partner_id

        vals = Order._prepare_order_vals(
            self.supplier_id, current_customer_partner, categories=self.category_ids
        )
        vals.update({"grouped_order_id": self.id})
        Order.create(vals)

        # Subscribe the current company to the supplier if not set
        current_company_ids = self.supplier_id.joint_buying_subscribed_company_ids.ids
        if self.env.user.company_id.id not in current_company_ids:
            self.supplier_id.with_context(
                no_check_joint_buying=True
            ).joint_buying_subscribed_company_ids = current_company_ids + [
                self.env.user.company_id.id
            ]
            # Display a message for the user
            self.env.user.notify_info(
                message=_(
                    "The company '%s' has been subscribed to the supplier '%s'."
                    % (self.env.user.company_id.complete_name, self.supplier_id.name)
                )
            )

        return self.see_current_order()

    @api.multi
    def get_url(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        action_id = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_grouped_my"
        ).id
        menu_id = self.env.ref("joint_buying_base.menu_root").id
        return (
            "{base_url}/web?"
            "#id={grouped_order_id}"
            "&action={action_id}"
            "&model=joint.buying.purchase.order.grouped"
            "&view_type=form"
            "&menu_id={menu_id}".format(
                base_url=base_url,
                grouped_order_id=self.id,
                action_id=action_id,
                menu_id=menu_id,
            )
        )
