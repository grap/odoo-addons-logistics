# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "joint_buying_tour", "date_tour"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE joint_buying_tour
            RENAME COLUMN date_tour TO start_date;
            """,
        )

    if not openupgrade.column_exists(env.cr, "joint_buying_tour", "end_date"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE joint_buying_tour
            ADD COLUMN end_date TIMESTAMP;
            """,
        )

        openupgrade.logged_query(
            env.cr,
            """
            UPDATE joint_buying_tour
            SET end_date = start_date + interval '4 hour'
            """,
        )
