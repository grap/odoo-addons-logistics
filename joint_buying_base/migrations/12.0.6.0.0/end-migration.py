import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    TransportRequest = env["joint.buying.transport.request"]
    requests = TransportRequest.search([])
    _logger.info(f"Recompute Origin field for {len(requests)} transport requests ...")
    requests._compute_origin()
    _logger.info(f"Recompute Tours for {len(requests)} transport requests ...")
    requests.button_compute_tour()
