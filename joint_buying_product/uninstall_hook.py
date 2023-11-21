# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def uninstall_product_db(cr):

    cr.execute(
        """
        ALTER TABLE product_template
        DROP COLUMN is_joint_buying;
    """
    )
