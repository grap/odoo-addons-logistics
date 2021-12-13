# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE joint_buying_purchase_order_line
        ADD COLUMN product_name varchar;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE joint_buying_purchase_order_line jbpol
        SET product_name = pt.name
        FROM product_product pp,
            product_template pt
        WHERE jbpol.product_id = pp.id
        AND pp.product_tmpl_id = pt.id
        AND pp.default_code is null;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE joint_buying_purchase_order_line jbpol
        SET product_name = '[' || pp.default_code || ']' || pt.name
        FROM product_product pp,
            product_template pt
        WHERE jbpol.product_id = pp.id
        AND pp.product_tmpl_id = pt.id
        AND pp.default_code is not null;
        """,
    )
