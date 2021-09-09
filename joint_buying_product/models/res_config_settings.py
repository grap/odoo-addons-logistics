# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    end_date_near_day = fields.Integer(
        string="Number of Day 'Near'",
        help="number of days below which the end of the order is near",
    )

    end_date_imminent_day = fields.Integer(
        string="Number of Day 'Imminent'",
        help="number of days below which the end of the order is imminent",
    )
