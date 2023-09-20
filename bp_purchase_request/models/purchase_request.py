from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class bp_pr_purchase_request(models.Model):
    _name 	        = 'bp_pr.purchase_request'
    _order 	        = 'name desc'
    _inherit		= ['mail.thread']
    _description	= 'Purchase Request'

    def can_edited(self):
        qty_proses = sum((i.rfq + i.qty_po) for i in self.purchase_request_line_ids)
        if qty_proses == 0:
            return True
        else:
            return False
        
    @api.onchange('user_request_id')
    def _onchange_user_request_id(self):
        employee = self.env['hr.employee'].search([('user_id','=',self.user_request_id.id)])
        if employee.department_id.id:
            self.department_id = employee.department_id.id

    def action_draft(self):
        qty_proses = sum((i.qty_rfq + i.qty_po) for i in self.purchase_request_line_ids)
        if qty_proses == 0:
            return self.write({'state':'draft'})
        else:
            raise UserError(_('Cannot be set to draft \n' + 'An RFQ already created'))
        
    def action_draft_administrator(self):
        self.action_draft()
    
    def action_to_approve(self):
        if len(self.purchase_request_line_ids)>0:
            return self.write({'state':'to_approve', 'name':self.env['ir.sequence'].next_by_code('bp_pr.purchase_request') if self.name == '-' else self.name})
        else:
            raise UserError(_("Please insert product first"))

    def action_approved(self):
        return self.write({'state':'approved', 'user_approved_id':self.env.user.id, 'date_approved':datetime.today()})
    
    def action_rejected(self):
        return self.write({'state':'rejected'})
    
    def action_done(self):
        return self.write({'state':'done'})
    
    def unlink(self):
        for row in self:
            if not row.state == 'draft':
                raise UserError(_('You cannot delete a purchase request which is not draft.'))
        return super(bp_pr_purchase_request, self).unlink()
    
    

    name 		        = fields.Char(string='Number', default='-')
    user_request_id 	= fields.Many2one('res.users', string='Request by', default=lambda self: self.env.user.id, required=True, tracking=True)
    user_approved_id 	= fields.Many2one('res.users', string='Approved by', tracking=True)
    date_request 	    = fields.Date(string='Request Date', default=fields.Datetime.now, tracking=True)
    date_approved 	    = fields.Date(string='Approved Date', tracking=True)
    origin 	            = fields.Char(string='Source Document', size=50)
    desc 	            = fields.Text(string='Desc')
    department_id 	    = fields.Many2one('hr.department', string='Department', ondelete='restrict')
    state 	            = fields.Selection(string='State', selection=[('draft', 'Draft'), ('to_approve', 'To be approved'), ('approved','Approved'), ('rejected','Rejected'), ('done','Done')], default='draft', tracking=True)
    purchase_request_line_ids 	= fields.One2many('bp_pr.purchase_request_line', 'purchase_request_id', string='Purchase Request')

class bp_pr_purchase_request_line(models.Model):
    _name 	        = 'bp_pr.purchase_request_line'
    _order 	        = 'date_request desc'
    _inherit		= ['mail.thread']
    _description	= 'Purchase Request Line'

    @api.depends('product_id')
    def _compute_uom_id(self):
        for row in self:
            row.uom_id = row.product_id.uom_id.id
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name = self.product_id.name

    def _compute_qty_rfq(self):
        for row in self:
            po_line = self.env['purchase.order.line'].search([('purchase_request_line_id','=',row.id), ('state','in',['draft','sent','to approve'])])
            row.qty_rfq = sum(i.product_qty for i in po_line)
    
    def _compute_qty_po(self):
        for row in self:
            po_line = self.env['purchase.order.line'].search([('purchase_request_line_id','=',row.id), ('state','in',['purchase','done'])])
            row.qty_po = sum(i.product_qty for i in po_line)
    
    @api.depends('qty_rfq','qty_po')
    def _compute_qty_remaining(self):
        for row in self:
            row.qty_remaining = row.qty_request - row.qty_rfq - row.qty_po
    

    name 		    = fields.Char(string='Description', required=True, tracking=True)
    product_id 	    = fields.Many2one('product.template', string='Product', required=True, ondelete='restrict', tracking=True)
    uom_id 	        = fields.Many2one('uom.uom', string='Uom', compute='_compute_uom_id', store=True)
    qty_request 	= fields.Float(string='Qty Request', tracking=True)
    qty_rfq 	    = fields.Float(string='Qty RFQ', compute='_compute_qty_rfq')
    qty_po 	        = fields.Float(string='Qty PO', compute='_compute_qty_po')
    qty_remaining 	= fields.Float(string='Qty Remaining', compute='_compute_qty_remaining')
    qty_rejected 	= fields.Float(string='Qty Rejected')
    purchase_request_id 	= fields.Many2one('bp_pr.purchase_request', string='Purchase Request', ondelete='cascade')
    date_request 	        = fields.Date(string='Request Date', related='purchase_request_id.date_request', store=True)
    state 	                = fields.Selection(string='State', related='purchase_request_id.state', store=True)
    

