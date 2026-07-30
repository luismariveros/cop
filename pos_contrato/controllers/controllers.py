# -*- coding: utf-8 -*-
# from odoo import http


# class EterpPosContrato(http.Controller):
#     @http.route('/eterp_pos_contrato/eterp_pos_contrato', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eterp_pos_contrato/eterp_pos_contrato/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('eterp_pos_contrato.listing', {
#             'root': '/eterp_pos_contrato/eterp_pos_contrato',
#             'objects': http.request.env['eterp_pos_contrato.eterp_pos_contrato'].search([]),
#         })

#     @http.route('/eterp_pos_contrato/eterp_pos_contrato/objects/<model("eterp_pos_contrato.eterp_pos_contrato"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eterp_pos_contrato.object', {
#             'object': obj
#         })
