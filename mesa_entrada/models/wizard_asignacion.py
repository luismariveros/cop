from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsignarEmpleadoWizard(models.TransientModel):
    _name = "eterp.mesa.entrada.asignar.empleado.wizard"
    _description = "Asistente para asignar expediente a empleado"

    expediente_id = fields.Many2one(
        "mesa.entrada.expediente",
        string="Expediente",
        default=lambda self: self.env.context.get("active_id"),
        readonly=True,
    )

    destinatario_id = fields.Many2one(
        "hr.employee",
        string="Empleado Destinatario",
        domain="[('user_id', '!=', False)]",
        required=True,
    )

    observacion = fields.Text(string="Observación")

    @api.onchange("destinatario_id")
    def _onchange_destinatario(self):
        if self.destinatario_id and self.destinatario_id.department_id:
            return {
                "value": {
                    "observacion": f"Asignación a {self.destinatario_id.name} del departamento {self.destinatario_id.department_id.name}"
                }
            }

    def action_asignar(self):
        self.ensure_one()
        expediente = self.expediente_id

        if not expediente:
            raise ValidationError("No se ha seleccionado un expediente")

        # Actualizar el expediente con el destinatario seleccionado
        expediente.write(
            {
                "destinatario": self.destinatario_id.id,
                "state": "assigned",
            }
        )

        # Registrar en historial si el destinatario tiene departamento
        if self.destinatario_id.department_id:
            self.env["historial.departamento"].create(
                {
                    "expediente_id": expediente.id,
                    "departamento_id": self.destinatario_id.department_id.id,
                    "fecha": fields.Date.today(),
                    "accion": "asignacion",
                    "observacion": self.observacion
                    or f"Asignado a {self.destinatario_id.name}",
                }
            )

        # Enviar mensaje de actividad al empleado asignado
        if self.destinatario_id.user_id:
            expediente.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.destinatario_id.user_id.id,
                summary=f"Nuevo Expediente Asignado: {expediente.name}",
                note=self.observacion or "Sin descripción adicional",
            )

        # Enviar mensaje de seguimiento
        expediente.message_post(
            body=f"Expediente asignado a {self.destinatario_id.name}"
            + (f"<br/>Observación: {self.observacion}" if self.observacion else ""),
            subject="Asignación de Expediente",
        )

        return {"type": "ir.actions.act_window_close"}


class AsignarDepartamentoWizard(models.TransientModel):
    _name = "eterp.mesa.entrada.asignar.departamento.wizard"
    _description = "Asistente para asignar expediente a departamento"

    expediente_id = fields.Many2one(
        "mesa.entrada.expediente",
        string="Expediente",
        default=lambda self: self.env.context.get("active_id"),
        readonly=True,
    )

    departamento_id = fields.Many2one(
        "hr.department",
        string="Departamento Destino",
        required=True,
    )

    observacion = fields.Text(string="Observación")

    @api.onchange("departamento_id")
    def _onchange_departamento(self):
        if self.departamento_id:
            return {
                "value": {
                    "observacion": f"Traslado al departamento {self.departamento_id.name}"
                }
            }

    def action_asignar(self):
        self.ensure_one()
        expediente = self.expediente_id

        if not expediente:
            raise ValidationError("No se ha seleccionado un expediente")

        old_dept = (
            expediente.departamento_actual.name
            if expediente.departamento_actual
            else "Sin departamento"
        )

        # Actualizar el expediente con el departamento seleccionado
        expediente.write(
            {
                "oficina_destino": self.departamento_id.id,
                "departamento_actual": self.departamento_id.id,
                "state": "in_dept",
            }
        )

        # Registro en historial
        self.env["historial.departamento"].create(
            {
                "expediente_id": expediente.id,
                "departamento_id": self.departamento_id.id,
                "fecha": fields.Date.today(),
                "accion": "asignacion",
                "observacion": self.observacion
                or f"Trasladado desde {old_dept} a {self.departamento_id.name}",
            }
        )

        # Notificar a los usuarios del departamento destino
        employees = self.env["hr.employee"].search(
            [("department_id", "=", self.departamento_id.id), ("user_id", "!=", False)]
        )

        for employee in employees:
            expediente.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=employee.user_id.id,
                summary=f"Expediente asignado: {expediente.name}",
                note=self.observacion
                or f"El expediente {expediente.name} ha sido asignado a su departamento",
            )

        # Enviar mensaje de seguimiento
        expediente.message_post(
            body=f"Expediente asignado al departamento {self.departamento_id.name}"
            + (f"<br/>Observación: {self.observacion}" if self.observacion else ""),
            subject="Asignación a Departamento",
        )

        return {"type": "ir.actions.act_window_close"}
