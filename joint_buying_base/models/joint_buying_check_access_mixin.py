# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import AccessError


class JointBuyingCheckAccessMixin(models.AbstractModel):
    _name = "joint.buying.check.access.mixin"
    _description = "Joint Buying Check Access Mixin"

    _check_write_access_company_field_id = False

    _check_write_access_fields_no_check = []

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if not self.env.user.has_group(
            "joint_buying_base.group_joint_buying_manager"
        ) and not self.env.context.get("no_check_joint_buying", False):
            if (
                ("is_joint_buying" not in self._fields or res.is_joint_buying)
                and res.mapped(self._check_write_access_company_field_id)
                != self.env.user.company_id
            ):
                raise AccessError(
                    _(
                        "You can not create this item because"
                        " you are not responsible for it"
                    )
                )
        return res

    @api.multi
    def write(self, vals):
        to_check_fields = [
            x
            for x in list(vals.keys())
            if x not in self._check_write_access_fields_no_check
        ]
        if (
            not self.env.user.has_group("joint_buying_base.group_joint_buying_manager")
            and not self.env.context.get("no_check_joint_buying", False)
            and to_check_fields
        ):
            if "is_joint_buying" in self._fields:
                items = self.filtered(lambda x: x.is_joint_buying)
            else:
                items = self
            for item in items:
                if (
                    item.mapped(self._check_write_access_company_field_id)
                    != self.env.user.company_id
                ):
                    raise AccessError(
                        _(
                            "You can not update this item because"
                            " you are not responsible for it"
                        )
                    )
        return super().write(vals)

    @api.multi
    def unlink(self):
        if not self.env.user.has_group(
            "joint_buying_base.group_joint_buying_manager"
        ) and not self.env.context.get("no_check_joint_buying", False):
            if "is_joint_buying" in self._fields:
                items = self.filtered(lambda x: x.is_joint_buying)
            else:
                items = self
            for item in items:
                if (
                    item.mapped(self._check_write_access_company_field_id)
                    != self.env.user.company_id
                ):
                    raise AccessError(
                        _(
                            "You can not unlink this item because"
                            " you are not responsible for it"
                        )
                    )
        return super().unlink()
