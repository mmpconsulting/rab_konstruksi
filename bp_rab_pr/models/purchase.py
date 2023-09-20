from odoo import api, fields, models


class purchase_order(models.Model):
    _inherit 	= 'purchase.order'

    rab_id 	= fields.Many2one('bp_rab.rab', string='RAB', ondelete='restrict')