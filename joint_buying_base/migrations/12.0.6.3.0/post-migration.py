import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    ResCompany = env["res.company"].with_context(active_test=False)
    companies = ResCompany.search([])
    for company in companies:
        partner = company.joint_buying_partner_id.with_context(
            write_joint_buying_partner=True
        )
        new_name = company._prepare_joint_buying_partner_vals()["name"]
        _logger.info(f"Rename {partner.name} into {new_name} ...")
        partner.name = new_name
