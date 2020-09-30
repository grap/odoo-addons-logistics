# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class GlobalMixin(models.AbstractModel):
    _name = "global.mixin"
    _description = "Global Mixin"

    is_global = fields.Boolean(
        compute="_compute_is_global", string="Is Global", store=True
    )

    @api.depends("company_id")
    def _compute_is_global(self):
        for item in self:
            item.is_global = item.company_id.id is False

    # Overload the private _search function, that is used by the other ORM functions
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
        args += [("is_global", "=", bool(self.env.context.get("only_global", False)))]
        return super()._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
