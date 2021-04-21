# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from odoo.addons.base.models.res_partner import ADDRESS_FIELDS


class ResPartner(models.Model):
    _inherit = ["res.partner", "joint.buying.mixin"]
    _name = "res.partner"

    joint_buying_favorite_company_ids = fields.Many2many(
        relation="res_company_res_partner_favorite_rel",
        comodel_name="res.company",
        name="Favorite Companies for Joint Buyings",
    )

    is_favorite = fields.Boolean(
        compute="_compute_is_favorite",
        inverse="_inverse_is_favorite",
        string="Is Favorite Vendor",
    )

    joint_buying_partner_id = fields.Many2one(
        name="Global Partner for joint Buying",
        domain="[('is_joint_buying', '=', True), ('supplier', '=', True)]",
        comodel_name="res.partner",
    )

    joint_buying_company_id = fields.Many2one(
        comodel_name="res.company", name="Related Company for Joint Buyings"
    )

    joint_buying_pivot_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Pivot Company",
        help="Activity that has a commercial relationship with this supplier",
    )

    joint_buying_deposit_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Deposit Company",
        help="Activity that will serve as a deposit for this supplier",
    )

    @api.constrains("joint_buying_partner_id", "company_id")
    def _check_joint_buying_partner_id(self):
        check_partners = self.filtered(lambda x: x.joint_buying_partner_id)
        for partner in check_partners:
            other_partners = self.search(
                [
                    ("id", "!=", partner.id),
                    (
                        "joint_buying_partner_id",
                        "=",
                        partner.joint_buying_partner_id.id,
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
                            partner.joint_buying_partner_id.name,
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

    def _compute_is_favorite(self):
        for partner in self.filtered(lambda x: x.is_joint_buying):
            partner.is_favorite = (
                partner in self.env.user.company_id.joint_buying_favorite_partner_ids
            )

    def _inverse_is_favorite(self):
        partners = self.filtered(lambda x: x.is_favorite)
        if partners:
            self.env.user.company_id.write(
                {"joint_buying_favorite_partner_ids": [(4, x.id) for x in partners]}
            )
        partners = self.filtered(lambda x: not x.is_favorite)
        if partners:
            self.env.user.company_id.write(
                {"joint_buying_favorite_partner_ids": [(3, x.id) for x in partners]}
            )

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

    @api.model
    def _get_fields_no_writable_joint_buying_company(self):
        """return fields that can not be written on joint_buying companies"""

        res = list(ADDRESS_FIELDS)
        res += ["name", "is_joint_buying", "company_id", "is_company", "email", "phone"]
        return res

    # delay = fields.Integer(
    #     default=0, string="Timeframes for preparations before order."
    # )
    # period = fields.Integer(default=0, string="Period between each order")
    # init_period_date = fields.Date(
    #     string="Initial date to start the periods between each order."
    # )
