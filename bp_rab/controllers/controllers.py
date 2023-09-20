# -*- coding: utf-8 -*-
# from odoo import http


# class BpRab(http.Controller):
#     @http.route('/bp_rab/bp_rab/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bp_rab/bp_rab/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bp_rab.listing', {
#             'root': '/bp_rab/bp_rab',
#             'objects': http.request.env['bp_rab.bp_rab'].search([]),
#         })

#     @http.route('/bp_rab/bp_rab/objects/<model("bp_rab.bp_rab"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bp_rab.object', {
#             'object': obj
#         })
