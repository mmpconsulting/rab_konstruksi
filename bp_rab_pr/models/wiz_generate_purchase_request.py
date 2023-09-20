from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class bp_rab_pr_wiz_generate_purchase_request(models.TransientModel):
    _name 	= 'bp_rab_pr.wiz_generate_purchase_request'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        wizard_line_ids = []
        
        if active_model == 'bp_rab_pr.v_rab_product':
            v_rab_product = self.env['bp_rab_pr.v_rab_product'].search([('id','in',active_ids)])
        else:
            v_rab_product = self.env['bp_rab_pr.v_rab_product'].search([('rab_id','in',active_ids)])

        if v_rab_product:
            res['rab_id'] = v_rab_product[0].rab_id.id
            if not all([row.state == 'rab' for row in v_rab_product]):
                raise UserError(_('Only RAB state can be processed'))
            elif not all([row.rab_id.id == res['rab_id'] for row in v_rab_product]):
                raise UserError(_('Only same RAB can be processed'))
            else:
                for i in v_rab_product:
                    wizard_line_ids.append((0, 0, {
                        'name': i.product_id.name,
                        'product_id': i.product_id.id,
                        'uom_id': i.product_id.uom_id.id,
                        'qty_rab': i.qty_rab,
                        'qty_request': i.qty_rab,
                        'rab_product_id': i.rab_product_id.id,
                        }))

        if not wizard_line_ids:
            return res
        res['wiz_generate_purchase_request_line_ids'] = wizard_line_ids
        return res

    def save(self):
        if len(self.wiz_generate_purchase_request_line_ids) > 0:
            purchase_request = self.env['bp_pr.purchase_request'].create({
                'user_request_id' : self.user_request_id.id, 
                'date_request' : self.date_request,
                'rab_id' : self.rab_id.id
                })
            for i in self.wiz_generate_purchase_request_line_ids:
                if i.qty_request > 0:
                    self.env['bp_pr.purchase_request_line'].create({
                        'name' : i.name,
                        'product_id' : i.product_id.id,
                        'uom_id' : i.product_id.uom_id.id,
                        'qty_request' : i.qty_request,
                        'purchase_request_id' : purchase_request.id,
                        })

            return {
                'res_id': purchase_request.id,
                'name': _('Purchase Request'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'bp_pr.purchase_request',
                'view_id': False,
                'context': False,
                'type': 'ir.actions.act_window'}
        
        return True

    rab_id 	            = fields.Many2one('bp_rab.rab', string='RAB', required=True, ondelete='cascade')
    date_request 	    = fields.Date(string='Request Date', default=fields.Datetime.now)
    user_request_id 	= fields.Many2one('res.users', string='Request by', default=lambda self: self.env.user.id, required=True)
    wiz_generate_purchase_request_line_ids 	= fields.One2many('bp_rab_pr.wiz_generate_purchase_request_line', 'wiz_generate_purchase_request_id', string='Purchase Request Line')

class bp_rab_pr_wiz_generate_purchase_request_line(models.TransientModel):
    _name 	= 'bp_rab_pr.wiz_generate_purchase_request_line'

    name 		    = fields.Char(string='Description', required=True)
    product_id 	    = fields.Many2one('product.template', string='Product')
    uom_id 	        = fields.Many2one('uom.uom', string='Uom')
    qty_rab 	    = fields.Float(string='Qty RAB')
    qty_request 	= fields.Float(string='Qty Request')
    rab_product_id 	= fields.Many2one('bp_rab.rab_product', string='RAM', required=True, ondelete='cascade')
    wiz_generate_purchase_request_id 	= fields.Many2one('bp_rab_pr.wiz_generate_purchase_request', string='Purchase Request', required=True, ondelete='cascade')

