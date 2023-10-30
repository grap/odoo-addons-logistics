# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime, timedelta

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # Configure Correctly 'Durable Storage' Field
    # Custom GRAP
    company_domain = [("code", "=", "LSE")]
    partner_domain = [("name", "ilike", "Triandines")]

    partners = (
        env["res.company"].search(company_domain).mapped("joint_buying_partner_id")
    )
    partners |= (
        env["res.partner"].with_context(joint_buying=True).search(partner_domain)
    )

    _logger.info(
        f"Mark {len(partners)} partners as Durable Storage :"
        f"{' --- '.join([x.name for x in partners])}..."
    )
    partners.write({"joint_buying_is_durable_storage": True})

    # Create Transport Requests for recent joint buying purchase orders
    min_deposit_date = datetime.today() + timedelta(
        days=-env["joint.buying.wizard.find.route"]._MAX_TRANSPORT_DURATION
    )
    orders = (
        env["joint.buying.purchase.order.grouped"]
        .search([("deposit_date", ">", min_deposit_date.strftime("%Y-%m-%d %H:%M"))])
        .mapped("order_ids")
    )
    _logger.info(
        f"generate transport requests for {len(orders)} joint buying orders, if required..."
    )
    orders._hook_state_changed()

    # Compute tours for all the created transport requests
    requests = orders.mapped("transport_request_id")
    _logger.info(
        f"Computing tours for {len(requests)} transport requests, if required..."
    )

    requests.button_compute_tour()
