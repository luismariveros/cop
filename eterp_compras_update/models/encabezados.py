# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportEncabezado(models.Model):
    _name = "report.encabezado"
    _description = "Encabezados para Reportes"

    name = fields.Char("Nombre", required=True)
    active = fields.Boolean("Activo", default=True)
    predeterminado = fields.Boolean("Predeterminado", default=False)

    imagen_izquierda = fields.Binary("Imagen Izquierda")
    imagen_centro_izquierda = fields.Binary("Imagen Centro Izquierda")
    imagen_centro_derecha = fields.Binary("Imagen Centro Derecha")
    imagen_derecha = fields.Binary("Imagen Derecha")

    departamento = fields.Char(
        "Departamento", default="DEPARTAMENTO DE MARKETING Y COMUNICACIÓN"
    )

    # Al marcar como predeterminado, desmarca los demás
    @api.onchange("predeterminado")
    def _onchange_predeterminado(self):
        if self.predeterminado:
            encabezados = self.search(
                [("id", "!=", self._origin.id), ("predeterminado", "=", True)]
            )
            for encabezado in encabezados:
                encabezado.predeterminado = False
