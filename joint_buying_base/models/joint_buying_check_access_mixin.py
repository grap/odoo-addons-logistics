# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import AccessError


class JointBuyingCheckAccessMixin(models.AbstractModel):
    _name = "joint.buying.check.access.mixin"
    _description = "Joint Buying Check Access Mixin"

    _check_access_can_create = False

    _check_access_can_unlink = False

    _check_access_company_field_id = False

    _check_access_write_fields_no_check = []

    @api.multi
    def _joint_buying_check_access(self):
        """Overload this function in each model
        Should return False if the access if forbidden
        """
        raise NotImplementedError()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if self.env.context.get("no_check_joint_buying", False):
            # explicitely ignore the check, if asked
            return res

        if self.env.user.has_group("joint_buying_base.group_joint_buying_manager"):
            # A manager has no contrains
            return res

        if "is_joint_buying" in self._fields and not res.is_joint_buying:
            # if it's a mixed model (global / local) like product and partner
            # and if we are in a local context, no check.
            return res

        if not self._check_access_can_create:
            raise AccessError(
                _("You can not create this item. Please ask to the logistic Manager.")
            )

        if not res._joint_buying_check_access():
            raise AccessError(
                _(
                    "You can not create this item because"
                    " you are not responsible for it"
                )
            )
        return res

    @api.multi
    def write(self, vals):
        if self.env.context.get("no_check_joint_buying", False):
            # explicitely ignore the check, if asked
            return super().write(vals)

        if self.env.user.has_group("joint_buying_base.group_joint_buying_manager"):
            # A manager has no contrains
            return super().write(vals)

        if not (set(vals.keys()) - set(self._check_access_write_fields_no_check)):
            # Updated fields are all unprotected
            return super().write(vals)

        # Filter on joint buying items
        if "is_joint_buying" in self._fields:
            items = self.filtered(lambda x: x.is_joint_buying)
        else:
            items = self

        if not items._joint_buying_check_access():
            raise AccessError(
                _(
                    "You can not update this item because"
                    " you are not responsible for it"
                )
            )
        return super().write(vals)

    @api.multi
    def unlink(self):
        if self.env.context.get("no_check_joint_buying", False):
            # explicitely ignore the check, if asked
            return super().unlink()

        if self.env.user.has_group("joint_buying_base.group_joint_buying_manager"):
            # A manager has no contrains
            return super().unlink()

        # Filter on joint buying items
        if "is_joint_buying" in self._fields:
            items = self.filtered(lambda x: x.is_joint_buying)
        else:
            items = self

        if not items:
            return super().unlink()

        if not self._check_access_can_unlink:
            raise AccessError(
                _("You can not unlink the items. Please ask to the logistic Manager.")
            )

        if not items._joint_buying_check_access():
            raise AccessError(
                _(
                    "You can not unlink this item because"
                    " you are not responsible for it"
                )
            )

        return super().unlink()
