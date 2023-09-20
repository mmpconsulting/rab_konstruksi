from odoo import api, fields, models


class purchase_order_line(models.Model):
    _inherit 	= 'purchase.order.line'

    purchase_request_line_id 	= fields.Many2one('bp_pr.purchase_request_line', string='Purchase Request Line', ondelete='restrict')