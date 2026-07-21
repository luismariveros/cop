# -*- coding: utf-8 -*-
# from odoo import http


# class EterpComprasUpdate(http.Controller):
#     @http.route('/eterp_compras_update/eterp_compras_update', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eterp_compras_update/eterp_compras_update/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('eterp_compras_update.listing', {
#             'root': '/eterp_compras_update/eterp_compras_update',
#             'objects': http.request.env['eterp_compras_update.eterp_compras_update'].search([]),
#         })

#     @http.route('/eterp_compras_update/eterp_compras_update/objects/<model("eterp_compras_update.eterp_compras_update"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eterp_compras_update.object', {
#             'object': obj
#         })
