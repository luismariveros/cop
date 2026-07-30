from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
import base64
import os


class MesaEntradaExpediente(models.Model):
    _name = "eterp.mesa.entrada.expediente"
    _description = "Expediente de Mesa de Entrada"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"  # Campo a usar como nombre de registro

    # Campos de Cabecera
    name = fields.Char(
        string="Número de Expediente",
        required=True,
        copy=False,
        default="Nuevo",
        tracking=True,
        readonly=True,
    )

    fecha = fields.Datetime(
        string="Fecha y Hora",
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )

    fecha_hora_recepcion = fields.Datetime(
        string="Fecha y Hora de Recepción",
        tracking=True,
    )

    quien_recibe = fields.Char(
        string="Quién Recibe?",
        tracking=True,
    )

    es_externo = fields.Boolean(
        string="Es un externo?",
        default=False,
        tracking=True,
    )

    remitente = fields.Many2one(
        "res.partner",
        string="Remitente",
        tracking=True,
    )

    procede = fields.Many2one(
        "hr.department",
        string="Procedencia",
        tracking=True,
    )

    destinatario = fields.Many2one(
        "hr.employee",
        string="Destinatario",
        tracking=True,
    )

    tipo_documento = fields.Many2one(
        "eterp.tipo.documento",
        string="Tipo de Documento",
        tracking=True,
    )

    referencia = fields.Text(
        string="Referencia",
        tracking=True,
    )

    providencia = fields.Many2one(
        "eterp.providencia",
        string="Providencia",
        tracking=True,
    )

    asunto = fields.Text(
        string="Asunto",
        tracking=True,
    )

    oficina_destino = fields.Many2one(
        "hr.department",
        string="Oficina Destino",
        tracking=True,
    )

    departamento_actual = fields.Many2one(
        "hr.department",
        string="Departamento Actual",
        tracking=True,
        readonly=True,
    )

    historial_departamentos = fields.One2many(
        "eterp.historial.departamento",
        "expediente_id",
        string="Historial de Departamentos",
        readonly=True,
    )

    # Campos de Detalle
    observacion = fields.Text(
        string="Observación del Expediente",
        tracking=True,
    )

    cantidad_hojas = fields.Integer(
        string="Cantidad de Hojas",
        default=0,
        tracking=True,
    )

    # Estado del Expediente
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("to_daf", "Enviado a D.A.F."),
            ("in_daf_review", "En Revisión D.A.F."),
            ("back_to_mesa", "Devuelto a Mesa"),
            ("assigned", "Asignado a Destinatario"),
            ("in_progress", "En Proceso"),
            ("in_dept", "En Departamento"),
            ("done", "Completado"),
            ("cancelled", "Cancelado"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
        readonly=True,
    )

    # Documentos
    documento_ids = fields.One2many(
        "eterp.mesa.entrada.documento",
        "expediente_id",
        string="Documentos",
    )

    # Campos de auditoría
    creado_por = fields.Many2one(
        "res.users",
        string="Creado por",
        default=lambda self: self.env.user,
        readonly=True,
    )

    fecha_creacion = fields.Datetime(
        string="Fecha de Creación",
        default=fields.Datetime.now,
        readonly=True,
    )

    # Campos calculados de permisos
    can_edit = fields.Boolean(
        string="Puede Editar",
        compute="_compute_permissions",
        help="Campo técnico para saber si el usuario actual puede editar",
        store=False,
    )

    can_cancel = fields.Boolean(
        string="Puede Cancelar",
        compute="_compute_permissions",
        help="Campo técnico para saber si el usuario actual puede cancelar",
        store=False,
    )

    can_complete = fields.Boolean(
        string="Puede Completar",
        compute="_compute_permissions",
        help="Campo técnico para saber si el usuario actual puede completar",
        store=False,
    )

    can_reopen = fields.Boolean(
        string="Puede Reabrir",
        compute="_compute_permissions",
        help="Campo técnico para saber si el usuario actual puede reabrir",
        store=False,
    )

    # Métodos de permisos
    @api.depends("state", "departamento_actual", "destinatario")
    def _compute_permissions(self):
        for record in self:
            # Obtener usuario y empleado actual
            current_user = self.env.user
            current_employee = self.env["hr.employee"].search(
                [("user_id", "=", current_user.id)], limit=1
            )

            # Determinar si el usuario pertenece a Mesa de Entrada o DAF
            is_mesa_entrada = False
            is_daf = False

            if current_employee and current_employee.department_id:
                is_mesa_entrada = (
                    "mesa de entrada" in current_employee.department_id.name.lower()
                )
                is_daf = (
                    "administración y finanzas"
                    in current_employee.department_id.name.lower()
                    or "daf" in current_employee.department_id.name.lower()
                )

            # Verificar si es administrador
            is_admin = current_user.has_group("base.group_system")

            # Verificar si el expediente está en su departamento
            in_my_department = False
            if (
                current_employee
                and current_employee.department_id
                and record.departamento_actual
            ):
                in_my_department = (
                    current_employee.department_id.id == record.departamento_actual.id
                )

            # Verificar si está asignado a él
            assigned_to_me = False
            if current_employee and record.destinatario:
                assigned_to_me = current_employee.id == record.destinatario.id

            # Permiso para editar
            record.can_edit = (record.state not in ["done", "cancelled"]) and (
                is_admin
                or is_mesa_entrada
                or is_daf
                or in_my_department
                or assigned_to_me
            )

            # Permiso para cancelar y completar (solo Mesa de Entrada, DAF y admins)
            record.can_cancel = is_admin or is_mesa_entrada or is_daf
            record.can_complete = (
                is_admin or is_mesa_entrada or is_daf
            ) and record.state not in ["done", "cancelled"]

            # Permiso para reabrir (solo Mesa de Entrada, DAF y admins)
            record.can_reopen = (
                is_admin or is_mesa_entrada or is_daf
            ) and record.state in ["done", "cancelled"]

    def _is_editable(self):
        """
        Método auxiliar para determinar si el registro es editable por el usuario actual
        """
        self.ensure_one()

        # Si el expediente está completado o cancelado, nadie puede editar
        if self.state in ["done", "cancelled"]:
            return False

        # Obtener usuario y empleado actual
        current_user = self.env.user
        current_employee = self.env["hr.employee"].search(
            [("user_id", "=", current_user.id)], limit=1
        )

        # Si es administrador, siempre puede editar
        if current_user.has_group("base.group_system"):
            return True

        # Si no hay empleado asociado, no puede editar
        if not current_employee:
            return False

        # Si no hay departamento asociado, no puede editar
        if not current_employee.department_id:
            return False

        # Si pertenece a Mesa de Entrada o DAF, puede editar
        if (
            "mesa de entrada" in current_employee.department_id.name.lower()
            or "administración y finanzas"
            in current_employee.department_id.name.lower()
            or "daf" in current_employee.department_id.name.lower()
        ):
            return True

        # Si es el destinatario, puede editar
        if self.destinatario and self.destinatario.id == current_employee.id:
            return True

        # Si pertenece al departamento actual, puede editar
        if (
            self.departamento_actual
            and self.departamento_actual.id == current_employee.department_id.id
        ):
            return True

        # En cualquier otro caso, no puede editar
        return False

    def _check_department_access(self):
        """
        Verifica si el usuario actual pertenece al departamento correcto para realizar operaciones
        """
        current_user = self.env.user

        # Si es administrador, siempre puede realizar operaciones
        if current_user.has_group("base.group_system"):
            return True

        current_employee = self.env["hr.employee"].search(
            [("user_id", "=", current_user.id)], limit=1
        )

        # Si no hay empleado o departamento, no puede realizar operaciones
        if not current_employee or not current_employee.department_id:
            raise AccessError(
                "Necesita estar asociado a un empleado con departamento para realizar esta acción"
            )

        # Si pertenece a Mesa de Entrada o DAF, siempre puede realizar operaciones
        if (
            "mesa de entrada" in current_employee.department_id.name.lower()
            or "administración y finanzas"
            in current_employee.department_id.name.lower()
            or "daf" in current_employee.department_id.name.lower()
        ):
            return True

        # Si es el destinatario, puede realizar operaciones
        if self.destinatario and self.destinatario.id == current_employee.id:
            return True

        # Si pertenece al departamento actual, puede realizar operaciones
        if (
            self.departamento_actual
            and self.departamento_actual.id == current_employee.department_id.id
        ):
            return True

        raise AccessError(
            "No tiene permisos para realizar esta acción. Solo personal del departamento actual o destinatario asignado."
        )

    # Métodos de ciclo de vida y lógica de negocio
    @api.model
    def create(self, vals):
        # Generación de número de expediente
        if vals.get("name", "Nuevo") == "Nuevo":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("eterp.mesa.entrada.expediente")
                or "Nuevo"
            )

        return super(MesaEntradaExpediente, self).create(vals)

    @api.depends("es_externo")
    def es_external(self):
        if self.es_externo:
            self.procede = False

    def action_send_to_daf(self):
        """
        Método para enviar expediente a Dirección de Administración y Finanzas
        """
        for record in self:
            # Verificar que el estado actual sea "draft"
            if record.state != "draft":
                raise ValidationError(
                    "Solo se pueden enviar a D.A.F. expedientes en estado Borrador"
                )

            # Verificar permisos
            if not record._is_editable():
                raise AccessError(
                    "No tiene permisos para enviar este expediente a D.A.F."
                )

            # Obtener departamento DAF
            daf_department = self.env["hr.department"].search(
                [("name", "ilike", "administración y finanzas")], limit=1
            )

            if not daf_department:
                raise ValidationError(
                    "No se encontró el departamento de Dirección de Administración y Finanzas"
                )

            record.oficina_destino = daf_department.id
            record.departamento_actual = daf_department.id
            record.state = "to_daf"

            # Registro en historial
            self.env["eterp.historial.departamento"].create(
                {
                    "expediente_id": record.id,
                    "departamento_id": daf_department.id,
                    "fecha": fields.Date.today(),
                    "accion": "envio",
                    "observacion": f"Envío inicial a D.A.F.",
                }
            )

            # Notificar a los usuarios del departamento DAF
            self._notify_department_users(
                daf_department,
                f"Nuevo Expediente para revisar: {record.name}",
                f"Se ha enviado el expediente {record.name} para revisión de D.A.F.",
            )

            record.message_post(
                body=f"Expediente enviado a D.A.F. ({daf_department.name})",
                subject="Envío a D.A.F.",
            )

    def action_daf_review(self):
        """
        Método para que el director de DAF revise el expediente
        """
        for record in self:
            # Verificar que el estado actual sea "to_daf"
            if record.state != "to_daf":
                raise ValidationError(
                    "Solo se pueden revisar expedientes en estado 'Enviado a D.A.F.'"
                )

            # Verificar que el usuario actual pertenece a DAF
            current_employee = self.env["hr.employee"].search(
                [("user_id", "=", self.env.uid)], limit=1
            )

            if (
                not current_employee
                or not current_employee.department_id
                or not (
                    "administración y finanzas"
                    or "mesa de entrada" in current_employee.department_id.name.lower()
                    or "daf" in current_employee.department_id.name.lower()
                )
            ):
                raise ValidationError(
                    "Solo el personal del departamento D.A.F. puede realizar esta acción"
                )

            record.state = "in_daf_review"
            record.message_post(
                body=f"Expediente en revisión por D.A.F. (Usuario: {current_employee.name})",
                subject="En Revisión D.A.F.",
            )

    def action_return_to_mesa(self):
        """
        Método para que el director retorne el expediente a mesa de entrada
        """
        for record in self:
            # Verificar que el estado actual sea válido para retornar
            valid_states = ["in_daf_review", "in_progress", "in_dept"]
            if record.state not in valid_states:
                raise ValidationError(
                    f"Solo se pueden retornar expedientes en estado: {', '.join(valid_states)}"
                )

            # Verificar permisos de departamento
            record._check_department_access()

            # Buscar departamento de Mesa de Entrada
            mesa_entrada_dept = self.env["hr.department"].search(
                [("name", "ilike", "mesa de entrada")], limit=1
            )

            if not mesa_entrada_dept:
                raise ValidationError(
                    "No se encontró el departamento de Mesa de Entrada"
                )

            old_dept = (
                record.departamento_actual.name
                if record.departamento_actual
                else "Sin departamento"
            )
            record.departamento_actual = mesa_entrada_dept.id
            record.state = "back_to_mesa"

            # Registro en historial
            self.env["eterp.historial.departamento"].create(
                {
                    "expediente_id": record.id,
                    "departamento_id": mesa_entrada_dept.id,
                    "fecha": fields.Date.today(),
                    "accion": "retorno",
                    "observacion": f"Retorno desde {old_dept} a Mesa de Entrada",
                }
            )

            # Notificar a los usuarios de mesa de entrada
            self._notify_department_users(
                mesa_entrada_dept,
                f"Expediente retornado: {record.name}",
                f"El expediente {record.name} ha sido retornado a Mesa de Entrada",
            )

            record.message_post(
                body=f"Expediente retornado a Mesa de Entrada desde {old_dept}",
                subject="Retorno a Mesa de Entrada",
            )

    def action_assign_to_employee(self):
        """
        Método para asignar un expediente a un empleado
        """
        for record in self:
            # Verificar que el estado actual sea "back_to_mesa"
            if record.state != "back_to_mesa":
                raise ValidationError(
                    "Solo se pueden asignar expedientes en estado 'Devuelto a Mesa'"
                )

            # Verificar si el usuario es de mesa de entrada o daf
            current_employee = self.env["hr.employee"].search(
                [("user_id", "=", self.env.uid)], limit=1
            )

            if current_employee and current_employee.department_id:
                is_mesa_entrada = (
                    "mesa de entrada" in current_employee.department_id.name.lower()
                )
                is_daf = (
                    "administración y finanzas"
                    in current_employee.department_id.name.lower()
                    or "daf" in current_employee.department_id.name.lower()
                )
                is_admin = self.env.user.has_group("base.group_system")

                if not (is_mesa_entrada or is_daf or is_admin):
                    raise AccessError(
                        "Solo el personal de Mesa de Entrada o D.A.F. puede asignar expedientes a empleados"
                    )

            if not record.destinatario:
                raise ValidationError(
                    "Debe seleccionar un destinatario para asignar el expediente"
                )

            record.state = "assigned"

            # Registro en historial si el destinatario tiene departamento
            if record.destinatario.department_id:
                self.env["eterp.historial.departamento"].create(
                    {
                        "expediente_id": record.id,
                        "departamento_id": record.destinatario.department_id.id,
                        "fecha": fields.Date.today(),
                        "accion": "asignacion",
                        "observacion": f"Asignado a {record.destinatario.name}",
                    }
                )

            # Enviar mensaje de actividad al empleado asignado
            if record.destinatario.user_id:
                self.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=record.destinatario.user_id.id,
                    summary=f"Nuevo Expediente Asignado: {record.name}",
                    note=record.referencia or "Sin descripción adicional",
                )

            # Enviar mensaje de seguimiento
            record.message_post(
                body=f"Expediente asignado a {record.destinatario.name}",
                subject="Asignación de Expediente",
            )

    def action_receive_expediente(self):
        """
        Método para que el empleado reciba el expediente
        """
        for record in self:
            # Verificar que el estado actual sea "assigned"
            if record.state != "assigned":
                raise ValidationError(
                    "Solo se pueden recibir expedientes en estado 'Asignado a Destinatario'"
                )

            # Verificar que el empleado actual sea el destinatario
            current_employee = self.env["hr.employee"].search(
                [("user_id", "=", self.env.uid)], limit=1
            )

            if not current_employee:
                raise AccessError(
                    "Debe estar asociado a un empleado para recibir expedientes"
                )

            if record.destinatario != current_employee:
                raise ValidationError(
                    "Solo el empleado destinatario puede recibir este expediente"
                )

            record.state = "in_progress"

            # Si el empleado tiene departamento, actualizar departamento actual
            if current_employee.department_id:
                record.departamento_actual = current_employee.department_id.id

            record.message_post(
                body=f"Expediente recibido por {current_employee.name}",
                subject="Recepción de Expediente",
            )

    def action_assign_to_department(self):
        """
        Método para asignar expediente a otro departamento
        """
        for record in self:
            # Verificar que el estado actual sea válido
            valid_states = ["in_progress", "back_to_mesa", "in_dept"]
            if record.state not in valid_states:
                raise ValidationError(
                    f"Solo se pueden asignar a departamento expedientes en estados: {', '.join(valid_states)}"
                )

            # Verificar permisos
            if record.state == "back_to_mesa":
                # Solo Mesa de Entrada o DAF pueden asignar desde estado "back_to_mesa"
                current_employee = self.env["hr.employee"].search(
                    [("user_id", "=", self.env.uid)], limit=1
                )

                if current_employee and current_employee.department_id:
                    is_mesa_entrada = (
                        "mesa de entrada" in current_employee.department_id.name.lower()
                    )
                    is_daf = (
                        "administración y finanzas"
                        in current_employee.department_id.name.lower()
                        or "daf" in current_employee.department_id.name.lower()
                    )
                    is_admin = self.env.user.has_group("base.group_system")

                    if not (is_mesa_entrada or is_daf or is_admin):
                        raise AccessError(
                            "Solo el personal de Mesa de Entrada o D.A.F. puede asignar expedientes desde Mesa de Entrada"
                        )
            else:
                # Para otros estados, verificar permisos de departamento
                record._check_department_access()

            if not record.oficina_destino:
                raise ValidationError(
                    "Debe seleccionar una oficina destino para continuar"
                )

            old_dept = (
                record.departamento_actual.name
                if record.departamento_actual
                else "Sin departamento"
            )
            record.departamento_actual = record.oficina_destino.id
            record.state = "in_dept"

            # Registro en historial
            self.env["eterp.historial.departamento"].create(
                {
                    "expediente_id": record.id,
                    "departamento_id": record.oficina_destino.id,
                    "fecha": fields.Date.today(),
                    "accion": "asignacion",
                    "observacion": f"Trasladado desde {old_dept} a {record.oficina_destino.name}",
                }
            )

            # Notificar a los usuarios del departamento destino
            self._notify_department_users(
                record.oficina_destino,
                f"Expediente asignado: {record.name}",
                f"El expediente {record.name} ha sido asignado a su departamento",
            )

            record.message_post(
                body=f"Expediente asignado al departamento {record.oficina_destino.name}",
                subject="Asignación a Departamento",
            )

    def action_complete_expediente(self):
        """
        Método para completar el expediente
        """
        for record in self:
            # Verificar permisos
            if not record.can_complete:
                raise AccessError("No tiene permisos para completar este expediente")

            # Verificar estado válido
            valid_states = ["back_to_mesa", "in_progress", "in_dept"]
            if record.state not in valid_states:
                raise ValidationError(
                    f"Solo se pueden completar expedientes en estados: {', '.join(valid_states)}"
                )

            record.state = "done"
            record.message_post(
                body="Expediente completado", subject="Finalización de Expediente"
            )

    def action_cancel_expediente(self):
        """
        Método para cancelar el expediente
        """
        for record in self:
            # Verificar permisos
            if not record.can_cancel:
                raise AccessError("No tiene permisos para cancelar este expediente")

            # Verificar estado válido (no se pueden cancelar expedientes ya completados o cancelados)
            invalid_states = ["done", "cancelled"]
            if record.state in invalid_states:
                raise ValidationError(
                    f"No se pueden cancelar expedientes en estados: {', '.join(invalid_states)}"
                )

            record.state = "cancelled"
            record.message_post(
                body="Expediente cancelado", subject="Cancelación de Expediente"
            )

    def action_reopen_expediente(self):
        """
        Método para reabrir un expediente cancelado o completado
        """
        for record in self:
            # Verificar permisos
            if not record.can_reopen:
                raise AccessError("No tiene permisos para reabrir este expediente")

            # Verificar estado válido
            valid_states = ["done", "cancelled"]
            if record.state not in valid_states:
                raise ValidationError(
                    f"Solo se pueden reabrir expedientes en estados: {', '.join(valid_states)}"
                )

            record.state = "back_to_mesa"

            # Buscar departamento de Mesa de Entrada
            mesa_entrada_dept = self.env["hr.department"].search(
                [("name", "ilike", "mesa de entrada")], limit=1
            )

            if mesa_entrada_dept:
                record.departamento_actual = mesa_entrada_dept.id

                # Registro en historial
                self.env["eterp.historial.departamento"].create(
                    {
                        "expediente_id": record.id,
                        "departamento_id": mesa_entrada_dept.id,
                        "fecha": fields.Date.today(),
                        "accion": "reapertura",
                        "observacion": f"Expediente reabierto y asignado a Mesa de Entrada",
                    }
                )

            record.message_post(
                body="Expediente reabierto", subject="Reapertura de Expediente"
            )

    def _notify_department_users(self, department, subject, body):
        """
        Método auxiliar para notificar a todos los usuarios de un departamento
        """
        if not department:
            return

        # Buscar empleados del departamento que tengan un usuario asociado
        employees = self.env["hr.employee"].search(
            [("department_id", "=", department.id), ("user_id", "!=", False)]
        )

        for employee in employees:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=employee.user_id.id,
                summary=subject,
                note=body,
            )

    def action_open_asignar_empleado_wizard(self):
        self.ensure_one()

        # Verificar estado y permisos
        if self.state != "back_to_mesa":
            raise ValidationError(
                "Solo se pueden asignar empleados a expedientes en estado 'Devuelto a Mesa'"
            )

        # Verificar si el usuario es de mesa de entrada o daf
        current_employee = self.env["hr.employee"].search(
            [("user_id", "=", self.env.uid)], limit=1
        )

        if current_employee and current_employee.department_id:
            is_mesa_entrada = (
                "mesa de entrada" in current_employee.department_id.name.lower()
            )
            is_daf = (
                "administración y finanzas"
                in current_employee.department_id.name.lower()
                or "daf" in current_employee.department_id.name.lower()
            )
            is_admin = self.env.user.has_group("base.group_system")

            if not (is_mesa_entrada or is_daf or is_admin):
                raise AccessError(
                    "Solo el personal de Mesa de Entrada o D.A.F. puede asignar expedientes a empleados"
                )

        return {
            "name": "Asignar a Empleado",
            "type": "ir.actions.act_window",
            "res_model": "eterp.mesa.entrada.asignar.empleado.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_expediente_id": self.id},
        }

    def action_open_asignar_departamento_wizard(self):
        self.ensure_one()

        # Verificar estado válido
        valid_states = ["in_progress", "back_to_mesa", "in_dept"]
        if self.state not in valid_states:
            raise ValidationError(
                f"Solo se pueden asignar a departamento expedientes en estados: {', '.join(valid_states)}"
            )

        # Verificar permisos
        if self.state == "back_to_mesa":
            # Solo Mesa de Entrada o DAF pueden asignar desde estado "back_to_mesa"
            current_employee = self.env["hr.employee"].search(
                [("user_id", "=", self.env.uid)], limit=1
            )

            if current_employee and current_employee.department_id:
                is_mesa_entrada = (
                    "mesa de entrada" in current_employee.department_id.name.lower()
                )
                is_daf = (
                    "administración y finanzas"
                    in current_employee.department_id.name.lower()
                    or "daf" in current_employee.department_id.name.lower()
                )
                is_admin = self.env.user.has_group("base.group_system")

                if not (is_mesa_entrada or is_daf or is_admin):
                    raise AccessError(
                        "Solo el personal de Mesa de Entrada o D.A.F. puede asignar expedientes desde Mesa de Entrada"
                    )
        else:
            # Para otros estados, verificar permisos de departamento
            self._check_department_access()

        return {
            "name": "Asignar a Departamento",
            "type": "ir.actions.act_window",
            "res_model": "eterp.mesa.entrada.asignar.departamento.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_expediente_id": self.id},
        }

    def action_view_details(self):
        """
        Muestra un resumen detallado del estado actual del expediente
        usando un diálogo modal estilizado
        """
        self.ensure_one()

        state_labels = {
            "draft": "Borrador",
            "to_daf": "Enviado a D.A.F.",
            "in_daf_review": "En Revisión D.A.F.",
            "back_to_mesa": "Devuelto a Mesa",
            "assigned": "Asignado a Destinatario",
            "in_progress": "En Proceso",
            "in_dept": "En Departamento",
            "done": "Completado",
            "cancelled": "Cancelado",
        }

        # Crear contexto para la vista
        context = {
            "default_expediente_id": self.id,
            "default_nombre": self.name,
            "default_estado_actual": state_labels.get(self.state, self.state),
        }

        # Información adicional basada en el estado
        if self.state == "to_daf" or self.state == "in_daf_review":
            context["default_info_adicional"] = "Dirección de Administración y Finanzas"

        if self.state == "assigned" and self.destinatario:
            context["default_destinatario"] = self.destinatario.name
            if self.destinatario.department_id:
                context["default_dept_destinatario"] = (
                    self.destinatario.department_id.name
                )

        if self.state == "in_dept" and self.departamento_actual:
            context["default_departamento_actual"] = self.departamento_actual.name

        # Añadir información de quién recibe y fecha de recepción
        if self.quien_recibe:
            context["default_quien_recibe"] = self.quien_recibe

        if self.fecha_hora_recepcion:
            context["default_fecha_hora_recepcion"] = self.fecha_hora_recepcion

        # Historial para la vista de árbol
        historial_items = []
        if self.historial_departamentos:
            # Ordenar por fecha más reciente
            for hist in self.historial_departamentos.sorted("fecha", reverse=True)[:3]:
                accion_labels = {
                    "envio": "Envío a",
                    "recepcion": "Recepción en",
                    "asignacion": "Asignación a",
                    "retorno": "Retorno a",
                    "reapertura": "Reapertura en",
                }
                accion = accion_labels.get(hist.accion, hist.accion)
                historial_items.append(
                    {
                        "fecha": hist.fecha,
                        "accion": accion,
                        "departamento": hist.departamento_id.name,
                    }
                )

        # Usar json.dumps para serializar de manera más segura los datos del historial
        import json

        try:
            context["default_historial_items"] = json.dumps(historial_items)
            # Si hay historial, agregar un flag para mostrarlo
            context["default_tiene_historial"] = bool(historial_items)
        except:
            # Fallback al método original si json.dumps falla
            context["default_historial_items"] = str(historial_items)
            context["default_tiene_historial"] = bool(historial_items)

        # Obtener referencia a la vista
        view_id = self.env.ref(
            "eterp_mesa_entrada_16.view_expediente_details_wizard_form"
        ).id

        return {
            "name": f"Detalles de Expediente {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "eterp.expediente.details.wizard",
            "view_mode": "form",
            "view_id": view_id,
            "target": "new",
            "context": context,
            "flags": {"mode": "readonly"},  # Para asegurarnos de que todo sea readonly
        }


class HistorialDepartamento(models.Model):
    _name = "eterp.historial.departamento"
    _description = "Historial de Departamentos de Expediente"
    _order = "fecha desc, id desc"

    expediente_id = fields.Many2one(
        "eterp.mesa.entrada.expediente",
        string="Expediente",
        required=True,
        ondelete="cascade",
    )

    departamento_id = fields.Many2one(
        "hr.department",
        string="Departamento",
        required=True,
    )

    fecha = fields.Date(
        string="Fecha", default=fields.Date.context_today, required=True
    )

    accion = fields.Selection(
        [
            ("envio", "Envío"),
            ("recepcion", "Recepción"),
            ("asignacion", "Asignación"),
            ("retorno", "Retorno"),
            ("reapertura", "Reapertura"),
        ],
        string="Acción",
        required=True,
    )

    observacion = fields.Text(string="Observación")

    usuario_id = fields.Many2one(
        "res.users",
        string="Usuario",
        default=lambda self: self.env.user,
        readonly=True,
    )


class MesaEntradaDocumento(models.Model):
    _name = "eterp.mesa.entrada.documento"
    _description = "Documentos de Expediente"

    expediente_id = fields.Many2one(
        "eterp.mesa.entrada.expediente",
        string="Expediente",
        required=True,
        ondelete="cascade",
    )

    nombre = fields.Char(string="Nombre", required=True)

    documento = fields.Binary(string="Documento", required=True, attachment=True)

    nombre_archivo = fields.Char(
        string="Nombre de Archivo", help="Nombre del archivo original"
    )

    tipo_documento = fields.Selection(
        [
            ("pdf", "PDF"),
            ("doc", "Documento Word"),
            ("xls", "Hoja de Cálculo"),
            ("img", "Imagen"),
            ("otro", "Otro"),
        ],
        string="Tipo de Documento",
        compute="_compute_tipo_documento",
        store=True,
    )

    icono = fields.Selection(
        [
            ("pdf", "fa-file-pdf-o"),
            ("doc", "fa-file-word-o"),
            ("xls", "fa-file-excel-o"),
            ("img", "fa-file-image-o"),
            ("otro", "fa-file-o"),
        ],
        string="Ícono",
        compute="_compute_tipo_documento",
        store=True,
    )

    fecha_documento = fields.Date(
        string="Fecha del Documento", default=fields.Date.context_today
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribir el método create para manejar el nombre de archivo
        """
        for vals in vals_list:
            # Solo modificar nombre_archivo si no existe
            if not vals.get("nombre_archivo") and vals.get("documento"):
                # Intentar usar el nombre original del archivo si está presente
                if vals.get("nombre_archivo"):
                    # Si ya tiene nombre de archivo, no lo modificamos
                    continue

                # Usar el nombre como base para el nombre de archivo
                base_nombre = vals.get("nombre", "documento")

                # Intentar generar un nombre de archivo con extensión
                vals["nombre_archivo"] = base_nombre

        return super(MesaEntradaDocumento, self).create(vals_list)

    @api.depends("nombre_archivo")
    def _compute_tipo_documento(self):
        for record in self:
            if record.nombre_archivo:
                # Obtener la extensión del archivo
                extension = os.path.splitext(record.nombre_archivo)[1][1:].lower()

                # Mapear extensiones a tipos
                if extension == "pdf":
                    record.tipo_documento = "pdf"
                    record.icono = "pdf"
                elif extension in ["doc", "docx"]:
                    record.tipo_documento = "doc"
                    record.icono = "doc"
                elif extension in ["xls", "xlsx"]:
                    record.tipo_documento = "xls"
                    record.icono = "xls"
                elif extension in ["jpg", "jpeg", "png", "gif"]:
                    record.tipo_documento = "img"
                    record.icono = "img"
                else:
                    record.tipo_documento = "otro"
                    record.icono = "otro"
            else:
                record.tipo_documento = "otro"
                record.icono = "otro"

    def action_view_document(self):
        """
        Método para abrir el documento en el visor de Odoo
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content?model={self._name}&field=documento&id={self.id}&filename={self.nombre_archivo}",
            "target": "new",
        }
