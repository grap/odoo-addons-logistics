# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)

from .product_product import _JOINT_BUYING_PRODUCT_CONTEXT


class JointBuyingPurchaseOrderLine(models.Model):
    _name = "joint.buying.purchase.order.line"
    _inherit = ["joint.buying.check.access.mixin"]
    _description = "Joint Buying Purchase Order"
    _order = "supplier_id, product_id"

    _check_access_can_create = True

    _sql_constraints = [
        (
            "order_product_uniq",
            "unique (order_id,product_id)",
            "You can not select the same product many times for the same Order !",
        ),
        (
            "qty_not_negative",
            "CHECK(qty >= 0)",
            "You can not set a negative quantity in the 'Purchase Quantity' field !",
        ),
    ]

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Purchase Order",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )

    supplier_id = fields.Many2one(
        related="order_id.supplier_id",
        comodel_name="res.partner",
        string="Supplier",
        readonly=True,
        index=True,
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    customer_id = fields.Many2one(
        related="order_id.customer_id",
        comodel_name="res.partner",
        string="Customer",
        readonly=True,
        index=True,
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    pivot_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Pivot Company",
        related="order_id.pivot_company_id",
        store=True,
    )

    company_code = fields.Char(
        related="order_id.customer_id.joint_buying_company_id.code",
        help="Technical field, used to display matrix"
        " with web_widget_x2many_2d_matrix module.",
    )

    sequence = fields.Integer(string="Sequence", default=10)

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain="["
        "('joint_buying_partner_id', '=', parent.supplier_id),"
        " ('purchase_ok', '=', True)"
        "]",
        required=True,
        context=_JOINT_BUYING_PRODUCT_CONTEXT,
        readonly=True,
        index=True,
    )

    local_product_id = fields.Many2one(
        comodel_name="product.product",
        compute="_compute_local_product_id",
    )

    qty = fields.Float(
        string="Purchase Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )

    uom_id = fields.Many2one(
        comodel_name="uom.uom", string="Purchase UoM", readonly=True
    )

    uom_measure_type = fields.Selection(related="uom_id.measure_type")

    product_uom_package_qty = fields.Float(
        string="Package Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        required=True,
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="UoM (of product)", readonly=True
    )

    product_uom_po_id = fields.Many2one(
        comodel_name="uom.uom", string="Supplier UoM (of product)", readonly=True
    )

    product_qty = fields.Float(
        string="Quantity (in Main UoM)",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_product_qty",
        store=True,
    )

    uom_different_description = fields.Char(
        string="Equivalent", compute="_compute_product_qty", store=True
    )

    product_weight = fields.Float(
        string="Brut Weight",
        required=True,
        readonly=True,
        digits=dp.get_precision("Stock Weight"),
    )

    price_unit = fields.Float(
        string="Unit Price",
        digits=dp.get_precision("Product Price"),
        required=True,
        readonly=True,
    )

    price_description = fields.Char(
        string="Pricing", compute="_compute_price_description", store=True
    )

    amount_untaxed = fields.Float(
        string="Total Untaxed Amount",
        compute="_compute_amount_untaxed",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    total_weight = fields.Float(
        string="Total Brut Weight", compute="_compute_total_weight", store=True
    )

    is_new = fields.Boolean(related="product_id.joint_buying_is_new")

    image = fields.Binary(related="product_id.image")

    image_small = fields.Binary(related="product_id.image_small")

    is_mine_customer = fields.Boolean(
        compute="_compute_is_mine_customer", search="_search_is_mine_customer"
    )

    is_mine_pivot = fields.Boolean(
        compute="_compute_is_mine_pivot", search="_search_is_mine_pivot"
    )

    @api.multi
    def _joint_buying_check_access(self):
        # We allow access to customer and to pivot company of the related supplier
        return len(
            self.filtered(lambda x: x.is_mine_customer or x.is_mine_pivot)
        ) == len(self)

    # Constrain section
    @api.constrains("qty", "product_uom_package_qty", "uom_id")
    def check_qty_package(self):
        ProductTemplate = self.env["product.template"]
        for line in self.filtered(lambda x: x.qty):
            if ProductTemplate._round_package_quantity(
                line.qty, line.product_uom_package_qty, False, line.uom_id
            )["warning"]:
                raise ValidationError(
                    _(
                        f"Unable to set the quantity {line.qty} {line.uom_id.name}"
                        f" for the product '{line.product_id.name}' because it doesn't"
                        f" respect the packaging"
                        f" '{line.product_uom_package_qty} {line.uom_id.name}'"
                    )
                )

    # Compute Section
    def _compute_is_mine_customer(self):
        current_partner = self.env.user.company_id.joint_buying_partner_id
        for line in self:
            line.is_mine_customer = line.customer_id == current_partner

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

    def _compute_is_mine_pivot(self):
        current_company = self.env.user.company_id
        for line in self:
            line.is_mine_pivot = line.pivot_company_id == current_company

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

    @api.depends("product_id")
    def _compute_local_product_id(self):
        for line in self:
            line.local_product_id = line.product_id.get_joint_buying_local_product_id()

    @api.depends("product_uom_id", "product_qty", "product_weight", "uom_measure_type")
    def _compute_total_weight(self):
        for line in self.filtered(lambda x: x.uom_measure_type == "unit"):
            line.total_weight = line.product_qty * line.product_weight
        for line in self.filtered(lambda x: x.uom_measure_type == "weight"):
            line.total_weight = line.product_qty

    @api.depends("uom_id", "product_uom_id.factor", "qty")
    def _compute_product_qty(self):
        for line in self.filtered(lambda x: x.uom_id == x.product_uom_id):
            line.product_qty = line.qty
            line.uom_different_description = False
        for line in self.filtered(lambda x: x.uom_id != x.product_uom_id):
            product_qty = line.uom_id._compute_quantity(
                line.qty, line.product_uom_id, rounding_method="HALF-UP"
            )
            line.product_qty = product_qty
            if product_qty:
                line.uom_different_description = _(
                    "or {} x {}".format(product_qty, line.product_uom_id.name)
                )
            else:
                line.uom_different_description = False

    @api.depends("price_unit", "product_uom_po_id")
    def _compute_price_description(self):
        for line in self:
            line.price_description = "{}€ / {}".format(
                line.price_unit, line.product_uom_po_id.name
            )

    @api.depends("uom_id", "product_uom_po_id.factor", "qty", "price_unit")
    def _compute_amount_untaxed(self):
        for line in self.filtered(lambda x: x.uom_id == x.product_uom_po_id):
            line.amount_untaxed = line.qty * line.price_unit
        for line in self.filtered(lambda x: x.uom_id != x.product_uom_po_id):
            product_uom_po_qty = line.uom_id._compute_quantity(
                line.qty, line.product_uom_po_id, rounding_method="HALF-UP"
            )
            line.amount_untaxed = product_uom_po_qty * line.price_unit

    @api.onchange("qty")
    def onchange_qty(self):
        res = {}
        ProductTemplate = self.env["product.template"]
        if self.qty:
            result = ProductTemplate._round_package_quantity(
                self.qty, self.product_uom_package_qty, False, self.uom_id
            )
            if result["warning"]:
                res["warning"] = result["warning"]
            self.qty = result["qty"]
        return res

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            self.product_uom_package_qty = False
            self.uom_id = False
            self.price_unit = 0.0
            self.qty = 0.0
            self.product_weight = 0.0
        else:
            self.product_uom_package_qty = self.product_id.uom_package_qty
            self.uom_id = self.product_id.uom_id.id
            self.product_weight = self.product_id.weight
            self.price_unit = self.product_id.lst_price

    @api.model
    def _prepare_line_vals(self, product):
        res = {
            "product_id": product.id,
            "uom_measure_type": product.uom_measure_type,
            "uom_id": product.uom_package_id.id or product.uom_po_id.id,
            "product_uom_id": product.uom_id.id,
            "product_uom_po_id": product.uom_po_id.id,
            "product_uom_package_qty": product.uom_package_qty,
            "product_weight": product.weight,
            "price_unit": product.lst_price,
            "qty": 0.0,
            "product_qty": 0.0,
            "amount_untaxed": 0.0,
            "total_weight": 0.0,
        }
        return res

    def _get_report_tour_data(self):
        self.ensure_one()
        return {
            "product_category": self.product_id._get_report_tour_category(),
            "supplier_partner": self.order_id.supplier_id,
            "description": (
                f"{self.product_id.name}"
                "<span style='color:#888;'>"
                f" ({self.qty} x {self.uom_id.name}) "
                "</span>"
            ),
        }

    def write(self, vals):
        res = super().write(vals)
        # if the related orders are closed (or deposited), and if user changed the quantity
        # lately. (for exemple, view joint.buying.wizard.update.order.grouped), we should
        # ensure that transport request are correctly created. (or deleted)
        self.mapped("order_id").filtered(
            lambda x: x.state in ["closed", "deposited"]
        )._hook_state_changed()
        return res
