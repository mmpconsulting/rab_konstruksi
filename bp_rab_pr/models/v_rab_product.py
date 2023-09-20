from odoo import api, fields, models, tools


class bp_rab_pr_v_rab_product(models.Model):
	_name 	= 'bp_rab_pr.v_rab_product'
	_auto 	= False
	
	def _compute_qty_purchase_request_line(self):
		for row in self:
			pr = self.env['bp_pr.purchase_request_line'].search([('rab_id','=',row.rab_id.id),('product_id','=',row.product_id.id)])
			row.qty_purchase_request_line = len(pr)

	def show_purchase_request_line(self):
		return {
			'type'      : 'ir.actions.act_window', 
			'name'      : 'Purchase Request Line',
			'views'     : [(self.env.ref('bp_purchase_request.purchase_request_line_list').id, 'tree')],
			'view_mode' : 'tree', 
			'res_model' : 'bp_pr.purchase_request_line', 
			'domain'    : [('rab_id', '=', self.rab_id.id),('product_id', '=', self.product_id.id)], 
			'context'   : "{'create':False, 'edit':False, 'delete':False}"}
	
	
	name 			= fields.Char(string='Product', related='product_id.name')
	product_id 	    = fields.Many2one('product.template', string='Product')
	rab_id 	        = fields.Many2one('bp_rab.rab', string='RAB')
	rab_date 	    = fields.Date(string='RAB Date')
	state 	        = fields.Selection(string='State', selection=[('draft', 'Draft'), ('rab', 'RAB'), ('finish', 'Finish'), ('cancel', 'Cancel'),])
	rab_product_id 	= fields.Many2one('bp_rab.rab_product', string='RAM')
	price 	        = fields.Float(string='Price')
	price_rap 		= fields.Float(string='Price RAP')
	qty_rab 	    = fields.Float(string='Qty RAB')
	qty_rap 		= fields.Float(string='Qty RAP')
	qty_request 	= fields.Float(string='Qty Request')
	qty_po 	        = fields.Float(string='Qty PO')
	qty_receipt 	= fields.Float(string='Qty Receipt')
	qty_consume 	= fields.Float(string='Qty Consume')
	rab_formula_line_ids 		= fields.One2many('bp_rab.rab_formula_line', 'rab_product_id', string='RAB Detail')
	qty_purchase_request_line 	= fields.Integer(string='Purchase Request', compute='_compute_qty_purchase_request_line')


	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute('''
			CREATE OR REPLACE VIEW %s AS (
SELECT rab_p.id, rab_p.product_id, rab_p.qty as qty_rab, rab_p.price, 
	rab_p.qty_rap, rab_p.price_rap,
	rab_p.rab_id, rab_p.id as rab_product_id,
	rab.state, rab.rab_date,
	COALESCE(pr.qty_request,0) as qty_request, 
	COALESCE(po.qty_po,0) as qty_po,
	COALESCE(sm.qty_receipt,0) as qty_receipt,
	COALESCE(ss.qty_consume,0) as qty_consume

FROM bp_rab_rab rab, bp_rab_rab_product rab_p
	LEFT OUTER JOIN(
		SELECT pr.rab_id, pr_line.product_id, sum(pr_line.qty_request) as qty_request
		FROM bp_pr_purchase_request pr, bp_pr_purchase_request_line pr_line
		WHERE pr.state in ('approved','done') AND 
			pr.id = pr_line.purchase_request_id
		GROUP BY pr.rab_id, pr_line.product_id
		)pr ON pr.product_id = rab_p.product_id AND pr.rab_id = rab_p.rab_id
	
	LEFT OUTER JOIN(
		SELECT po.rab_id, po_line.product_id, sum(po_line.product_qty) as qty_po
		FROM purchase_order po, purchase_order_line po_line
		WHERE po.state in ('purchase','done') AND 
			po.id = po_line.order_id
		GROUP BY po.rab_id, po_line.product_id
	)po ON po.product_id = rab_p.product_id AND po.rab_id = rab_p.rab_id

	LEFT OUTER JOIN(
		SELECT po.rab_id, sm.product_id, sum(sm.product_qty) as qty_receipt
		FROM purchase_order po, purchase_order_stock_picking_rel po_sp_rel,
			stock_picking sp, stock_move sm
		WHERE sp.state = 'done' AND
			po.id = po_sp_rel.purchase_order_id AND
			po_sp_rel.stock_picking_id = sp.id AND
			sp.id = sm.picking_id
		GROUP BY po.rab_id, sm.product_id
	)sm ON sm.product_id = rab_p.product_id AND sm.rab_id = rab_p.rab_id
	
	LEFT OUTER JOIN(
		SELECT ss.rab_id, ss.product_id, sum(ss.scrap_qty) as qty_consume
		FROM stock_scrap ss
		WHERE ss.state='done'
		GROUP BY ss.rab_id, ss.product_id
	)ss ON ss.product_id = rab_p.product_id AND ss.rab_id = rab_p.rab_id
	
WHERE rab_p."type"='ram' AND rab_p.rab_id = rab.id
			)''' % (self._table,)
		)