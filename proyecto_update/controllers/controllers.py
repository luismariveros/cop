# -*- coding: utf-8 -*-
# from odoo import http


# class EterpProyectoUpdate(http.Controller):
#     @http.route('/eterp_proyecto_update/eterp_proyecto_update', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eterp_proyecto_update/eterp_proyecto_update/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('eterp_proyecto_update.listing', {
#             'root': '/eterp_proyecto_update/eterp_proyecto_update',
#             'objects': http.request.env['eterp_proyecto_update.eterp_proyecto_update'].search([]),
#         })

#     @http.route('/eterp_proyecto_update/eterp_proyecto_update/objects/<model("eterp_proyecto_update.eterp_proyecto_update"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eterp_proyecto_update.object', {
#             'object': obj
#         })
