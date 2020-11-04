import logging
from datetime import datetime

from odoo.tests import common

logging.basicConfig(level=logging.DEBUG)


class TestGenerateTours(common.TransactionCase):
    def setUp(self):
        super().setUp()

    def test_basic_case(self):
        """
        Create three joint_buying suppliers:
            - init_period_date : today
            - period : 15
            - delay : 10
        Create two joint_buying customers
        Create one tour template :
            - init period date : today
            - period : 15
            - deadline : 20

        In this case, the start date of each suppliers
        is the same that the tour template and the same period.
        Suppliers are sync with the tour template configuration.

        So the generate_tour method must generate one tour with four
        joint_buying_purchase.
        """

        supplier_1 = self.env.ref(
            "joint_buying_base.res_partner_for_joint_buying_supplier_in_grap"
        )
        supplier_2 = self.env.ref(
            "joint_buying_base.res_partner_for_joint_buying_pivot_activity"
        )
        supplier_3 = self.env.ref(
            "joint_buying_base.res_partner_for_joint_buying_supplier_out_grap"
        )
        customer_1 = self.env.ref(
            "joint_buying_base.res_partner_for_joint_buying_customer_1"
        )
        customer_2 = self.env.ref(
            "joint_buying_base.res_partner_for_joint_buying_customer_2"
        )

        tour_template = self.env["joint.buying.tour.template"].create(
            {
                "name": "tour_template",
                "deadline": 13,
                "period": 14,
                "init_period_date": datetime.today().date(),
            }
        )
        self.assertEqual(len(tour_template.tour_ids), 0)

        tour_template.generate_tour()

        self.assertEqual(len(tour_template.tour_ids), 1)
        self.assertEqual(len(tour_template.tour_ids[0].joint_buying_purchase_ids), 6)
        self.assertIn(
            tour_template.tour_ids[0].joint_buying_purchase_ids[0].supplier_id.id,
            [supplier_1.id, supplier_2.id, supplier_3.id],
        )
        self.assertIn(
            tour_template.tour_ids[0].joint_buying_purchase_ids[1].customer_id.id,
            [customer_1.id, customer_2.id],
        )
