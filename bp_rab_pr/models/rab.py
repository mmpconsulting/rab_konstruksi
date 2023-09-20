from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class bp_rab_rab(models.Model):
    _inherit 			= 'bp_rab.rab'

    def _compute_qty_purchase_request(self):
        for row in self:
            pr = self.env['bp_pr.purchase_request'].search([('rab_id','=',row.id)])
            row.qty_purchase_request = len(pr)

    def _compute_qty_purchase_order(self):
        for row in self:
            po = self.env['purchase.order'].search([('rab_id','=',row.id)])
            row.qty_purchase_order = len(po)   

    def show_purchase_request(self):
        return {
            'type'      : 'ir.actions.act_window', 
            'name'      : 'Purchase Request',
            'views'     : [(self.env.ref('bp_purchase_request.purchase_request_list').id, 'tree'), (self.env.ref('bp_purchase_request.purchase_request_form').id, 'form')],
            'view_mode' : 'tree,form', 
            'res_model' : 'bp_pr.purchase_request', 
            'domain'    : [('rab_id', '=', self.id)], 
            'context'   : "{'create':False, 'edit':False, 'delete':False}"}
    
    def show_purchase_order(self):
        return {
            'type'      : 'ir.actions.act_window', 
            'name'      : 'Purchase Order',
            'views'     : [(self.env.ref('purchase.purchase_order_view_tree').id, 'tree'), (self.env.ref('purchase.purchase_order_form').id, 'form')],
            'view_mode' : 'tree,form', 
            'res_model' : 'purchase.order', 
            'domain'    : [('rab_id', '=', self.id)], 
            'context'   : "{'create':False, 'edit':False, 'delete':False}"}
    
    def unlink(self):
        if self.qty_purchase_request == 0 and self.qty_purchase_order == 0:
            return super(bp_rab_rab, self).unlink()
        else:
            raise UserError(_('Cannot be deleted because it is used in another transaction'))
    

    qty_purchase_request 	= fields.Integer(string='Purchase Request', compute='_compute_qty_purchase_request')
    qty_purchase_order 	    = fields.Integer(string='Purchase Order', compute='_compute_qty_purchase_order')