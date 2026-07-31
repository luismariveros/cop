from odoo import models, fields, api
import json


class ExpedienteDetailsWizard(models.TransientModel):
    _name = "expediente.details.wizard"
    _description = "Detalles de Expediente"

    expediente_id = fields.Many2one(
        "mesa.entrada.expediente", string="Expediente", readonly=True
    )
    nombre = fields.Char(string="Número de Expediente", readonly=True)
    estado_actual = fields.Char(string="Estado Actual", readonly=True)
    info_adicional = fields.Char(string="Información Adicional", readonly=True)
    destinatario = fields.Char(string="Destinatario Asignado", readonly=True)
    dept_destinatario = fields.Char(
        string="Departamento del Destinatario", readonly=True
    )
    departamento_actual = fields.Char(string="Departamento Actual", readonly=True)

    # Nuevos campos para recepción
    quien_recibe = fields.Char(string="Quién Recibe", readonly=True)
    fecha_hora_recepcion = fields.Datetime(
        string="Fecha y Hora de Recepción", readonly=True
    )

    # Campos para el historial
    historial_ids = fields.One2many(
        "expediente.details.historial", "wizard_id", string="Historial"
    )

    # Flag para controlar la visualización del historial
    tiene_historial = fields.Boolean(string="Tiene Historial", default=False)

    @api.model
    def default_get(self, fields_list):
        res = super(ExpedienteDetailsWizard, self).default_get(fields_list)

        # Si tenemos historial_items en el contexto
        if "default_historial_items" in self.env.context:
            try:
                # Uso de json.loads en lugar de eval para mayor seguridad
                historial_str = self.env.context.get("default_historial_items", "[]")

                # Intentar primero con json.loads, pero si falla, usar eval con seguridad
                try:
                    historial_items = json.loads(historial_str)
                except:
                    # Fallback a eval, pero con precaución
                    historial_items = eval(historial_str)

                historial_vals = []

                for item in historial_items:
                    historial_vals.append(
                        {
                            "fecha": item.get("fecha"),
                            "accion": item.get("accion"),
                            "departamento": item.get("departamento"),
                        }
                    )

                if historial_vals:
                    res["historial_ids"] = [(0, 0, val) for val in historial_vals]
                    res["tiene_historial"] = True

            except Exception as e:
                # Log del error para facilitar depuración
                import logging

                _logger = logging.getLogger(__name__)
                _logger.error(f"Error al procesar historial: {e}")
                _logger.error(
                    f"Contenido recibido: {self.env.context.get('default_historial_items', 'Vacío')}"
                )
                pass

        return res


class ExpedienteDetailsHistorial(models.TransientModel):
    _name = "expediente.details.historial"
    _description = "Línea de Historial de Expediente"
    _order = "fecha desc"

    wizard_id = fields.Many2one(
        "expediente.details.wizard", string="Wizard", ondelete="cascade"
    )
    fecha = fields.Date(string="Fecha")
    accion = fields.Char(string="Acción")
    departamento = fields.Char(string="Departamento")
