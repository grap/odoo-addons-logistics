# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Base",
    "version": "12.0.1.1.7",
    "category": "GRAP - Logistics",
    "author": "GRAP,La Jardinière,Hashbang",
    "website": "https://github.com/grap/odoo-addons-logistics/",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "name_search_reset_res_partner",
        "res_company_code",
        "base_geolocalize_openstreetmap",
    ],
    "external_dependencies": {"python": ["openupgradelib", "geopy"]},
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/menu.xml",
        "views/view_res_company.xml",
        "views/view_res_partner.xml",
        "views/view_res_partner_category.xml",
        "views/view_res_users.xml",
        "views/view_res_config_settings.xml",
        "views/view_joint_buying_tour.xml",
        "wizards/view_joint_buying_wizard_set_tour.xml",
    ],
    "demo": [
        "demo/res_company.xml",
        "demo/res_users.xml",
        "demo/res_partner_category.xml",
        "demo/res_partner.xml",
        "demo/joint_buying_tour.xml",
    ],
    "post_init_hook": "_create_joint_buying_partner_for_companies",
    "installable": True,
}
