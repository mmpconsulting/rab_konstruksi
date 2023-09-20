# -*- coding: utf-8 -*-
# from odoo import http


# class BpPurchaseRequest(http.Controller):
#     @http.route('/bp_purchase_request/bp_purchase_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bp_purchase_request/bp_purchase_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bp_purchase_request.listing', {
#             'root': '/bp_purchase_request/bp_purchase_request',
#             'objects': http.request.env['bp_purchase_request.bp_purchase_request'].search([]),
#         })

#     @http.route('/bp_purchase_request/bp_purchase_request/objects/<model("bp_purchase_request.bp_purchase_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bp_purchase_request.object', {
#             'object': obj
#         })
