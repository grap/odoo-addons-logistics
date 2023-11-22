# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def uninstall_product_db(cr, registry):
    # # Display joint buying product in generic category
    # # before deleting it.
    # cr.execute("""
    #     UPDATE product_template
    #     SET categ_id = (
    #         SELECT res_id
    #         FROM ir_model_data
    #         WHERE module = 'product'
    #         AND name = 'product_category_all'
    #     )
    #     WHERE categ_id = (
    #         SELECT res_id
    #         FROM ir_model_data
    #         WHERE module = 'joint_buying_product'
    #         AND name = 'product_category'
    #     );
    #     """)
    cr.execute(
        """
        ALTER TABLE product_template
        DROP COLUMN is_joint_buying;
    """
    )
