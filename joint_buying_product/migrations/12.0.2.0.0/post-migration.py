# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            INSERT INTO joint_buying_frequency (
                partner_id,
                create_date,
                create_uid,
                write_date,
                write_uid,
                frequency,
                next_start_date,
                next_end_date,
                next_deposit_date,
                deposit_partner_id
            )
            SELECT
            id as partner_id,
            create_date,
            create_uid,
            write_date,
            write_uid,
            openupgrade_legacy_12_0_joint_buying_frequency,
            openupgrade_legacy_12_0_joint_buying_next_start_date,
            openupgrade_legacy_12_0_joint_buying_next_end_date,
            openupgrade_legacy_12_0_joint_buying_next_deposit_date,
            openupgrade_legacy_12_0_joint_buying_deposit_partner_id
            FROM res_partner
            WHERE openupgrade_legacy_12_0_joint_buying_frequency != 0;
        """,
    )
