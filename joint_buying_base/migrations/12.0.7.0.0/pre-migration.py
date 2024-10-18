# Copyright (C) 2024-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info(
        "Fix bad computation of joint_buying_transport_request.start_date field."
    )
    openupgrade.logged_query(
        env.cr,
        """
    UPDATE joint_buying_transport_request tr_main
    SET start_date = tmp.min_start_date
    FROM (
        SELECT tr.id as transport_request_id,
        min(tl.start_date) as min_start_date
        FROM joint_buying_transport_request tr
        INNER JOIN joint_buying_transport_request_line trl
            ON trl.request_id = tr.id
        INNER JOIN joint_buying_tour_line tl
            ON tl.id = trl.tour_line_id
        WHERE tr.state = 'computed'
        GROUP BY tr.id
    ) as tmp
    WHERE
        tr_main.id = tmp.transport_request_id
        AND tr_main.start_date != tmp.min_start_date;
    """,
    )
