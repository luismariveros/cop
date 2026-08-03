# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrderDAFAuthorization(models.Model):
    _inherit = "purchase.order"

    daf_authorized = fields.Boolean(
        string="Autorizado por DAF",
        default=False,
        copy=False,
        readonly=True,
        help="Indica si esta orden ha sido autorizada por la Dirección de Administración y Finanzas",
    )

    daf_authorized_by = fields.Many2one(
        "res.users",
        string="Autorizado por",
        readonly=True,
        copy=False,
    )

    daf_authorized_date = fields.Datetime(
        string="Fecha de autorización",
        readonly=True,
        copy=False,
    )

    # Campos para seguimiento de solicitudes de autorización
    authorization_requested = fields.Boolean(
        string="Autorización Solicitada",
        default=False,
        copy=False,
        readonly=True,
        help="Indica si se ha solicitado la autorización para esta orden",
    )

    authorization_requested_by = fields.Many2one(
        "res.users",
        string="Solicitado por",
        readonly=True,
        copy=False,
    )

    authorization_requested_date = fields.Datetime(
        string="Fecha de solicitud",
        readonly=True,
        copy=False,
    )

    # Método para autorizar la orden por DAF
    def action_authorize_daf(self):
        self.ensure_one()

        # Verificar que el usuario pertenezca al grupo DAF
        if not self.env.user.has_group("compras_update.group_daf"):
            raise UserError(
                _(
                    "Solo los usuarios de la Dirección de Administración y Finanzas pueden autorizar órdenes de compra."
                )
            )

        # Actualizar los campos de autorización
        self.write(
            {
                "daf_authorized": True,
                "daf_authorized_by": self.env.user.id,
                "daf_authorized_date": fields.Datetime.now(),
            }
        )

        # Registrar el evento en el chatter
        self.message_post(
            body=_("Orden de compra autorizada por %s") % self.env.user.name,
            message_type="notification",
        )

        # Marcar como completadas las actividades relacionadas con la autorización
        activities = self.env["mail.activity"].search(
            [
                ("res_id", "=", self.id),
                ("res_model", "=", "purchase.order"),
                ("summary", "=", "Autorizar Orden de Compra"),
            ]
        )
        for activity in activities:
            activity.action_done()

        # Retornar una acción para recargar la vista
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    # Método para solicitar autorización a DAF
    def action_request_daf_authorization(self):
        self.ensure_one()

        # Verificar que la orden esté confirmada
        if self.state != "purchase":
            raise UserError(
                _("Solo se puede solicitar autorización para órdenes confirmadas.")
            )

        # Verificar que no esté ya autorizada
        if self.daf_authorized:
            raise UserError(_("Esta orden ya está autorizada."))

        # Verificar que no se haya solicitado autorización previamente
        if self.authorization_requested:
            raise UserError(_("Ya se ha solicitado autorización para esta orden."))

        # Actualizar campos de solicitud
        self.write(
            {
                "authorization_requested": True,
                "authorization_requested_by": self.env.user.id,
                "authorization_requested_date": fields.Datetime.now(),
            }
        )

        # Buscar usuarios del grupo DAF para asignarles actividades
        daf_users = self.env["res.users"].search(
            [("groups_id", "in", self.env.ref("compras_update.group_daf").id)]
        )

        if not daf_users:
            raise UserError(
                _(
                    "No se encontraron usuarios en el grupo DAF para asignar la actividad."
                )
            )

        # Crear actividades para los usuarios DAF
        for user in daf_users:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user.id,
                note=_(
                    "Se ha solicitado la autorización para la Orden de Compra %s por %s"
                )
                % (self.name, self.env.user.name),
                summary=_("Autorizar Orden de Compra"),
                date_deadline=fields.Date.today(),
            )

        # Registrar en el chatter
        self.message_post(
            body=_("Solicitud de autorización enviada a los usuarios DAF por %s")
            % self.env.user.name,
            message_type="notification",
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Solicitud Enviada"),
                "message": _(
                    "La solicitud de autorización ha sido enviada a los usuarios de DAF."
                ),
                "sticky": False,
                "type": "success",
            },
        }

    # Método para revocar la autorización DAF (solo para administradores)
    def action_revoke_daf_authorization(self):
        self.ensure_one()

        # Solo administradores pueden revocar la autorización
        if not self.env.user.has_group("base.group_system"):
            raise UserError(
                _("Solo los administradores pueden revocar una autorización DAF.")
            )

        # Revocar la autorización
        self.write(
            {
                "daf_authorized": False,
                "daf_authorized_by": False,
                "daf_authorized_date": False,
                "authorization_requested": False,
                "authorization_requested_by": False,
                "authorization_requested_date": False,
            }
        )

        # Registrar el evento en el chatter
        self.message_post(
            body=_("Autorización DAF revocada por %s") % self.env.user.name,
            message_type="notification",
        )

        # Retornar una acción para recargar la vista
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
