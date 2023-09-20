from odoo import api, fields, models


class sale_order(models.Model):
    _inherit 	= 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.rab_id = None

    rab_id 	= fields.Many2one('bp_rab.rab', string='RAB', ondelete='restrict')