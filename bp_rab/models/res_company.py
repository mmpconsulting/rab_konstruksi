from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    project_product_id = fields.Many2one('product.product', string='Default Project Product',domain=[('type', '=', 'service')])

    