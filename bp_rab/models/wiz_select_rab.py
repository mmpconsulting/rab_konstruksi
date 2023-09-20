from odoo import api, fields, models


class bp_rab_wiz_select_rab(models.TransientModel):
    _name 	= 'bp_rab.wiz_select_rab'

    def save(self):
        for i in self.rab_pekerjaan_ids:
            i.write({'formula_id':self.formula_id.id})
        return True

    rab_id 	            = fields.Many2one('bp_rab.rab', string='RAB', required=True)
    formula_id 	        = fields.Many2one('bp_rab.formula', string='Formula', required=True)
    rab_pekerjaan_ids 	= fields.Many2many('bp_rab.rab_pekerjaan', 'bp_rab_wiz_select_rab_rab_pekerjaan', id1='wiz_select_rab_id', id2='rab_pekerjaan_id', string='RAB')