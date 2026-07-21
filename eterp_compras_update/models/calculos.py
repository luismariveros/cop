# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Método para calcular los saldos del saldo_monto_obligado, tiene que ir restando proyecto_monto_obligado - todos las ordenes de compras confirmadas de ese proyecto
    @api.depends("proyect_id", "state")
    def _compute_saldo_monto_obligado(self):
        for order in self:
            monto_obligado = 0.0

            # Inicializar valores por defecto
            order.saldo_monto_obligado = monto_obligado

            # Solo realizar la búsqueda si tiene un proyecto seleccionado
            if order.proyect_id:
                try:
                    # Construir dominio para buscar órdenes confirmadas
                    domain = [
                        ("proyect_id", "=", order.proyect_id.id),
                        ("state", "in", ["purchase", "done"]),
                    ]

                    _logger.info(f"Cálculo de montos obligados - Dominio: {domain}")
                    otras_ordenes = self.env["purchase.order"].search(domain)
                    _logger.info(f"Órdenes encontradas: {len(otras_ordenes)}")

                    # Sumar los montos de las órdenes encontradas
                    for otra_orden in otras_ordenes:
                        _logger.info(
                            f"Orden: {otra_orden.name}, Monto: {otra_orden.amount_total}"
                        )
                        monto_obligado += otra_orden.amount_total

                    order.saldo_monto_obligado = (
                        self.proyecto_monto_obligado - monto_obligado
                    )
                    _logger.info(f"Monto obligado: {monto_obligado}")
                except Exception as e:
                    _logger.error(f"Error al calcular montos obligados: {e}")

    # Método mejorado para calcular saldos de objetos de gasto
    @api.depends("proyect_id", "objetos_gasto_proyecto_ids", "state")
    def _compute_objetos_gasto_display(self):
        """Genera una vista HTML detallada de los objetos de gasto del proyecto con saldos actualizados"""
        _logger.info("Computing objetos gasto display")
        for order in self:
            _logger.info(f"Procesando orden: {order.name}")
            if not order.proyect_id or not order.objetos_gasto_proyecto_ids:
                order.objetos_gasto_display = False
                continue

            html = '<div class="o_objetos_gasto_container">'

            for objeto in order.objetos_gasto_proyecto_ids:
                _logger.info(
                    f"Procesando objeto de gasto: {objeto.objeto_gasto_id.name}"
                )
                # Buscar todas las órdenes confirmadas
                domain = [
                    ("proyect_id", "=", order.proyect_id.id),
                    ("state", "in", ["purchase", "done"]),
                ]

                _logger.info(f"Buscando órdenes con dominio: {domain}")

                # Buscar órdenes que cumplan con el criterio
                otras_ordenes = self.env["purchase.order"].search(domain)

                # Inicializar monto utilizado
                monto_utilizado = 0.0

                # Sumar los montos de las líneas de compra con este objeto de gasto
                for otra_orden in otras_ordenes:
                    for linea in otra_orden.order_line:
                        if (
                            linea.objeto_gasto_id
                            and linea.objeto_gasto_id.id == objeto.id
                        ):
                            _logger.info(
                                f"Orden: {otra_orden.name}, Línea con objeto de gasto {objeto.objeto_gasto_id.name}, Subtotal: {linea.price_subtotal}"
                            )
                            monto_utilizado += linea.price_subtotal

                # Calcular saldo
                monto_asignado = objeto.importe or 0.0
                saldo = monto_asignado - monto_utilizado

                # Color del saldo según disponibilidad
                color_class = "text-success" if saldo > 0 else "text-danger"

                # Formatear los valores monetarios
                formatted_asignado = "{:,.0f}".format(monto_asignado).replace(",", ".")
                formatted_utilizado = "{:,.0f}".format(monto_utilizado).replace(
                    ",", "."
                )
                formatted_saldo = "{:,.0f}".format(saldo).replace(",", ".")

                # Obtener nombre del objeto de gasto
                nombre_objeto = objeto.objeto_gasto_id.name
                descripcion = objeto.descripcion or ""

                # Construir la tarjeta HTML para este objeto de gasto
                html += f"""
                <div class="o_objeto_gasto_card mb-2" style="border: 1px solid #ddd; border-radius: 4px; padding: 8px;">
                    <div class="d-flex justify-content-between">
                        <strong>{nombre_objeto}</strong>
                        <span class="badge badge-pill {color_class}">{formatted_saldo} ₲</span>
                    </div>
                    <div style="font-size: 0.85em; color: #666;">{descripcion}</div>
                    <div class="row mt-1">
                        <div class="col-4">
                            <small class="text-muted">Asignado:</small>
                            <div>{formatted_asignado} ₲</div>
                        </div>
                        <div class="col-4">
                            <small class="text-muted">Utilizado:</small>
                            <div>{formatted_utilizado} ₲</div>
                        </div>
                        <div class="col-4">
                            <small class="text-muted">Saldo:</small>
                            <div class="{color_class}">{formatted_saldo} ₲</div>
                        </div>
                    </div>
                </div>
                """

            html += "</div>"
            order.objetos_gasto_display = html

    # Método mejorado para calcular montos de objeto de gasto seleccionado
    @api.depends("objeto_gasto_id", "proyect_id", "state")
    def _compute_objeto_gasto_montos(self):
        for order in self:
            monto_asignado = order.objeto_gasto_monto_asignado or 0.0
            monto_utilizado = 0.0

            # Inicializar valores por defecto
            order.objeto_gasto_monto_utilizado = monto_utilizado
            order.objeto_gasto_saldo = monto_asignado - monto_utilizado

            # Solo realizar la búsqueda si tiene un proyecto y objeto de gasto seleccionado
            if order.objeto_gasto_id and order.proyect_id:
                try:
                    # Construir dominio para buscar órdenes confirmadas
                    domain = [
                        ("proyect_id", "=", order.proyect_id.id),
                        ("state", "in", ["purchase", "done"]),
                    ]

                    _logger.info(f"Cálculo de montos objeto gasto - Dominio: {domain}")
                    otras_ordenes = self.env["purchase.order"].search(domain)
                    _logger.info(f"Órdenes encontradas: {len(otras_ordenes)}")

                    # Sumar los montos de las líneas de órdenes con este objeto de gasto
                    for otra_orden in otras_ordenes:
                        for linea in otra_orden.order_line:
                            if (
                                linea.objeto_gasto_id
                                and linea.objeto_gasto_id.id == order.objeto_gasto_id.id
                            ):
                                _logger.info(
                                    f"Orden: {otra_orden.name}, Línea con objeto de gasto {order.objeto_gasto_id.objeto_gasto_id.name}, Subtotal: {linea.price_subtotal}"
                                )
                                monto_utilizado += linea.price_subtotal

                    order.objeto_gasto_monto_utilizado = monto_utilizado
                    order.objeto_gasto_saldo = monto_asignado - monto_utilizado
                    _logger.info(
                        f"Monto utilizado: {monto_utilizado}, Saldo: {monto_asignado - monto_utilizado}"
                    )
                except Exception as e:
                    _logger.error(f"Error al calcular montos de objeto de gasto: {e}")

    # Método mejorado para calcular montos del proveedor
    @api.depends("partner_id", "proyect_id", "state")
    def _compute_proveedor_montos(self):
        for order in self:
            monto_asignado = 0.0
            monto_utilizado = 0.0

            # Inicializar valores por defecto
            order.proveedor_monto_asignado = monto_asignado
            order.proveedor_monto_utilizado = monto_utilizado
            order.proveedor_saldo = monto_asignado - monto_utilizado

            # Solo realizar la búsqueda si tiene un proyecto y proveedor seleccionado
            if order.partner_id and order.proyect_id:
                try:
                    # Buscar el proveedor en el proyecto
                    proveedor_proyecto = self.env["project.proveedor"].search(
                        [
                            ("project_id", "=", order.proyect_id.id),
                            ("partner_id", "=", order.partner_id.id),
                        ],
                        limit=1,
                    )

                    if proveedor_proyecto:
                        monto_asignado = proveedor_proyecto.importe_total

                        # Construir dominio para buscar órdenes confirmadas de este proveedor
                        domain = [
                            ("proyect_id", "=", order.proyect_id.id),
                            ("partner_id", "=", order.partner_id.id),
                            ("state", "in", ["purchase", "done"]),
                        ]

                        # No incluir la orden actual si ya existe
                        if not isinstance(order.id, models.NewId) and order.id:
                            domain.append(("id", "!=", order.id))

                        _logger.info(f"Cálculo de montos proveedor - Dominio: {domain}")
                        otras_ordenes = self.env["purchase.order"].search(domain)
                        _logger.info(
                            f"Órdenes de proveedor encontradas: {len(otras_ordenes)}"
                        )

                        # Sumar los montos de las órdenes encontradas
                        for otra_orden in otras_ordenes:
                            _logger.info(
                                f"Orden: {otra_orden.name}, Monto: {otra_orden.amount_total}"
                            )
                            monto_utilizado += otra_orden.amount_total

                    order.proveedor_monto_asignado = monto_asignado
                    order.proveedor_monto_utilizado = monto_utilizado
                    order.proveedor_saldo = monto_asignado - monto_utilizado
                    _logger.info(
                        f"Proveedor - Asignado: {monto_asignado}, Utilizado: {monto_utilizado}, Saldo: {monto_asignado - monto_utilizado}"
                    )
                except Exception as e:
                    _logger.error(f"Error al calcular montos de proveedor: {e}")

    # Método adicional para forzar el recálculo de montos cuando cambia el proyecto
    @api.onchange("proyect_id")
    def _onchange_proyect_id_recalculate(self):
        if self.proyect_id:
            # Forzar recálculo de montos al cambiar el proyecto
            self._compute_objetos_gasto_proyecto()
            self._compute_objetos_gasto_display()
            self._compute_objeto_gasto_montos()
            self._compute_proveedor_montos()


class PurchaseOrderHooks(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        result = super(PurchaseOrderHooks, self).button_confirm()
        # Forzar la actualización de montos utilizados y saldos en todas las órdenes activas
        self._update_all_order_balances()
        return result

    # Método para actualizar los saldos en todas las órdenes de compra activas
    def _update_all_order_balances(self):
        """
        Este método actualiza los saldos de todas las órdenes de compra activas
        que pertenecen al mismo proyecto que la orden actual.
        """
        if not self.proyect_id:
            return

        try:
            # Buscar todas las órdenes activas (borrador) del mismo proyecto
            active_orders = self.env["purchase.order"].search(
                [
                    ("proyect_id", "=", self.proyect_id.id),
                    ("state", "=", "draft"),
                ]
            )

            _logger.info(f"Actualizando saldos en {len(active_orders)} órdenes activas")

            # Limpiar caché global para todas las órdenes
            self.env.clear_cache()

            # Forzar el recálculo de campos calculados en cada orden
            for order in active_orders:
                # Invalidar caché específica de esta orden
                order.invalidate_cache()

                # Forzar recálculo directo de los campos computados
                order._compute_objetos_gasto_display()
                order._compute_objeto_gasto_montos()
                order._compute_proveedor_montos()

            # Commit para asegurar que los cambios se guarden
            self.env.cr.commit()

        except Exception as e:
            _logger.error(f"Error al actualizar saldos en órdenes activas: {e}")

    # Método que se ejecuta después de escribir un registro
    def write(self, vals):
        result = super(PurchaseOrderHooks, self).write(vals)

        # Si cambió el estado o el monto, actualizar saldos
        if "state" in vals or "amount_total" in vals or "order_line" in vals:
            self._update_all_order_balances()

        return result

    # Acción para forzar la actualización manual de saldos
    def action_refresh_balances(self):
        """
        Acción para forzar la actualización manual de saldos.
        """
        self.ensure_one()

        # Recalcular saldos para esta orden
        self.invalidate_cache()
        self._compute_objetos_gasto_display()
        self._compute_objeto_gasto_montos()
        self._compute_proveedor_montos()

        # También actualizar otras órdenes relacionadas
        self._update_all_order_balances()

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    # Método para permitir la vista previa de la OC antes de pedir confirmación
    def action_preview_order(self):
        """
        Acción para mostrar una vista previa de la orden de compra
        antes de solicitar su confirmación.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "flags": {"mode": "readonly"},
            "context": {"preview_mode": True},
        }

    # Método para solicitar confirmación al director
    def action_request_confirmation(self):
        """
        Solicita confirmación al Director para esta orden de compra.
        """
        self.ensure_one()

        # Enviar notificación al Director (DAF)
        user_ids = self.env["res.users"].search(
            [("groups_id", "in", self.env.ref("purchase.group_purchase_manager").id)]
        )

        if user_ids:
            partner_ids = user_ids.mapped("partner_id.id")

            # Crear registro de actividad para notificar
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user_ids[0].id,
                note=f"Se requiere su confirmación para la Orden de Compra {self.name}",
                summary="Confirmar Orden de Compra",
            )

            # También enviar mensaje en el chat
            self.message_post(
                body=f"<p>Se ha solicitado confirmación para esta Orden de Compra.</p>",
                partner_ids=partner_ids,
                message_type="notification",
                subtype_id=self.env.ref("mail.mt_note").id,
            )

        return True


class PurchaseOrderCreate(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        """Sobrescribir create para asegurar saldos correctos desde el inicio"""
        record = super(PurchaseOrderCreate, self).create(vals)

        # Forzar cálculo de saldos inmediatamente
        record.invalidate_cache()
        record._compute_objetos_gasto_display()
        record._compute_objeto_gasto_montos()
        record._compute_proveedor_montos()

        return record
