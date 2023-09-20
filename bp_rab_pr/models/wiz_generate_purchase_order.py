from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class bp_pr_wiz_generate_purchase_order(models.TransientModel):
    _inherit 	= 'bp_pr.wiz_generate_purchase_order'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        
        if active_model == 'bp_pr.purchase_request_line':
            purchase_request_line = self.env['bp_pr.purchase_request_line'].search([('id','in',active_ids)])
            if purchase_request_line:
                res['rab_id'] = purchase_request_line[0].rab_id.id
                if not all([row.rab_id.id == res['rab_id'] for row in purchase_request_line]):
                    raise UserError(_('Only same RAB can be processed'))
        return res
    
    def save(self):
        res = super().save()
        purchase_order = self.env['purchase.order'].search([('id','=',res['res_id'])])
        purchase_order.write({'rab_id':self.rab_id.id})
        return res

    rab_id 	= fields.Many2one('bp_rab.rab', string='RAB')