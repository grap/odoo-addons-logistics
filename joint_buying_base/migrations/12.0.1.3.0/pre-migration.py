# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # transform deposit company into partner deposit
    # (joint_buying_deposit_company_id --> joint_buying_deposit_partner_id)
    if openupgrade.column_exists(
        env.cr, "res_partner", "joint_buying_deposit_company_id"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE res_partner
            RENAME COLUMN joint_buying_deposit_company_id
            TO joint_buying_deposit_company_id__obsolete;
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE res_partner
            ADD COLUMN joint_buying_deposit_partner_id int;
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE res_partner rp
            SET joint_buying_deposit_partner_id = rc.joint_buying_partner_id
            FROM res_company rc
            WHERE rp.joint_buying_deposit_company_id__obsolete = rc.id;
            """,
        )

        # Flag partners as stage if not done
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE res_partner
            SET is_joint_buying_stage = true
            WHERE id in (
                SELECT joint_buying_deposit_partner_id FROM res_partner)
            AND is_joint_buying_stage is false;
            """,
        )

        # set to false, due to change of the default value
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE res_company
            SET joint_buying_auto_subscribe = false;
            """,
        )
