# -*- coding: utf-8 -*-
# from odoo import http


# class EterpMesaEntrada16(http.Controller):
#     @http.route('/eterp_mesa_entrada_16/eterp_mesa_entrada_16', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eterp_mesa_entrada_16/eterp_mesa_entrada_16/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('eterp_mesa_entrada_16.listing', {
#             'root': '/eterp_mesa_entrada_16/eterp_mesa_entrada_16',
#             'objects': http.request.env['eterp_mesa_entrada_16.eterp_mesa_entrada_16'].search([]),
#         })

#     @http.route('/eterp_mesa_entrada_16/eterp_mesa_entrada_16/objects/<model("eterp_mesa_entrada_16.eterp_mesa_entrada_16"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eterp_mesa_entrada_16.object', {
#             'object': obj
#         })
