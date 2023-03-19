# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Product Labels",
    "version": "12.0.1.0.1",
    "category": "GRAP - Logistics",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-logistics",
    "license": "AGPL-3",
    "depends": [
        # GRAP
        "joint_buying_product",
        "product_label",
    ],
    "data": [
        "views/view_res_partner.xml",
        "views/view_product_product.xml",
        "views/view_joint_buying_purchase_order.xml",
    ],
    "installable": True,
    "auto_install": True,
}
