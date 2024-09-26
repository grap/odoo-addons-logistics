# Copyright (C) 2024-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    JointBuyingOrder = env["joint.buying.purchase.order"]

    # Get null orders deposited or closed
    # that still have a transport request related
    openupgrade.logged_query(
        env.cr,
        """
        SELECT po.id
        FROM joint_buying_transport_request tr
        INNER JOIN joint_buying_purchase_order po
            ON po.id = tr.order_id
        WHERE po.state IN ('deposited', 'closed')
        AND po.amount_untaxed = 0.0;
        """,
    )

    order_ids = [x[0] for x in env.cr.fetchall()]

    _logger.info(f"Unlink Transport Requests for orders {order_ids} ...")
    JointBuyingOrder.browse(order_ids)._hook_state_changed()

    # Get NOT null recent orders
    # that don't have a transport request related
    openupgrade.logged_query(
        env.cr,
        """
    SELECT
        po.id,
        po.create_date,
        po.state,
        po.amount_untaxed
    FROM joint_buying_purchase_order po
    WHERE po.id not in (
        SELECT order_id from joint_buying_transport_request
        WHERE order_id is not null
    )
    AND po.deposit_partner_id != po.delivery_partner_id
    AND po.amount_untaxed > 0.0 AND po.deposit_date > '2024-01-01';
    """,
    )

    order_ids = [x[0] for x in env.cr.fetchall()]

    _logger.info(f"Create Transport Requests for orders {order_ids} ...")
    JointBuyingOrder.browse(order_ids)._hook_state_changed()
