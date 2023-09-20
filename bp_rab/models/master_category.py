from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class bp_rab_master_category(models.Model):
    _name 	= 'bp_rab.master_category'
    _order 	= 'name'
    _inherit		= ['mail.thread']
    _description	= 'Category'

    def name_get(self):
        data = []
        for x in self:
            if x.number:
                data.append((x.id, '[' + x.number + '] ' + x.name))
        return data
    
    def compute_formula(self):
        for i in self.master_category_line_ids:
            i.compute_formula()
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + ['|', ('name', 'ilike', name), ('number', 'ilike', name)]),limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
    
    @api.constrains('number')
    def _check_number(self):
        if len(self.search([('number', '=', self.number)])) > 1:
            raise ValidationError('Number ' + self.number + ' sudah ada')
        
    def get_number(self):
        kembar=True
        while kembar:
            code = self.env['ir.sequence'].next_by_code('bp_rab.master_category')
            if len(self.search([('number', '=', code)])) == 0:
                kembar=False
        return code
        
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copy)") % self.name
        default['number'] = self.get_number()
        return super(bp_rab_master_category, self).copy(default=default)
    
    @api.model
    def create(self, vals):
        if not self.number:
            vals['number'] = self.get_number()
        return super(bp_rab_master_category, self).create(vals)

    name 		    = fields.Char(string='Category', tracking=True)
    number 	        = fields.Char(string='Number', size=10)
    description 	= fields.Char(string='Description', size=100)
    active 	        = fields.Boolean(string='Active', default=True, tracking=True)
    master_category_line_ids 	= fields.One2many('bp_rab.master_category_line', 'master_category_id', string='Detail', copy=True)

class bp_rab_master_category_line(models.Model):
    _name 	= 'bp_rab.master_category_line'
    _order 	= 'sequence'
    _inherit		= ['mail.thread']
    _description	= 'Detail Category'

    @api.onchange('code')
    def _onchange_code(self):
        if self.code and not self.code[0] == '$':
            self.code = '$' + self.code

    def compute_formula(self):
        if self.formula:
            formula = self.formula
            for char in self.formula.split():
                if '$' in char:
                    char = str(char).replace("(", "").replace(")", "")
                    line = self.search([('code', '=', char),('master_category_id', '=', self.master_category_id.id)])
                    if line:
                        formula = formula.replace(char, str(line.value))
                    else:
                        raise ValidationError('Code ' + char + ' in formula ' + self.formula + ' not found')
            
            try:
                self.value = eval(formula)
            except Exception as e:
                raise ValidationError('Wrong Formula ' + self.formula + ' \n' + str(e))

    @api.constrains('code')
    def _check_code(self):
        for row in self:
            if row.code and len(row.search([('code', '=', row.code),('master_category_id', '=', row.master_category_id.id)])) > 1:
                raise ValidationError('Code ' + row.code + ' sudah ada')
    

    name 		= fields.Char(string='Description', required=True, tracking=True)
    code 	    = fields.Char(string='Code', size=50, tracking=True)
    formula 	= fields.Char(string='Formula', size=200, tracking=True)
    value 	    = fields.Float(string='Value', tracking=True)
    uom_id 	    = fields.Many2one('uom.uom', string='Uom')
    sequence 	= fields.Integer(string='Sequence', default=1)
    master_category_id = fields.Many2one('bp_rab.master_category', string='Category', ondelete='cascade')