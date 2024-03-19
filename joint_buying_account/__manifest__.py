# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Joint Buying - Account",
    "version": "12.0.1.1.0",
    "category": "GRAP - Logistics",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-logistics",
    "license": "AGPL-3",
    "depends": [
        "account",
        # GRAP
        "joint_buying_product",
    ],
    "demo": [
        "demo/account_account.xml",
        "demo/account_journal.xml",
        "demo/account_tax.xml",
        "demo/product_product.xml",
        "demo/res_company.xml",
        "demo/ir_property.xml",
    ],
    "data": [
        "wizards/view_joint_buying_invoice_commission_wizard.xml",
        "views/view_res_config_settings.xml",
        "views/view_joint_buying_purchase_order_grouped.xml",
    ],
    "installable": True,
    "auto_install": True,
}
