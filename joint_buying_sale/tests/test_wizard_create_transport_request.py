# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestWizardCreateTransportRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.sale_order = self.env.ref("joint_buying_sale.sale_order_2")
        self.company_VEV = self.env.ref("joint_buying_base.company_VEV")
        self.company_CRB = self.env.ref("joint_buying_base.company_CRB")
        self.product_gingembrettes = self.env.ref(
            "joint_buying_product.product_ELD_gingembrettes"
        )
        self.product_orangettes = self.env.ref(
            "joint_buying_product.product_ELD_orangettes"
        )
        self.Wizard = self.env["joint.buying.create.transport.request.wizard"]

    def test_create_transport_request_from_sale_order(self):
        # Set 0 as weight of the product
        self.product_gingembrettes.weight = 0
        self.product_orangettes.weight = 0

        wizard = self.Wizard.with_context(active_id=self.sale_order.id).create(
            {
                "availability_date": datetime.now(),
                "start_partner_id": self.company_VEV.joint_buying_partner_id.id,
                "destination_partner_id": self.company_CRB.joint_buying_partner_id.id,
            }
        )

        self.assertEqual(len(wizard.product_ids), 2)

        # should fail, because weight are not set
        with self.assertRaises(UserError):
            wizard.create_transport_request()

        # Should success, if product has correct weight
        self.product_gingembrettes.weight = 0.250
        self.product_orangettes.weight = 0.300
        wizard.create_transport_request()

        # Should create a request
        request = self.sale_order.joint_buying_transport_request_id
        self.assertTrue(request)

        # Should fail, because a request exists
        with self.assertRaises(UserError):
            wizard.create_transport_request()

        # Should sucess if request has been deleted
        request.unlink()
        wizard.create_transport_request()
