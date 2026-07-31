from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError


class MesaEntradaExpediente(models.Model):
    _inherit = "mesa.entrada.expediente"

    def check_group_permissions(self, required_groups=None, error_message=None):
        """
        Verifica si el usuario actual pertenece a alguno de los grupos especificados

        Args:
            required_groups: Lista de referencias XML ID de grupos permitidos
            error_message: Mensaje de error personalizado

        Returns:
            True si pertenece al menos a un grupo, False si no

        Raises:
            AccessError si no pertenece a ningún grupo y se ha definido un mensaje de error
        """
        if not required_groups:
            return True

        current_user = self.env.user

        # Administrador siempre tiene acceso
        if current_user.has_group("base.group_system"):
            return True

        # Verifica si el usuario pertenece a alguno de los grupos
        has_permission = False
        for group in required_groups:
            if current_user.has_group(group):
                has_permission = True
                break

        if not has_permission and error_message:
            raise AccessError(error_message)

        return has_permission

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

            # Verificar permisos de grupos
            record.check_group_permissions(
                ["eterp_mesa_entrada_16.group_mesa_entrada"],
                "Solo el personal de Mesa de Entrada puede enviar expedientes a D.A.F.",
            )

            # Resto del código original...
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
            self.env["historial.departamento"].create(
                {
                    "expediente_id": record.id,
                    "departamento_id": daf_department.id,
                    "fecha": fields.Date.today(),
                    "accion": "envio",
                    "observacion": f"Envío inicial a D.A.F.",
                }
            )

            # Notificar a los usuarios del departamento DAF
            record._notify_department_users(
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

            # Verificar permisos de grupos
            record.check_group_permissions(
                ["eterp_mesa_entrada_16.group_daf"],
                "Solo el personal de D.A.F. puede realizar esta acción",
            )

            record.state = "in_daf_review"
            record.message_post(
                body=f"Expediente en revisión por D.A.F. (Usuario: {self.env.user.name})",
                subject="En Revisión D.A.F.",
            )

    def action_complete_expediente(self):
        """
        Método para completar el expediente
        """
        for record in self:
            # Verificar estado válido
            valid_states = ["back_to_mesa", "in_progress", "in_dept"]
            if record.state not in valid_states:
                raise ValidationError(
                    f"Solo se pueden completar expedientes en estados: {', '.join(valid_states)}"
                )

            # Verificar permisos de grupos
            record.check_group_permissions(
                [
                    "eterp_mesa_entrada_16.group_mesa_entrada",
                    "eterp_mesa_entrada_16.group_daf",
                ],
                "Solo el personal de Mesa de Entrada o D.A.F. puede completar expedientes",
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
            # Verificar estado válido (no se pueden cancelar expedientes ya completados o cancelados)
            invalid_states = ["done", "cancelled"]
            if record.state in invalid_states:
                raise ValidationError(
                    f"No se pueden cancelar expedientes en estados: {', '.join(invalid_states)}"
                )

            # Verificar permisos de grupos
            record.check_group_permissions(
                [
                    "eterp_mesa_entrada_16.group_mesa_entrada",
                    "eterp_mesa_entrada_16.group_daf",
                ],
                "Solo el personal de Mesa de Entrada o D.A.F. puede cancelar expedientes",
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
            # Verificar estado válido
            valid_states = ["done", "cancelled"]
            if record.state not in valid_states:
                raise ValidationError(
                    f"Solo se pueden reabrir expedientes en estados: {', '.join(valid_states)}"
                )

            # Verificar permisos de grupos
            record.check_group_permissions(
                [
                    "eterp_mesa_entrada_16.group_mesa_entrada",
                    "eterp_mesa_entrada_16.group_daf",
                ],
                "Solo el personal de Mesa de Entrada o D.A.F. puede reabrir expedientes",
            )

            record.state = "back_to_mesa"

            # Buscar departamento de Mesa de Entrada
            mesa_entrada_dept = self.env["hr.department"].search(
                [("name", "ilike", "mesa de entrada")], limit=1
            )

            if mesa_entrada_dept:
                record.departamento_actual = mesa_entrada_dept.id

                # Registro en historial
                self.env["historial.departamento"].create(
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
