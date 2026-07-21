# -*- coding: utf-8 -*-
# from odoo import http


# class EterpObjetoGasto(http.Controller):
#     @http.route('/eterp_objeto_gasto/eterp_objeto_gasto', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eterp_objeto_gasto/eterp_objeto_gasto/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('eterp_objeto_gasto.listing', {
#             'root': '/eterp_objeto_gasto/eterp_objeto_gasto',
#             'objects': http.request.env['eterp_objeto_gasto.eterp_objeto_gasto'].search([]),
#         })

#     @http.route('/eterp_objeto_gasto/eterp_objeto_gasto/objects/<model("eterp_objeto_gasto.eterp_objeto_gasto"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eterp_objeto_gasto.object', {
#             'object': obj
#         })
