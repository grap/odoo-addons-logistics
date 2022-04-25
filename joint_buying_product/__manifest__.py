# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Products",
    "version": "12.0.2.0.2",
    "category": "GRAP - Logistics",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-logistics",
    "license": "AGPL-3",
    "depends": [
        "product",
        # OCA
        "product_uom_measure_type",
        "web_notify",
        "web_tree_image_tooltip",
        "web_widget_x2many_2d_matrix",
        # GRAP
        "joint_buying_base",
        "product_uom_package",
    ],
    "pre_init_hook": "pre_init_product_db",
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "wizards/joint_buying_wizard_create_order.xml",
        "wizards/joint_buying_wizard_update_order_grouped.xml",
        "views/view_res_config_settings.xml",
        "views/view_product_template.xml",
        "views/view_product_product.xml",
        "views/view_product_supplier_info.xml",
        "views/view_res_users.xml",
        "views/view_joint_buying_purchase_order_grouped.xml",
        "views/view_joint_buying_purchase_order.xml",
        "views/view_res_partner.xml",
        "reports/report_template.xml",
        "reports/report.xml",
        "data/ir_cron.xml",
        "data/ir_config_parameter.xml",
        "data/product_category.xml",
        "data/ir_sequence.xml",
        "data/mail_template.xml",
    ],
    "demo": [
        "demo/joint_buying_category.xml",
        "demo/product_pricelist.xml",
        "demo/res_groups.xml",
        "demo/uom_uom.xml",
        "demo/product_product.xml",
        "demo/res_partner.xml",
        "demo/joint_buying_frequency.xml",
    ],
    "installable": True,
}
