# Copyright (C) 2020-Today: HASHBANG (https://hashbang.coop)
# @author: HAshbang (https://twitter.com/HashBangCoop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Purchase",
    "summary": "A module that allows activities to make grouped orders.",
    "version": "12.0.1.0.2",
    "category": "GRAP - Logistics",
    "author": "GRAP, Hashbang",
    "website": "https://hashbang.coop",
    "license": "AGPL-3",
    "depends": [
        "web_one2many_kanban",
        "web_tree_dynamic_colored_field",
        "purchase",
        "joint_buying_product",
    ],
    "data": [
        "data/ir_module_category_data.xml",
        "security/joint_buying_purchase_security.xml",
        "security/ir.model.access.csv",
        "views/view_res_partner.xml",
        "views/view_joint_buying_tour_template.xml",
        "views/view_joint_buying_tour.xml",
        "views/view_joint_buying_purchase_order.xml",
        "views/view_product_template.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/joint_buying_tour_template.xml",
        "demo/joint_buying_tour.xml",
        "demo/joint_buying_purchase_order.xml",
        "demo/joint_buying_purchase_order_line.xml",
        "demo/res_user.xml",
        "demo/res_partner.xml",
    ],
    "installable": True,
}
