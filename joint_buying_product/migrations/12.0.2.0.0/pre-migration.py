# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    "res_partner": [
        ("joint_buying_frequency", None),
        ("joint_buying_next_start_date", None),
        ("joint_buying_next_end_date", None),
        ("joint_buying_next_deposit_date", None),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
