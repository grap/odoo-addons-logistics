# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info(
        "Drop start_hour and arrival_hour column in joint_buying_tour_line"
        " as there are now computed on the fly"
    )

    env.cr.execute("ALTER TABLE joint_buying_tour_line DROP COLUMN start_hour;")
    env.cr.execute("ALTER TABLE joint_buying_tour_line DROP COLUMN arrival_hour;")
