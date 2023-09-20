# -*- coding: utf-8 -*-
# from odoo import http


# class BpRabPr(http.Controller):
#     @http.route('/bp_rab_pr/bp_rab_pr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bp_rab_pr/bp_rab_pr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bp_rab_pr.listing', {
#             'root': '/bp_rab_pr/bp_rab_pr',
#             'objects': http.request.env['bp_rab_pr.bp_rab_pr'].search([]),
#         })

#     @http.route('/bp_rab_pr/bp_rab_pr/objects/<model("bp_rab_pr.bp_rab_pr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bp_rab_pr.object', {
#             'object': obj
#         })
