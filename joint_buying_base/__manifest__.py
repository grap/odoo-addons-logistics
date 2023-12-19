# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Base",
    "version": "12.0.5.0.4",
    "category": "GRAP - Logistics",
    "author": "GRAP,La Jardinière,Hashbang",
    "website": "https://github.com/grap/odoo-addons-logistics",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "web",
        "decimal_precision",
        # OCA
        "base_geolocalize_company",
        "res_company_code",
        "res_company_active",
        "web_notify",
        "web_view_leaflet_map_partner",
        "web_widget_bokeh_chart",
        # GRAP
        "name_search_reset_res_partner",
    ],
    "external_dependencies": {
        "python": ["openupgradelib", "geopy", "bokeh", "pandas", "treelib"]
    },
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "views/menu.xml",
        "views/view_res_company.xml",
        "views/view_res_partner.xml",
        "views/view_res_partner_category.xml",
        "views/view_res_users.xml",
        "views/view_res_config_settings.xml",
        "views/view_joint_buying_carrier.xml",
        "views/view_joint_buying_tour_type.xml",
        "views/view_joint_buying_tour.xml",
        "views/view_joint_buying_tour_line.xml",
        "views/view_joint_buying_transport_request.xml",
        "views/view_joint_buying_transport_request_line.xml",
        "wizards/view_joint_buying_wizard_set_tour.xml",
        "wizards/joint_buying_wizard_find_route.xml",
        "reports/report_joint_buying_tour.xml",
        "reports/report.xml",
        "views/templates.xml",
    ],
    "demo": [
        "demo/res_company.xml",
        "demo/res_users.xml",
        "demo/res_partner_category.xml",
        "demo/res_partner.xml",
        "demo/joint_buying_carrier.xml",
        "demo/joint_buying_tour_type.xml",
        "demo/joint_buying_tour.xml",
        "demo/joint_buying_transport_request.xml",
    ],
    "post_init_hook": "_create_joint_buying_partner_for_companies",
    "installable": True,
}
