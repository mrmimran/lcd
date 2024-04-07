# -*- coding: utf-8 -*-
# from odoo import http


# class ProductSqmManagement(http.Controller):
#     @http.route('/product_sqm_management/product_sqm_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_sqm_management/product_sqm_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_sqm_management.listing', {
#             'root': '/product_sqm_management/product_sqm_management',
#             'objects': http.request.env['product_sqm_management.product_sqm_management'].search([]),
#         })

#     @http.route('/product_sqm_management/product_sqm_management/objects/<model("product_sqm_management.product_sqm_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_sqm_management.object', {
#             'object': obj
#         })
