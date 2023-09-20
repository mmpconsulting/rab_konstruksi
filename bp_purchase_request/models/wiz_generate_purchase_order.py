from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class bp_pr_wiz_generate_purchase_order(models.TransientModel):
    _name 	= 'bp_pr.wiz_generate_purchase_order'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        wizard_line_ids = []

        if not self.env.user.has_group('bp_purchase_request.bp_pr_administrator'):
            raise UserError(_('You do not have access'))
        
        if active_model == 'bp_pr.purchase_request_line':
            purchase_request_line = self.env['bp_pr.purchase_request_line'].search([('id','in',active_ids)])    
        elif active_model == 'bp_pr.purchase_request':
            purchase_request_line = self.env['bp_pr.purchase_request_line'].search([('purchase_request_id','in',active_ids)])

        if purchase_request_line:
            if all([req_line.state == 'approved' for req_line in purchase_request_line]):
                for i in purchase_request_line:
                    wizard_line_ids.append((0, 0, {
                        'name': i.name,
                        'product_id': i.product_id.id,
                        'uom_id': i.uom_id.id,
                        'qty_request': i.qty_remaining if i.qty_remaining > 0 else 0,
                        'qty_rfq': i.qty_remaining if i.qty_remaining > 0 else 0,
                        'purchase_request_line_id': i.id,
                        }))
            else:
                raise UserError(_('Only approved state can be processed'))

        if not wizard_line_ids:
            return res
        res['wiz_generate_purchase_order_line_ids'] = wizard_line_ids
        return res

    def save(self):
        if len(self.wiz_generate_purchase_order_line_ids) > 0:
            purchase_order = self.env['purchase.order'].create({
                'date_order' : self.date_po, 
                'partner_id' : self.partner_id.id,
                })
            for i in self.wiz_generate_purchase_order_line_ids:
                if i.qty_rfq > 0:
                    po_line = self.env['purchase.order.line'].create({
                        'name' : i.name,
                        'product_id' : i.product_id.id,
                        'product_qty' : i.qty_rfq,
                        'product_uom' : i.product_id.uom_id.id,
                        'date_planned' : self.date_po,
                        'price_unit' : 0.0,
                        'state' : 'draft',
                        'order_id' : purchase_order.id,
                        'purchase_request_line_id' : i.purchase_request_line_id.id
                        })
                    po_line._onchange_quantity()

            return {
                'res_id': purchase_order.id,
                'name': _('RFQ'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.order',
                'view_id': False,
                'context': False,
                'type': 'ir.actions.act_window'}

    date_po 	= fields.Date(string='RFQ Date', default=fields.Datetime.now, required=True)
    partner_id 	= fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank','=',True)], required=True)
    wiz_generate_purchase_order_line_ids 	= fields.One2many('bp_pr.wiz_generate_purchase_order_line', 'wiz_generate_purchase_order_id', string='Product')

class bp_pr_wiz_generate_purchase_order_line(models.TransientModel):
    _name 	= 'bp_pr.wiz_generate_purchase_order_line'

    wiz_generate_purchase_order_id 	= fields.Many2one('bp_pr.wiz_generate_purchase_order', string='Generate RFQ', required=True, ondelete='cascade')
    purchase_request_line_id 	    = fields.Many2one('bp_pr.purchase_request_line', string='Purchase Request Line')
    name 		    = fields.Char(string='Description')
    product_id 	    = fields.Many2one('product.template', string='Product', required=True, ondelete='restrict')
    uom_id 	        = fields.Many2one('uom.uom', string='Uom')
    qty_request 	= fields.Float(string='Qty Request')
    qty_rfq 	    = fields.Float(string='Qty RFQ')
