from odoo import api, fields, models
from odoo.exceptions import ValidationError

class bp_rab_formula(models.Model):
    _name 	    = 'bp_rab.formula'
    _inherit    = 'bp_rab.master_formula'
    _description	= 'Formula'

    @api.onchange('master_formula_id')
    def _onchange_master_formula_id(self):
        if not self.name:
            self.name = self.master_formula_id.name

        self.formula_line_ids.unlink()
        self.formula_category_ids.unlink()
        if self.master_formula_id:
            for i in self.master_formula_id.master_formula_line_ids:
                self.formula_line_ids.create({
                    'formula_id' : self.id,
                    'name' : i.name,
                    'code' : i.code,
                    'product_id' : i.product_id.id,
                    'uom_id' : i.uom_id.id,
                    'group_id' : i.group_id.id,
                    'category_id' : i.category_id.id,
                    'formula' : i.formula,
                    'qty' : i.qty,
                    'price' : i.price,
                    'total' : i.total,
                    'sequence' : i.sequence})
                
            for i in self.master_formula_id.master_formula_master_category_ids:
                self.formula_category_ids.create({
                    'formula_id' : self.id, 
                    'name' : i.name,
                    'code' : i.code,
                    'formula' : i.formula,
                    'value' : i.value,
                    'uom_id' : i.uom_id.id,
                    'sequence' : i.sequence})
    
    @api.depends('formula_line_ids')
    def _compute_jumlah(self):
        self.jumlah = sum(i.total for i in self.formula_line_ids)

    def compute_formula(self):
        for i in self.master_formula_line_ids:
            i.compute_formula()

    def compute_formula_category(self):
        for i in self.master_formula_master_category_ids:
            print(i.code)
            i.compute_formula()

    @api.model
    def create(self, vals):
        return super(models.Model, self).create(vals)
    
    name 		= fields.Char(string='Name', required=True)
    rab_id 	    = fields.Many2one('bp_rab.rab', string='RAB', required=True, ondelete='cascade')
    master_formula_id 	    = fields.Many2one('bp_rab.master_formula', string='Master Formula', ondelete='restrict')
    master_category_id 	    = fields.Many2one('bp_rab.master_category', string='Master Category', related='master_formula_id.master_category_id', store=True)
    formula_line_ids 	    = fields.One2many('bp_rab.formula_line', 'formula_id', string='Detail')
    formula_category_ids 	= fields.One2many('bp_rab.formula_category', 'formula_id', string='Category')
    rab_pekerjaan_ids 	    = fields.One2many('bp_rab.rab_pekerjaan', 'formula_id', string='RAB')


class bp_rab_formula_line(models.Model):
    _name 	    = 'bp_rab.formula_line'
    _inherit    = 'bp_rab.master_formula_line'

    def compute_formula(self):
        if self.formula:
            formula = self.formula
            for char in self.formula.split():
                if '$' in char:
                    char = str(char).replace("(", "").replace(")", "")
                    category = self.env['bp_rab.master_formula_master_category'].search([('code', '=', char),('formula_id', '=', self.formula_id.id)])
                    formula_line = self.env['bp_rab.master_formula_line'].search([('code', '=', char),('formula_id', '=', self.formula_id.id)])
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
    
    formula_id 	= fields.Many2one('bp_rab.formula', string='Formula', ondelete='cascade')


class bp_rab_formula_category(models.Model):
    _name 	    = 'bp_rab.formula_category'
    _inherit    = 'bp_rab.master_formula_master_category'

    def compute_formula(self):
        if self.formula:
            formula = self.formula
            for char in self.formula.split():
                if '$' in char:
                    char = str(char).replace("(", "").replace(")", "")
                    line = self.search([('code', '=', char),('formula_id', '=', self.formula_id.id)])
                    if line:
                        formula = formula.replace(char, str(line.value))
                    else:
                        raise ValidationError('Code ' + char + ' in formula ' + self.formula + ' not found')
            
            try:
                self.value = eval(formula)
            except Exception as e:
                raise ValidationError('Wrong Formula ' + self.formula + ' \n' + str(e))

    formula_id 	= fields.Many2one('bp_rab.formula', string='Formula', ondelete='cascade')

class bp_rab_formula_product(models.Model):
    _name 	= 'bp_rab.formula_product'

    product_id 	= fields.Many2one('product.template', string='Product', required=True, ondelete='restrict')
    uom_id 	    = fields.Many2one('uom.uom', string='Uom', related='product_id.uom_id')
    type 	    = fields.Selection(string='Product Type', related='product_id.type')
    price 	    = fields.Float(string='Price')
    rab_id 	    = fields.Many2one('bp_rab.rab', string='RAB', required=True, ondelete='cascade')


