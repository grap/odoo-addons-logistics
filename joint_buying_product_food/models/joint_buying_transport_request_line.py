# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class JointBuyingTransportRequestLine(models.Model):
    _inherit = "joint.buying.transport.request.line"

    # def get_report_information(self):
    #     self.ensure_one()
    #     res = super().get_report_information()
    #     if self.request_id.order_id:
    #         return {
    #             "normal": [
    #                 x for x in filter(lambda x: x[0].storage_method, res["all"])
    #             ],
    #             "cool": [
    #                 x
    #                 for x in filter(lambda x: x[0].storage_method == "cool", res["all"])
    #             ],
    #             "frozen": [
    #                 x
    #                 for x in filter(
    #                     lambda x: x[0].storage_method == "frozen", res["all"]
    #                 )
    #             ],
    #         }
    #     return res
