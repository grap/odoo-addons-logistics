# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Sale",
    "version": "12.0.1.1.5",
    "category": "GRAP - Logistics",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-logistics",
    "license": "AGPL-3",
    "depends": [
        "sale",
        # GRAP
        "joint_buying_product",
    ],
    "data": [
        "wizards/view_joint_buying_create_sale_order_wizard.xml",
        "views/view_joint_buying_purchase_order.xml",
        "views/view_joint_buying_purchase_order_grouped.xml",
    ],
    "installable": True,
    "auto_install": True,
}
