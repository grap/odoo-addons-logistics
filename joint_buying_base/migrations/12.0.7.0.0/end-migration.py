import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    TransportRequest = env["joint.buying.transport.request"]
    requests = TransportRequest.search([])
    _logger.info(f"Recompute Supplier field for {len(requests)} transport requests ...")
    requests._compute_supplier_id()
    _logger.info(f"Recompute Request Type for {len(requests)} transport requests ...")
    requests._compute_request_type()
