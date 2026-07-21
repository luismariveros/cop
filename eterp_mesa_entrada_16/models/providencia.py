from odoo import models, fields, api


class Providencia(models.Model):
    _name = "eterp.providencia"
    _description = "Providencias"
    _rec_name = "nombre"

    nombre = fields.Char(string="Nombre", required=True, translate=True)

    codigo = fields.Char(string="Código", required=True)

    descripcion = fields.Text(string="Descripción")

    activo = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ("codigo_unique", "unique(codigo)", "El código de providencia debe ser único")
    ]
