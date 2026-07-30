# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GestionOperacionalDocumento(models.Model):
    _name = "gestion.operacional.documento"
    _description = "Documentos Relacionados a Gestión Operacional"

    gestion_operacional_id = fields.Many2one(
        "gestion.operacional", string="Gestión Operacional", ondelete="cascade"
    )

    name = fields.Char(string="Nombre del Documento", required=True)
    descripcion = fields.Text(string="Descripción")
    fecha = fields.Date(string="Fecha", default=fields.Date.context_today)

    # Campo para adjuntar documento
    documento = fields.Binary(string="Documento", attachment=True)
    documento_filename = fields.Char(string="Nombre del archivo")

    # Tipo de documento
    tipo_documento = fields.Selection(
        [
            ("orden_compra", "Orden de Compra"),
            ("factura", "Factura"),
            ("contrato", "Contrato"),
            ("informe", "Informe"),
            ("otro", "Otro"),
        ],
        string="Tipo de Documento",
        default="otro",
        required=True,
    )

    # Estado del documento
    state = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("aprobado", "Aprobado"),
            ("rechazado", "Rechazado"),
        ],
        string="Estado",
        default="borrador",
    )

    # Responsable
    user_id = fields.Many2one(
        "res.users",
        string="Responsable",
        default=lambda self: self.env.user,
        tracking=True,
    )

    @api.model
    def create(self, vals):
        """Sobrescribe el método create para realizar acciones al crear un documento"""
        # Añadir lógica adicional aquí si es necesario
        return super(GestionOperacionalDocumento, self).create(vals)

    def action_aprobar(self):
        """Acción para aprobar el documento"""
        for record in self:
            record.state = "aprobado"

    def action_rechazar(self):
        """Acción para rechazar el documento"""
        for record in self:
            record.state = "rechazado"

    def action_borrador(self):
        """Acción para volver a borrador"""
        for record in self:
            record.state = "borrador"
