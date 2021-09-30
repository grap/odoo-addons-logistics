# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from odoo.addons.base.models.res_partner import ADDRESS_FIELDS

_JOINT_BUYING_PARTNER_CONTEXT = {
    "joint_buying": 1,
    "form_view_ref": "joint_buying_base.view_res_partner_form_joint_buying",
}


class ResPartner(models.Model):
    _inherit = ["res.partner", "joint.buying.mixin", "joint.buying.check.access.mixin"]
    _name = "res.partner"

    _COMMISSION_STATE = [
        ("signed", "Signed"),
        ("rejected", "Rejected"),
        ("not_applicable", "Not Applicable"),
    ]

    _check_write_access_company_field_id = "joint_buying_pivot_company_id"

    _check_write_access_fields_no_check = ["joint_buying_is_subscribed"]

    joint_buying_subscribed_company_ids = fields.Many2many(
        string="Subscribed Companies",
        relation="res_company_res_partner_subscribed_rel",
        comodel_name="res.company",
        name="Companies with Subscription to the supplier",
        default=lambda x: x._default_joint_buying_subscribed_company_ids(),
    )

    joint_buying_is_subscribed = fields.Boolean(
        compute="_compute_joint_buying_is_subscribed",
        inverse="_inverse_joint_buying_is_subscribed",
        string="Subscribed",
    )

    joint_buying_global_partner_id = fields.Many2one(
        name="Global Partner for joint Buying",
        domain="[('is_joint_buying', '=', True)]",
        comodel_name="res.partner",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    joint_buying_company_id = fields.Many2one(
        comodel_name="res.company", name="Related Company for Joint Buyings"
    )

    joint_buying_pivot_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Pivot Company",
        help="Activity that has a commercial relationship with this supplier",
    )

    joint_buying_deposit_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Deposit Place",
        help="Place that will serve as a deposit for this supplier",
        domain="[('is_joint_buying_stage', '=', True)]",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    # TODO, rename into joint_buying_is_stage
    is_joint_buying_stage = fields.Boolean(
        string="Is Stage",
        default=False,
        help="Check this box if that address can be a step of a tour",
    )

    joint_buying_description = fields.Html(string="Complete Description")

    joint_buying_is_mine = fields.Boolean(
        compute="_compute_joint_buying_is_mine", search="_search_joint_buying_is_mine"
    )

    joint_buying_commission_state = fields.Selection(
        selection=_COMMISSION_STATE, string="Joint Buying Commission Agreement"
    )

    joint_buying_commission_rate = fields.Float(string="Joint Buying Commission Rate")

    # Onchange section
    @api.onchange("joint_buying_pivot_company_id")
    def onchange_joint_buying_pivot_company_id(self):
        if self.joint_buying_pivot_company_id:
            self.joint_buying_subscribed_company_ids |= (
                self.joint_buying_pivot_company_id
            )

    # Constraint Section
    @api.constrains("joint_buying_global_partner_id", "company_id")
    def _check_joint_buying_global_partner_id(self):
        check_partners = self.filtered(lambda x: x.joint_buying_global_partner_id)
        for partner in check_partners:
            other_partners = self.search(
                [
                    ("id", "!=", partner.id),
                    (
                        "joint_buying_global_partner_id",
                        "=",
                        partner.joint_buying_global_partner_id.id,
                    ),
                    ("company_id", "=", partner.company_id.id),
                ]
            )
            if other_partners:
                raise ValidationError(
                    _(
                        "You can not link the supplier %s to the Joint"
                        " Buying partner %s"
                        " because you have other suppliers that are still"
                        " related to him : \n\n %s"
                        % (
                            partner.name,
                            partner.joint_buying_global_partner_id.name,
                            ", ".join([x.name for x in other_partners]),
                        )
                    )
                )

    @api.constrains("is_joint_buying", "company_id")
    def _check_is_joint_buying_company_id(self):
        return super()._check_is_joint_buying_company_id()

    @api.constrains("is_joint_buying", "joint_buying_company_id", "customer")
    def _check_joint_buying_company_customer(self):
        if self.filtered(
            lambda x: x.is_joint_buying and not x.joint_buying_company_id and x.customer
        ):
            raise UserError(
                _(
                    "You can not create a customer joint buying partner."
                    " You should ask to you ERP manager to do it via"
                    " the creation of a company."
                )
            )

    # Default Section
    def _default_joint_buying_subscribed_company_ids(self):
        if self.env.context.get("joint_buying"):
            companies = self.env["res.company"].search(
                [("joint_buying_auto_subscribe", "=", True)]
            )
            return companies.ids

    # Compute Section
    def _compute_joint_buying_is_mine(self):
        current_company = self.env.user.company_id
        for partner in self:
            partner.joint_buying_is_mine = (
                partner.joint_buying_pivot_company_id == current_company
            )

    def _compute_joint_buying_is_subscribed(self):
        for partner in self.filtered(lambda x: x.is_joint_buying):
            partner.joint_buying_is_subscribed = (
                partner in self.env.user.company_id.joint_buying_subscribed_partner_ids
            )

    # Search Section
    def _search_joint_buying_is_mine(self, operator, value):
        current_company = self.env.user.company_id
        if (operator == "=" and value) or (operator == "!=" and not value):
            search_operator = "in"
        else:
            search_operator = "not in"
        return [
            (
                "id",
                search_operator,
                self.search(
                    [("joint_buying_pivot_company_id", "=", current_company.id)]
                ).ids,
            )
        ]

    # Inverse Section
    def _inverse_joint_buying_is_subscribed(self):
        partners = self.filtered(lambda x: x.joint_buying_is_subscribed)
        if partners:
            self.env.user.company_id.write(
                {"joint_buying_subscribed_partner_ids": [(4, x.id) for x in partners]}
            )
        partners = self.filtered(lambda x: not x.joint_buying_is_subscribed)
        if partners:
            self.env.user.company_id.write(
                {"joint_buying_subscribed_partner_ids": [(3, x.id) for x in partners]}
            )

    # Overload Section
    def write(self, vals):
        res = super().write(vals)
        # Do not allow to update partner that have been created
        # from companies to be updated this way
        if (
            self.filtered(lambda x: x.joint_buying_company_id)
            and not self.env.context.get("write_joint_buying_partner", False)
            and set(self._get_fields_no_writable_joint_buying_company())
            & set(vals.keys())
        ):
            raise AccessError(
                _(
                    "You can not update this partner this way"
                    " you should ask to your ERP Manager to update this field"
                    " via the related company."
                )
            )
        return res

    def unlink(self):
        if self.filtered(lambda x: x.joint_buying_company_id):
            raise AccessError(
                _(
                    "You can not delete this partner because it is related to a"
                    " company for joint Buyings. Please archive it."
                )
            )
        return super().unlink()

    # Custom section
    def toggle_joint_buying_is_subscribed(self):
        self.ensure_one()
        self.joint_buying_is_subscribed = not self.joint_buying_is_subscribed
        return True

    @api.model
    def _get_fields_no_writable_joint_buying_company(self):
        """return fields that can not be written on joint_buying companies"""
        res = list(ADDRESS_FIELDS)
        res += [
            "name",
            "is_joint_buying",
            "company_id",
            "is_company",
            "email",
            "phone",
            "mobile",
            "website",
            "vat",
        ]
        return res

    @api.multi
    def demo_geolocalize(self):
        partners = self.filtered(
            lambda x: x.street and x.city and not x.partner_latitude
        )
        partners.geo_localize()
