import logging
from datetime import datetime

from odoo.tests import common

logging.basicConfig(level=logging.DEBUG)


class TestGenerateTours(common.TransactionCase):
    def setUp(self):
        super().setUp()

    def basic_case(self):
        """
        Create two joint_buying suppliers:
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

        logging.debug("TOTOTOTOTOTO")
        supplier_1 = self.env["res.partner"].create(
            {
                "company_id": False,
                "is_joint_buying": True,
                "is_joint_buying_supplier": True,
                "is_company": True,
                "supplier": True,
                "name": "supplier_1",
                "delay": 10,
                "period": 15,
                "init_period_date": datetime.today().date(),
            }
        )
        supplier_2 = self.env["res.partner"].create(
            {
                "company_id": False,
                "is_joint_buying": True,
                "is_joint_buying_supplier": True,
                "is_company": True,
                "supplier": True,
                "name": "supplier_2",
                "delay": 10,
                "period": 15,
                "init_period_date": datetime.today().date(),
            }
        )
        customer_1 = self.env["res.partner"].create(
            {
                "company_id": False,
                "is_joint_buying": True,
                "is_joint_buying_customer": True,
                "is_company": True,
                "name": "customer_1",
            }
        )
        customer_2 = self.env["res.partner"].create(
            {
                "company_id": False,
                "is_joint_buying": True,
                "is_joint_buying_customer": True,
                "is_company": True,
                "name": "customer_2",
            }
        )

        tour_template = self.env["joint.buying.tour.template"].create(
            {
                "name": "tour_template",
                "deadline": 10,
                "period": 15,
                "init_period_date": datetime.today().date(),
            }
        )

        tour_template.generate_tour()
        self.assertEqual(len(tour_template.tour_ids), 1)
        self.assertEqual(len(tour_template.tour_ids[0].joint_buying_purchase_ids), 4)
        self.assertIn(
            tour_template.tour_ids[0].joint_buying_purchase_ids[0].supplier_id.id,
            [supplier_1.id, supplier_2.id],
        )
        self.assertIn(
            tour_template.tour_ids[0].joint_buying_purchase_ids[1].customer_id.id,
            [customer_1.id, customer_2.id],
        )
