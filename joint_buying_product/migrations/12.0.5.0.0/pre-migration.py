# Copyright (C) 2024-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # Configure Correctly new 'Delivery Place' Field
    if not openupgrade.column_exists(
        env.cr, "joint_buying_purchase_order", "delivery_partner_id"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE joint_buying_purchase_order
            ADD COLUMN delivery_partner_id int;
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE joint_buying_purchase_order jbpo
            SET delivery_partner_id = jbpo.customer_id;
            """,
        )
