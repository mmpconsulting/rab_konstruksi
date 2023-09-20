from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    project_product_id = fields.Many2one(related='company_id.project_product_id', readonly=False)

