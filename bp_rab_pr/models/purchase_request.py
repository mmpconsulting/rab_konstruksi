from odoo import api, fields, models


class bp_pr_purchase_request(models.Model):
    _inherit    = 'bp_pr.purchase_request'

    rab_id 	    = fields.Many2one('bp_rab.rab', string='RAB', ondelete='restrict')

class bp_pr_purchase_request_line(models.Model):
    _inherit 	= 'bp_pr.purchase_request_line'

    rab_id 	    = fields.Many2one('bp_rab.rab', string='RAB', related='purchase_request_id.rab_id', store=True)