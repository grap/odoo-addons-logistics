# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Products",
    "version": "12.0.1.0.2",
    "category": "GRAP - Logistics",
    "author": "GRAP",
    "website": "http://www.grap.coop",
    "license": "AGPL-3",
    "depends": ["product", "joint_buying_base"],
    "data": [
        "views/view_product_product.xml",
        "views/view_product_template.xml",
        "views/view_product_supplier_info.xml",
    ],
    "demo": ["demo/product_product.xml"],
    "installable": True,
    "auto_install": True,
}
