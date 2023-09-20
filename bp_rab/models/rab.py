from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import xlsxwriter, io, base64

class bp_rab_rab(models.Model):
    _name 	= 'bp_rab.rab'
    _order 	= 'rab_date desc'
    _inherit		= ['mail.thread']
    _description	= 'RAB'
    
    def action_create_so(self):
        if self.env.user.company_id.project_product_id:
            vals = {
                "partner_id" : self.partner_id.id,
                "rab_id" : self.id,
            }
            so = self.env['sale.order'].create(vals)
            
            line_vals = {
                'product_id' : self.env.user.company_id.project_product_id.id,
                'name' : self.name,
                'product_uom_qty' : 1,
                'price_unit' : self.total,
                'order_id' : so.id
            }
            self.env['sale.order.line'].create(line_vals)
            
            view = self.env.ref('sale.view_order_form')
            
            return {
                'type': 'ir.actions.act_window',
                'name': self.name,
                'res_model': 'sale.order',
                'view_mode': 'form',
                'view_id' : view.id,
                'target': 'current',
                'res_id' : so.id
            }
        else:
            raise UserError('Default service product is not set.')

    def action_rpt_rab_excel(self):
        rpt_rab = self.env['bp_rab.rpt_rab']
        self.write({'xlsx_file': rpt_rab.get_rpt_rab_excel(self),})
        return {'type' : 'ir.actions.act_url',
                'url': 'web/content/?model=' + self._name + '&field=xlsx_file&download=true&id=' + str(self.id) + '&filename=RAB ' + self.name + '.xlsx',
                'target': 'new',}
    
    def action_rpt_ram_excel(self):
        rpt_ram = self.env['bp_rab.rpt_ram']
        self.write({'xlsx_file': rpt_ram.get_rpt_ram_excel(self, self.rab_product_ram_ids, 'RAM'),})
        return {'type' : 'ir.actions.act_url',
                'url': 'web/content/?model=' + self._name + '&field=xlsx_file&download=true&id=' + str(self.id) + '&filename=RAM ' + self.name + '.xlsx',
                'target': 'new',}
    
    def action_rpt_raj_excel(self):
        rpt_ram = self.env['bp_rab.rpt_ram']
        self.write({'xlsx_file': rpt_ram.get_rpt_ram_excel(self, self.rab_product_raj_ids, 'RAJ'),})
        return {'type' : 'ir.actions.act_url',
                'url': 'web/content/?model=' + self._name + '&field=xlsx_file&download=true&id=' + str(self.id) + '&filename=RAJ ' + self.name + '.xlsx',
                'target': 'new',}
    
    def show_sale_order(self):
        return {
            'type'      : 'ir.actions.act_window', 
            'name'      : 'Sale Order',
            'views'     : [(self.env.ref('sale.view_quotation_tree_with_onboarding').id, 'tree'), (self.env.ref('sale.view_order_form').id, 'form')],
            'view_mode' : 'tree,form', 
            'res_model' : 'sale.order', 
            'domain'    : [('rab_id', '=', self.id)], 
            'context'   : "{'create':False, 'edit':False, 'delete':False}"}
    
    def name_get(self):
        data = []
        for x in self:
            data.append((x.id, '[' + x.number + '] ' + x.name))
        return data
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + ['|', ('name', 'ilike', name), ('number', 'ilike', name)]),limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
    
    def _compute_qty_sale_order(self):
        for row in self:
            so = self.env['sale.order'].search([('rab_id','=',self.id)])
            row.qty_sale_order = len(so)
    
    @api.depends('rab_pekerjaan_ids')
    def _compute_total(self):
        self.total = sum(i.total for i in self.rab_pekerjaan_ids)

    def get_rab_product_id(self, product_id):
        rab_product = self.env['bp_rab.rab_product'].search([('rab_id','=',self.id), ('product_id','=',product_id.id)])
        if not rab_product:
            formula_product = self.env['bp_rab.formula_product'].search([('rab_id','=',self.id), ('product_id','=',product_id.id)])
            rab_product = self.env['bp_rab.rab_product'].create({
                'rab_id' : self.id, 
                'product_id' : product_id.id,
                'price' : formula_product.price,
                'type' : 'raj' if product_id.type == 'service' else 'ram'})
        
        return rab_product.id
    
    def get_price(self):
        self.formula_product_ids.unlink()
        formula_line = self.env['bp_rab.formula_line'].read_group([ ('formula_id.rab_id','=',self.id) ], fields=['product_id','price:max'], groupby=['product_id'])
        for i in formula_line:
            self.env['bp_rab.formula_product'].create({'rab_id':self.id, 'product_id':i['product_id'][0], 'price':i['price']})

    def update_price(self):
        for i in self.formula_ids:
            query = """
                    SELECT fl.id, fl.product_id, fp.price
                    FROM bp_rab_formula_line fl, bp_rab_formula_product fp
                    WHERE fl.formula_id=%s
                        AND fp.rab_id=%s
                        AND fl.product_id=fp.product_id
                        AND NOT fl.price=fp.price
                    """ % (str(i.id), str(self.id))
            self.env.cr.execute(query)
            product_price = self.env.cr.dictfetchall()
            for j in product_price:
                formula_line = self.env['bp_rab.formula_line'].search([('id','=',j['id'])])
                formula_line.write({'price':j['price']})
                formula_line._compute_total()
            
            if product_price:
                i._compute_jumlah()

    def create_ram_raj(self):
        if len(self.rab_pekerjaan_ids) == 0:
            raise UserError(_('Insert RAB first'))
        elif len(self.rab_pekerjaan_ids.search([('rab_id','=',self.id),('formula_id','=',False)])) > 0:
            raise UserError(_('There is a formula that is still empty'))
        else:
            self.get_price()
            self.update_price()
            for i in self.rab_pekerjaan_ids:
                i.write({'bobot' : i.total / self.total})
                for j in i.formula_id.formula_line_ids:
                    rab_product_id = self.get_rab_product_id(j.product_id)
                    i.rab_formula_line_ids.create({
                        'rab_pekerjaan_id' : i.id,
                        'formula_line_id' : j.id,
                        'rab_product_id' : rab_product_id,
                        'product_id' : j.product_id.id,
                        'qty' : j.qty * i.volume_akhir,
                        'price' : j.price,
                        'total' : j.total * i.volume_akhir,
                        'sequence' : i.sequence})
            self.write({'state':'rab'})
                
    def action_draft(self):
        self.rab_product_ram_ids.unlink()
        self.rab_product_raj_ids.unlink()
        for i in self.rab_pekerjaan_ids:
            i.rab_formula_line_ids.unlink()
        self.write({'state':'draft'})
    
    def action_finish(self):
        self.write({'state':'finish'})

    def action_cancel(self):
        self.write({'state':'cancel'})
    
    def unlink(self):
        for row in self:
            if row.state == 'draft':
                return super(bp_rab_rab, self).unlink()
            else:
                raise UserError(_('Only draft state can be delete'))

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('bp_rab.rab')
        return super(bp_rab_rab, self).create(vals)

    name 		= fields.Char(string='Pekerjaan', size=50, required=True, tracking=True)
    partner_id 	= fields.Many2one('res.partner', string='Customer', domain=[('customer_rank','=',True)], required=True)
    rab_date 	= fields.Date(string='RAB Date', default=fields.Datetime.now, tracking=True)
    number 	    = fields.Char(string='Number', size=10)
    lokasi 	    = fields.Char(string='Lokasi', size=50)
    due_date 	= fields.Integer(string='Due Date')
    total 	    = fields.Float(string='Total', compute='_compute_total', store=True)
    state 	    = fields.Selection(string='State', selection=[('draft', 'Draft'), ('rab', 'Rab'), ('finish', 'Finish'), ('cancel', 'Cancel'),], default='draft', tracking=True)
    xlsx_file   = fields.Binary(string='Excel File')
    qty_sale_order 	        = fields.Integer(string='Sale Order', compute='_compute_qty_sale_order')

    rab_pekerjaan_ids 	    = fields.One2many('bp_rab.rab_pekerjaan', 'rab_id', string='RAB')
    rab_product_ids 	    = fields.One2many('bp_rab.rab_product', 'rab_id', string='Product')
    formula_ids 	        = fields.One2many('bp_rab.formula', 'rab_id', string='Formula')
    formula_product_ids 	= fields.One2many('bp_rab.formula_product', 'rab_id', string='Price')
    rab_product_ram_ids 	= fields.One2many('bp_rab.rab_product', 'rab_id', string='RAM', domain=[('type','=','ram')])
    rab_product_raj_ids 	= fields.One2many('bp_rab.rab_product', 'rab_id', string='RAJ', domain=[('type','=','raj')])

class bp_rab_rab_pekerjaan(models.Model):
    _name 	= 'bp_rab.rab_pekerjaan'
    _order 	= 'sequence'
    _inherit		= ['mail.thread']
    _description	= 'Pekerjaan'

    @api.onchange('group_id')
    def _onchange_group_id(self):
        ctx = self.env.context
        if 'default_rab_id' in ctx and ctx['default_rab_id']:
            return {'domain': {'formula_id': [('rab_id', '=', ctx['default_rab_id'])]}}
        
    @api.depends('formula_id')
    def _compute_hsp(self):
        self.hsp = self.formula_id.hsp if self.formula_id else 0

    @api.depends('panjang','lebar','tinggi','unit')
    def _compute_volume(self):
        self.volume = self.panjang * self.lebar * self.tinggi * self.unit

    @api.depends('volume','index')
    def _compute_volume_akhir(self):
        self.volume_akhir = self.volume * self.index

    @api.depends('volume_akhir','hsp')
    def _compute_total(self):
        self.total = self.total = self.volume_akhir * self.hsp
    
    name 		    = fields.Char(string='Item Pekerjaan', required=True, tracking=True)
    group_id 	    = fields.Many2one('bp_rab.group', string='Group', required=True, ondelete='restrict', domain=[('tag','=','rab')])
    group_line_id 	= fields.Many2one('bp_rab.group_line', string='Sub Group', required=True, ondelete='restrict')
    kode_gambar 	= fields.Char(string='Kode Gambar', size=50, tracking=True)
    spesifikasi 	= fields.Char(string='Spesifikasi', size=50, tracking=True)
    formula_id 	    = fields.Many2one('bp_rab.formula', string='Formula', ondelete='restrict', tracking=True)
    panjang 	    = fields.Float(string='Panjang', tracking=True)
    lebar 	        = fields.Float(string='Lebar', tracking=True)
    tinggi 	        = fields.Float(string='Tinggi', tracking=True)
    unit 	        = fields.Float(string='Unit', tracking=True)
    volume 	        = fields.Float(string='Volume', compute='_compute_volume', store=True)
    index 	        = fields.Float(string='Index', default=1, tracking=True)
    volume_akhir 	= fields.Float(string='Volume Akhir', compute='_compute_volume_akhir', store=True)
    hsp 	        = fields.Float(string='HSP', compute='_compute_hsp', store=True)
    total 	        = fields.Float(string='Total', compute='_compute_total', store=True)
    bobot 	        = fields.Float(string='Bobot (%)')
    sequence 	    = fields.Integer(string='Sequence', default=1)
    rab_id 	        = fields.Many2one('bp_rab.rab', string='RAB', ondelete='cascade')
    rab_formula_line_ids 	= fields.One2many('bp_rab.rab_formula_line', 'rab_pekerjaan_id', string='Formula Detail')

class bp_rab_rab_formula_line(models.Model):
    _name 	= 'bp_rab.rab_formula_line'
    _order 	= 'sequence'

    rab_pekerjaan_id 	= fields.Many2one('bp_rab.rab_pekerjaan', string='Pekerjaan', ondelete='restrict')
    rab_product_id 	    = fields.Many2one('bp_rab.rab_product', string='Product')
    formula_line_id 	= fields.Many2one('bp_rab.formula_line', string='Formula Detail')
    product_id 	= fields.Many2one('product.template', string='Product')
    qty 	    = fields.Float(string='Qty')
    price 	    = fields.Float(string='Price')
    total 	    = fields.Float(string='Total')
    sequence 	= fields.Integer(string='Sequence', default=1)

class bp_rab_rab_product(models.Model):
    _name 	= 'bp_rab.rab_product'

    @api.depends('rab_formula_line_ids')
    def _compute_total(self):
        for row in self:
            qty = 0
            total = 0 
            for i in row.rab_formula_line_ids:
                qty += i.qty
                total += i.total

            row.total = total
            row.qty = qty

    @api.depends('qty','index_qty')
    def _compute_qty_rap(self):
        for row in self:
            row.qty_rap = row.qty * row.index_qty

    @api.depends('price','index_price')
    def _compute_price_rap(self):
        for row in self:
            row.price_rap = row.price * row.index_price

    @api.depends('qty_rap','price_rap')
    def _compute_total_rap(self):
        for row in self:
            row.total_rap = row.qty_rap * row.price_rap
    
    name 		= fields.Char(string='Name')
    product_id 	= fields.Many2one('product.template', string='Product', required=True)
    type 	    = fields.Selection(string='Type', selection=[('ram', 'RAM'), ('raj', 'RAJ')])
    qty 	    = fields.Float(string='Qty RAB', compute='_compute_total', store=True)
    price 	    = fields.Float(string='Price', compute='_compute_total', store=True)
    total 	    = fields.Float(string='Total', compute='_compute_total', store=False)
    index_qty 	= fields.Float(string='Idx Qty', default=1)
    index_price = fields.Float(string='Idx Price', default=1)
    qty_rap 	= fields.Float(string='Qty RAP', compute='_compute_qty_rap', store=True)
    price_rap 	= fields.Float(string='Price RAP', compute='_compute_price_rap', store=True)
    total_rap 	= fields.Float(string='Total RAP', compute='_compute_total_rap', store=False)
    rab_id 	    = fields.Many2one('bp_rab.rab', string='RAB', required=True, ondelete='cascade')
    rab_formula_line_ids 	= fields.One2many('bp_rab.rab_formula_line', 'rab_product_id', string='RAB Detail')
