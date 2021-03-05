# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class JointBuyingMixin(models.AbstractModel):
    _name = "joint.buying.mixin"
    _description = "Joint Buying Mixin"

    is_joint_buying = fields.Boolean(
        string="For Joint Buyings",
        readonly=True,
        index=True,
        default=lambda x: x._default_is_joint_buying(),
    )

    def _default_is_joint_buying(self):
        return bool(self.env.context.get("joint_buying", False))

    def _check_is_joint_buying_company_id(self):
        """Technical note, you should call with @api.constrains
        and super() this function in your overloaded model,
        due to the fact that the field company_id is not present
        in all model.
        """
        for item in self:
            if item.is_joint_buying and item.company_id:
                raise ValidationError(
                    _(
                        "You can not create an item for 'joint buying'"
                        " that has a company field defined."
                    )
                )

    # Overload Create function:
    # In a joint buying context
    # the system will create joint buying object.
    @api.model
    def create(self, vals):
        if "joint_buying" not in vals.keys():
            if bool(self.env.context.get("joint_buying", False)):
                vals.update({"joint_buying": True, "company_id": False})
        return super().create(vals)

    # Overload the private _search function:
    # This function is used by the other ORM functions
    # (name_search, search_read)
    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        args += [
            ("is_joint_buying", "=", bool(self.env.context.get("joint_buying", False)))
        ]
        return super()._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
