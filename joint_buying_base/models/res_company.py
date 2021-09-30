# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

from odoo.addons.base.models.res_partner import ADDRESS_FIELDS
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


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

    def _prepare_joint_buying_partner_vals(self):
        self.ensure_one()
        sanitized_name = self.name.replace("|", "")
        vals = {
            "name": _("{} (Joint Buyings)").format(sanitized_name),
            "is_joint_buying": True,
            "is_joint_buying_stage": True,
            "joint_buying_company_id": self.id,
            "company_id": False,
            "is_company": True,
            "joint_buying_pivot_company_id": self.id,
            "email": self.email,
            "phone": self.phone,
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
        res.joint_buying_partner_id = ResPartner.with_context(
            write_joint_buying_partner=True, no_check_joint_buying=True
        ).create(res._prepare_joint_buying_partner_vals())
        return res

    def write(self, vals):
        # Technical Note: we add context key here
        # to avoid error when recomputing related / computed values
        res = super(
            ResCompany,
            self.with_context(
                write_joint_buying_partner=True, no_check_joint_buying=True
            ),
        ).write(vals)
        for company in self:
            partner_vals = company._prepare_joint_buying_partner_vals()
            if list(set(vals.keys()) & set(partner_vals)):
                company.joint_buying_partner_id.with_context(
                    write_joint_buying_partner=True
                ).write(partner_vals)
        return res

    @api.multi
    def demo_geolocalize(self):
        self.mapped("joint_buying_partner_id").demo_geolocalize()
