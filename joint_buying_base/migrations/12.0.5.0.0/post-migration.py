# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    tours = env["joint.buying.tour"].search([])
    _logger.info(
        "Initialize new start and arrival dates fields" f" for {len(tours)} tours"
    )
    tours.recompute_dates()
