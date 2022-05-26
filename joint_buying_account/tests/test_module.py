# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_vat_incl = self.env.ref(
            "joint_buying_account.product_ELD_ecureuil"
        )
        self.product_vat_excl = self.env.ref("joint_buying_account.product_ELD_hibou")
        self.pricelist_ELD = self.env.ref("joint_buying_product.pricelist_10_percent")
        self.company_ELD = self.env.ref("joint_buying_base.company_ELD")
        self.currency_ELD = self.company_ELD.currency_id

    def test_01_create_global_product_without_pricelist_vat_excl(self):
        global_product_vat_excl = self.product_vat_excl.create_joint_buying_product()

        self.assertEqual(
            self.currency_ELD.round(global_product_vat_excl.lst_price),
            self.currency_ELD.round(self.product_vat_excl.lst_price),
            "Global Product (from product vat excl) should has price vat excl.",
        )

    def test_02_create_global_product_without_pricelist_vat_incl(self):
        global_product_vat_incl = self.product_vat_incl.create_joint_buying_product()

        self.assertEqual(
            self.currency_ELD.round(global_product_vat_incl.lst_price),
            self.currency_ELD.round(self.product_vat_incl.lst_price / 1.2),
            "Global Product (from product vat incl) should has price vat incl.",
        )

    def test_11_create_global_product_with_pricelist_vat_excl(self):
        self.company_ELD.joint_buying_pricelist_id = self.pricelist_ELD

        global_product_vat_excl = self.product_vat_excl.create_joint_buying_product()

        self.assertEqual(
            self.currency_ELD.round(global_product_vat_excl.lst_price),
            self.currency_ELD.round(self.product_vat_excl.lst_price * 0.9),
            "Global Product (from product vat excl) should has price vat excl."
            " (regression regarding pricelist feature)",
        )

    def test_12_create_global_product_with_pricelist_vat_incl(self):
        self.company_ELD.joint_buying_pricelist_id = self.pricelist_ELD

        global_product_vat_incl = self.product_vat_incl.create_joint_buying_product()

        self.assertEqual(
            self.currency_ELD.round(global_product_vat_incl.lst_price),
            self.currency_ELD.round(self.product_vat_incl.lst_price / 1.2 * 0.9),
            "Global Product (from product vat incl) should has price vat incl."
            " (regression regarding pricelist feature)",
        )

    # def test_02_create_global_product_with_pricelist(self):
    #     self.company_ELD.joint_buying_pricelist_id = self.pricelist_ELD

    #     # Test product vat incl
    #     global_product_vat_incl = self.product_vat_incl.create_joint_buying_product()

    #     self.assertEqual(
    #         global_product_vat_incl.lst_price,
    #         self.product_vat_incl.lst_price / 1.2 * 0.9,
    #         "Global Product (from product vat incl) should has price vat excl."
    #         " (regression regarding pricelist feature)",
    #     )

    #     # Test product vat incl
    #     global_product_vat_excl = self.product_vat_incl.create_joint_buying_product()

    #     self.assertEqual(
    #         global_product_vat_excl.lst_price,
    #         self.product_vat_excl.lst_price * 0.9,
    #         "Global Product (from product vat excl) should has price vat excl."
    #         " (regression regarding pricelist feature)",
    #     )
