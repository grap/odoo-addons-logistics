# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


@openupgrade.migrate()
def migrate(env, version):
    tables = [
        "joint_buying_wizard_set_tour_line",
        "joint_buying_wizard_set_tour",
        "joint_buying_tour_line",
        "joint_buying_tour",
        "joint_buying_carrier",
    ]
    for table in tables:
        openupgrade.logged_query(env.cr, "TRUNCATE TABLE %s CASCADE;", (AsIs(table),))

    openupgrade.logged_query(
        env.cr, "DELETE FROM mail_followers WHERE res_model = 'joint.buying.tour';"
    )
