# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.local_orangette = self.env.ref(
            "joint_buying_product.product_ELD_orangettes"
        )
        self.label = self.env.ref("product_label.label_agriculture_biologique")
        self.global_orangette = self.local_orangette.joint_buying_product_id

    def test_01_propagate(self):
        self.assertEqual(len(self.global_orangette.label_ids), 0)

        self.local_orangette.write({"label_ids": [(6, 0, [self.label.id])]})
        self.local_orangette.update_joint_buying_product()
        self.assertEqual(len(self.global_orangette.label_ids), 1)
