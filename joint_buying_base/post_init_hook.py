# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import SUPERUSER_ID, api


def _create_joint_buying_partner_for_companies(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env["res.company"].with_context(active_test=False).search([])

    for company in companies:
        if not company.joint_buying_partner_id:
            vals = company._prepare_joint_buying_partner_vals()
            vals.update({"customer": False, "supplier": False})
            if company._fields.get("active"):
                vals.update({"active": company.active})
            company.joint_buying_partner_id = env["res.partner"].create(vals)
