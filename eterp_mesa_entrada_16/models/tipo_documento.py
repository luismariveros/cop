from odoo import models, fields, api


class TipoDocumento(models.Model):
    _name = "eterp.tipo.documento"
    _description = "Tipos de Documento"
    _rec_name = "nombre"

    nombre = fields.Char(string="Nombre", required=True, translate=True)

    codigo = fields.Char(string="Código", required=True)

    descripcion = fields.Text(string="Descripción")

    activo = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        (
            "codigo_unique",
            "unique(codigo)",
            "El código de tipo de documento debe ser único",
        )
    ]
