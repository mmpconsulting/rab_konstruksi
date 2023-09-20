from odoo import api, fields, models

class stock_scrap(models.Model):
    _inherit = 'stock.scrap'

    rab_id 	= fields.Many2one('bp_rab.rab', string='RAB', ondelete='restrict')
    