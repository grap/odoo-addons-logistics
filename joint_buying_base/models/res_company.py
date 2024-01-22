# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import ADDRESS_FIELDS

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class ResCompany(models.Model):
    _inherit = "res.company"

    joint_buying_subscribed_partner_ids = fields.Many2many(
        relation="res_company_res_partner_subscribed_rel",
        comodel_name="res.partner",
        name="Suppliers with subscription",
    )

    joint_buying_auto_subscribe = fields.Boolean(
        string="Automatic Supplier Subscription",
        default=False,
        help="Check this box if you want to subscribe automatically"
        " to new suppliers.",
    )

    joint_buying_partner_id = fields.Many2one(
        comodel_name="res.partner",
        name="Related Partner for Joint Buyings",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        readonly=True,
    )

    is_joint_buying_customer = fields.Boolean(
        related="joint_buying_partner_id.customer",
        string="Is a Customer",
        readonly=False,
        store=True,
    )

    is_joint_buying_supplier = fields.Boolean(
        related="joint_buying_partner_id.supplier",
        string="Is a Vendor",
        readonly=False,
        store=True,
    )

    joint_buying_is_durable_storage = fields.Boolean(
        related="joint_buying_partner_id.joint_buying_is_durable_storage",
        string="Durable Storage",
        readonly=False,
        store=True,
    )

    def _get_company_fields_for_joint_buying_partner(self):
        """Return the company fields that raise the update
        of the related joint buying partner"""
        return ADDRESS_FIELDS + (
            "name",
            "active",
            "email",
            "phone",
            "website",
            "partner_latitude",
            "partner_longitude",
            "logo",
            "vat",
            "is_joint_buying_supplier",
        )

    def _prepare_joint_buying_partner_vals(self):
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()
        group_name = icp.get_param("joint_buying_base.group_name", "")
        suffix = group_name and ("(" + group_name + ")") or ""
        sanitized_name = self.name.replace("|", "").strip()
        vals = {
            "name": f"{sanitized_name} {suffix}",
            "active": self.active,
            "is_joint_buying": True,
            "is_joint_buying_stage": True,
            "joint_buying_company_id": self.id,
            "company_id": False,
            "is_company": True,
            "joint_buying_pivot_company_id": self.id,
            "email": self.email,
            "phone": self.phone,
            "website": self.website,
            "partner_latitude": self.partner_latitude,
            "partner_longitude": self.partner_longitude,
            "vat": self.vat,
            "image": self.logo,
        }
        for field_name in ADDRESS_FIELDS:
            value = getattr(self, field_name)
            value = value.id if isinstance(value, models.BaseModel) else value
            vals[field_name] = value
        return vals

    @api.model
    def create(self, vals):
        ResPartner = self.env["res.partner"]
        res = super().create(vals)
        partner_vals = res._prepare_joint_buying_partner_vals()
        # Handle relate fields, that are not correctly initialized
        # at the creation.
        if "is_joint_buying_customer" in vals:
            partner_vals["customer"] = vals.get("is_joint_buying_customer")
        if "is_joint_buying_supplier" in vals:
            partner_vals["supplier"] = vals.get("is_joint_buying_supplier")
            partner_vals["joint_buying_subscribed_company_ids"] = [
                (
                    6,
                    False,
                    ResPartner.with_context(
                        joint_buying=True
                    )._default_joint_buying_subscribed_company_ids(),
                )
            ]
        if "joint_buying_is_durable_storage" in vals:
            partner_vals["joint_buying_is_durable_storage"] = vals.get(
                "joint_buying_is_durable_storage"
            )

        res.joint_buying_partner_id = ResPartner.with_context(
            write_joint_buying_partner=True, no_check_joint_buying=True
        ).create(partner_vals)
        return res

    @api.multi
    def write(self, vals):
        ResPartner = self.env["res.partner"]
        # Technical Note: we add context key here
        # to avoid error when recomputing related / computed values
        res = super(
            ResCompany,
            self.with_context(
                write_joint_buying_partner=True, no_check_joint_buying=True
            ),
        ).write(vals)
        partner_fields = self._get_company_fields_for_joint_buying_partner()
        if list(set(vals.keys()) & set(partner_fields)):
            extra_vals = {}
            if vals.get("is_joint_buying_supplier", False):
                extra_vals.update(
                    {
                        "joint_buying_subscribed_company_ids": [
                            (
                                6,
                                False,
                                ResPartner.with_context(
                                    joint_buying=True
                                )._default_joint_buying_subscribed_company_ids(),
                            )
                        ]
                    }
                )
            self.update_joint_buying_partners(extra_vals=extra_vals)
        return res

    def geo_localize(self):
        """overload the function to update partner_latitude and
        partner_longitude that are related fields"""
        res = super().geo_localize()
        self.update_joint_buying_partners()
        return res

    @api.multi
    def update_joint_buying_partners(self, extra_vals=False):
        extra_vals = extra_vals or {}
        for company in self:
            extra_vals.update(company._prepare_joint_buying_partner_vals())
            company.joint_buying_partner_id.with_context(
                write_joint_buying_partner=True
            ).write(extra_vals)
