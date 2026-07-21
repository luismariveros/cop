# -*- coding: utf-8 -*-
# from odoo import http


# class EterpGestionOperacional(http.Controller):
#     @http.route('/eterp_gestion_operacional/eterp_gestion_operacional', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eterp_gestion_operacional/eterp_gestion_operacional/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('eterp_gestion_operacional.listing', {
#             'root': '/eterp_gestion_operacional/eterp_gestion_operacional',
#             'objects': http.request.env['eterp_gestion_operacional.eterp_gestion_operacional'].search([]),
#         })

#     @http.route('/eterp_gestion_operacional/eterp_gestion_operacional/objects/<model("eterp_gestion_operacional.eterp_gestion_operacional"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eterp_gestion_operacional.object', {
#             'object': obj
#         })
