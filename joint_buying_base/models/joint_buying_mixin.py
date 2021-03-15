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

    @api.model
    def _join_buying_mixin_add_domain(self, domain):
        return domain + [
            ("is_joint_buying", "=", bool(self.env.context.get("joint_buying", False)))
        ]

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if self._name == "res.partner":
            print("joint_buying_base::search")
        domain = self._join_buying_mixin_add_domain(domain)
        return super().search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
        )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._name == "res.partner":
            print("joint_buying_base::name_search")
        args = self._join_buying_mixin_add_domain(args)
        return super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )





    # # Overload the private _search function:
    # # This function is used by the other ORM functions
    # # (name_search, search_read)
    # @api.model
    # def _search(
    #     self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None
    # ):
    #     if self._name == "res.partner":
    #         print("joint_buying_base::_search")
    #     args += [
    #         ("is_joint_buying", "=", bool(self.env.context.get("joint_buying", False)))
    #     ]
    #     return super()._search(
    #         args,
    #         offset=offset,
    #         limit=limit,
    #         order=order,
    #         count=count,
    #         access_rights_uid=access_rights_uid,
    #     )

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     if self._name == "res.partner":
    #         print("joint_buying_base::name_search")
    #     return super().name_search(
    #         name=name, args=args, operator=operator, limit=limit
    #     )

    # @api.model
    # def _name_search(
    #     self, name='', args=None, operator='ilike', limit=100, name_get_uid=None
    # ):
    #     # Overload also _name_search
    #     # because res.partner._name_search doesn't call super in all
    #     # cases. (so doesn't call _search)
    #     if self._name == "res.partner":
    #         print("joint_buying_base::_name_search")
    #     args += [
    #         ("is_joint_buying", "=", bool(self.env.context.get("joint_buying", False)))
    #     ]
    #     return super()._name_search(
    #         name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
    #     )
