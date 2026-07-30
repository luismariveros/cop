# For copyright and license notices, see __manifest__.py file in module root

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    ci = fields.Char(help='Cedula de Identidad', string='C.I.N°')
    ruc = fields.Char(help="Registro Unico de Contribuyentes", string='RUC', copy=False)
    nf = fields.Char(help="Nombre de Fantasía", string='Nombre Fantasía', copy=False)
    phone_2 = fields.Char(help="Numero de Teléfono", string='Teléfono 2')
    mobile_2 = fields.Char(help="Numero de Movil", string='Móvil 2')
    email_2 = fields.Char(help="Correo Electrónico 2", string="Correo electrónico")
    location = fields.Char(help="Enlace a la ubicación", string='Ubicación')
    # location_url = fields.Char(help="Enlace a la ubicación", string='Ubicación')
    # location_iframe = fields.Char(help="Iframe de google map", string='Insertar mapa')
    
    # @api.onchange("location")
    # def format_location(self):
    #     for rec in self:
    #         print(" rec=>>>>>>>>>", rec.location)
    #         rec.location = "url"