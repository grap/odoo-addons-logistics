# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # set company website on related joint buying partners
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner rp
        SET website = rp2.website
        FROM res_company rc, res_partner rp2
        WHERE rc.joint_buying_partner_id = rp.id
        AND rc.partner_id = rp2.id
        AND rp.website is null
        AND rp2 is not null;
        """,
    )
