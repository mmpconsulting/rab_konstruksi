from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class bp_rab_master_formula(models.Model):
    _name 	= 'bp_rab.master_formula'
    _order 	= 'name'
    _inherit		= ['mail.thread']
    _description	= 'Formula'

    def name_get(self):
        data = []
        for x in self:
            if x.number:
                data.append((x.id, '[' + x.number + '] ' + x.name))
            else:
                data.append((x.id, x.name))
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
    
    @api.onchange('master_category_id') 
    def _onchange_master_category_id(self):
        if self.master_category_id:
            for i in self.master_category_id.master_category_line_ids:
                self.master_formula_master_category_ids.create({
                    'master_formula_id' : self.id, 
                    'name' : i.name,
                    'code' : i.code,
                    'formula' : i.formula,
                    'value' : i.value,
                    'uom_id' : i.uom_id.id,
                    'sequence' : i.sequence})
        else:
            self.master_formula_master_category_ids.unlink()

    @api.depends('master_formula_line_ids')
    def _compute_jumlah(self):
        self.jumlah = sum(i.total for i in self.master_formula_line_ids)

    @api.depends('jumlah','margin')
    def _compute_margin_value(self):
        for row in self:
            row.margin_value = row.margin / 100 * row.jumlah

    @api.depends('margin_value','jumlah')
    def _compute_hsp(self):
        for row in self:
            row.hsp = row.jumlah + row.margin_value

    def compute_formula(self):
        for i in self.master_formula_line_ids:
            i.compute_formula()

    def compute_formula_category(self):
        for i in self.master_formula_master_category_ids:
            print(i.code)
            i.compute_formula()

    def check_code(self, code):
        if code:
            line = self.master_formula_line_ids.filtered(lambda i: i.code==code)
            category = self.master_formula_master_category_ids.filtered(lambda i: i.code==code)
            if len(line)+len(category)>1:
                raise ValidationError('Code ' + code + ' sudah ada')
            
    @api.constrains('number')
    def _check_number(self):
        if len(self.search([('number', '=', self.number)])) > 1:
            raise ValidationError('Number ' + self.number + ' sudah ada')
        
    def get_number(self):
        kembar=True
        while kembar:
            code = self.env['ir.sequence'].next_by_code('bp_rab.master_formula')
            if len(self.search([('number', '=', code)])) == 0:
                kembar=False
        return code

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copy)") % self.name
        default['number'] = self.get_number()
        return super(bp_rab_master_formula, self).copy(default=default)

    @api.model
    def create(self, vals):
        if not self.number:
            vals['number'] = self.get_number()
        return super(bp_rab_master_formula, self).create(vals)

    name 		    = fields.Char(string='Formula', required=True, tracking=True)
    number 	        = fields.Char(string='Number', size=10)
    margin 	        = fields.Float(string='Margin (%)', tracking=True)
    jumlah 	        = fields.Float(string='Jumlah', compute='_compute_jumlah', store=True)
    margin_value 	= fields.Float(string='Margin', compute='_compute_margin_value', store=True)
    hsp 	        = fields.Float(string='HSP', compute='_compute_hsp', store=True)
    active 	        = fields.Boolean(string='Active', default=True, tracking=True)
    master_category_id 	= fields.Many2one('bp_rab.master_category', string='Category', ondelete='restrict')
    master_formula_line_ids 	        = fields.One2many('bp_rab.master_formula_line', 'master_formula_id', string='Detail', copy=True)
    master_formula_master_category_ids 	= fields.One2many('bp_rab.master_formula_master_category', 'master_formula_id', string='Category', copy=True)

class bp_rab_master_formula_line(models.Model):
    _name 	= 'bp_rab.master_formula_line'
    _order 	= 'sequence'
    _inherit		= ['mail.thread']
    _description	= 'Detail Formula'

    @api.onchange('code')
    def _onchange_code(self):
        if self.code and not self.code[0] == '$':
            self.code = '$' + self.code

    @api.depends('product_id')
    def _compute_uom_id(self):
        for row in self:
            row.uom_id = row.product_id.uom_id.id

    @api.depends('qty', 'price')
    def _compute_total(self):
        for row in self:
            row.total = row.qty * row.price
    
    def compute_formula(self):
        if self.formula:
            formula = self.formula
            for char in self.formula.split():
                if '$' in char:
                    char = str(char).replace("(", "").replace(")", "")
                    category = self.env['bp_rab.master_formula_master_category'].search([('code', '=', char),('master_formula_id', '=', self.master_formula_id.id)])
                    formula_line = self.env['bp_rab.master_formula_line'].search([('code', '=', char),('master_formula_id', '=', self.master_formula_id.id)])
                    if category:
                        formula = formula.replace(char, str(category.value))
                    elif formula_line:
                        formula = formula.replace(char, str(formula_line.qty))
                    else:
                        raise ValidationError('Code ' + char + ' in formula ' + self.formula + ' not found')
            try:
                self.qty = eval(formula)
            except Exception as e:
                raise ValidationError('Wrong Formula ' + self.formula + ' \n' + str(e))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name = self.product_id.name
        category = self.env['bp_rab.group'].search([('name','=',self.product_id.categ_id.name),('tag','=','category')])
        if len(category)==1:
            self.category_id = category.id
        

    @api.constrains('code')
    def _check_code(self):
        for row in self:
            row.master_formula_id.check_code(row.code)
    

    name 		= fields.Char(string='Description', tracking=True)
    code 	    = fields.Char(string='Code', size=50, tracking=True)
    product_id 	= fields.Many2one('product.template', string='Product', required=True, ondelete='restrict', tracking=True)
    uom_id 	    = fields.Many2one('uom.uom', string='Uom', compute='_compute_uom_id', store=True)
    group_id 	= fields.Many2one('bp_rab.group', string='Group', required=True, ondelete='restrict', domain=[('tag','=','formula')])
    category_id = fields.Many2one('bp_rab.group', string='Category', required=True, ondelete='restrict', domain=[('tag','=','category')])
    formula 	= fields.Char(string='Formula', size=200, tracking=True)
    qty 	    = fields.Float(string='Qty', tracking=True)
    price 	    = fields.Float(string='Price', tracking=True)
    total 	    = fields.Float(string='Total', compute='_compute_total')
    sequence 	= fields.Integer(string='Sequence', default=1)
    master_formula_id 	= fields.Many2one('bp_rab.master_formula', string='Formula', ondelete='cascade')

class bp_rab_master_formula_master_category(models.Model):
    _name 	    = 'bp_rab.master_formula_master_category'
    _inherit    = 'bp_rab.master_category_line'

    @api.constrains('code')
    def _check_code(self):
        for row in self:
            row.master_formula_id.check_code(row.code)

    def compute_formula(self):
        if self.formula:
            formula = self.formula
            for char in self.formula.split():
                if '$' in char:
                    char = str(char).replace("(", "").replace(")", "")
                    line = self.search([('code', '=', char),('master_formula_id', '=', self.master_formula_id.id)])
                    if line:
                        formula = formula.replace(char, str(line.value))
                    else:
                        raise ValidationError('Code ' + char + ' in formula ' + self.formula + ' not found')
            
            try:
                self.value = eval(formula)
            except Exception as e:
                raise ValidationError('Wrong Formula ' + self.formula + ' \n' + str(e))

    master_formula_id 	= fields.Many2one('bp_rab.master_formula', string='Formula', ondelete='cascade')


