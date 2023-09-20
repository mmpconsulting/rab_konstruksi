from odoo import api, fields, models


class bp_rab_group(models.Model):
    _name 	= 'bp_rab.group'
    _order 	= 'name'

    name 	= fields.Char(string='Group', required=True)
    tag 	= fields.Selection(string='Tag', selection=[('formula', 'formula'), ('rab', 'rab'), ('category', 'category')])
    group_line_ids 	= fields.One2many('bp_rab.group_line', 'group_id', string='Sub Group')

class bp_rab_group_line(models.Model):
    _name 	= 'bp_rab.group_line'
    _order 	= 'sequence, id'

    name 		= fields.Char(string='Sub Group', required=True)
    sequence 	= fields.Integer(string='Sequence', default=1)
    group_id 	= fields.Many2one('bp_rab.group', string='Group', ondelete='cascade')
