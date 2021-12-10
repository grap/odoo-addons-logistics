# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_product_db(cr):

    # Add product_product.is_joint_buying
    cr.execute(
        """
        ALTER TABLE product_product
        ADD COLUMN is_joint_buying boolean;
        UPDATE product_product set is_joint_buying = false;
    """
    )

    # Add product_template.is_joint_buying
    cr.execute(
        """
        ALTER TABLE product_template
        ADD COLUMN is_joint_buying boolean;
        UPDATE product_template set is_joint_buying = false;
    """
    )

    # Add product_supplierinfo.joint_buying_partner_id
    cr.execute(
        """
        ALTER TABLE product_supplierinfo
        ADD COLUMN joint_buying_partner_id integer;
    """
    )
