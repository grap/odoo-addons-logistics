# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "res_partner", "joint_buying_partner_id"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE res_partner
            RENAME COLUMN joint_buying_partner_id TO joint_buying_global_partner_id;
            """,
        )
