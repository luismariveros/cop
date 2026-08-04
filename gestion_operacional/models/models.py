# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from pytz import timezone, UTC
from datetime import datetime


class GestionOperacional(models.Model):
    _name = "gestion.operacional"
    _description = "Gestión Operacional"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "expediente"

    proyecto_id = fields.Many2one("project.project", string="Proyecto")
    fecha = fields.Date(string="Fecha")
    area_solicitante = fields.Many2one("hr.department", string="Área Solicitante")

    # Nuevo campo para número de formulario
    nro_formulario = fields.Char(string="Nro. de Formulario", tracking=True)

    # Cambiado a no requerido
    expediente_id = fields.Many2one(
        "mesa.entrada.expediente",
        string="Expediente",
        required=False,
        tracking=True,
    )

    # Campo calculado para mantener compatibilidad con código existente
    expediente = fields.Char(
        string="Número de Expediente",
        related="expediente_id.name",
        store=True,
        readonly=True,
    )

    fecha_recepcion_expediente = fields.Datetime(
        string="Fecha de Recepción del Expediente",
        related="expediente_id.fecha",
        store=True,
        readonly=True,
    )

    fecha_recepcion_expediente_gmt3 = fields.Char(
        string="Fecha Recepción",
        compute="_compute_fecha_recepcion_gmt3",
        store=False,  # opcional: puedes ponerlo en True si lo deseas almacenar
    )

    destino = fields.Char(string="Destino")

    @api.depends("fecha_recepcion_expediente")
    def _compute_fecha_recepcion_gmt3(self):
        gmt3 = timezone("America/Asuncion")
        for record in self:
            fecha_utc = record.fecha_recepcion_expediente
            if fecha_utc:
                if fecha_utc.tzinfo is None:
                    fecha_utc = UTC.localize(fecha_utc)
                fecha_gmt3 = fecha_utc.astimezone(gmt3)
                record.fecha_recepcion_expediente_gmt3 = fecha_gmt3.strftime(
                    "%d/%m/%Y %H:%M"
                )
            else:
                record.fecha_recepcion_expediente_gmt3 = ""

    # Dominio dinámico para proveedor_id
    proveedor_id = fields.Many2one(
        "project.proveedor",
        string="Proveedor",
    )

    ruc_proveedor = fields.Char(
        string="RUC del Proveedor", compute="_compute_proveedor_ruc"
    )

    proveedor_name = fields.Char(
        "Nombre del Proveedor", compute="_compute_proveedor_name"
    )

    monto = fields.Float(string="Monto Solicitado")

    # Dominio dinámico para objeto_gasto_detalle_id
    objeto_gasto_detalle_id = fields.Many2one(
        "project.objeto.gasto",
        string="Detalle de Objeto de Gasto",
    )

    # Campo para monto total del proyecto (existente)
    monto_total_proyecto = fields.Float(
        string="Monto Total del Proyecto", compute="_compute_monto_total_proyecto"
    )

    # Nuevos campos para seguimiento financiero
    monto_utilizado = fields.Float(
        string="Monto Utilizado", compute="_compute_monto_utilizado", store=True
    )

    saldo_disponible = fields.Float(
        string="Saldo Disponible", compute="_compute_saldo_disponible", store=True
    )

    # Relaciones separadas para cada tipo de control
    control_839_ids = fields.One2many(
        "gestion.control.839", "gestion_operacional_id", string="Controles OG 839"
    )

    control_879_ids = fields.One2many(
        "gestion.control.879", "gestion_operacional_id", string="Controles OG 879"
    )

    # Método onchange para actualizar dominios cuando cambia el proyecto
    @api.onchange("proyecto_id")
    def _onchange_proyecto_id(self):
        # Reiniciar los campos relacionados cuando cambia el proyecto
        self.proveedor_id = False
        self.objeto_gasto_detalle_id = False

        # Actualizar los dominios
        if not self.proyecto_id:
            return {
                "domain": {
                    "proveedor_id": [],
                    "objeto_gasto_detalle_id": [],
                }
            }

        # Dominios específicos por proyecto
        return {
            "domain": {
                # Filtrar proveedores relacionados con el proyecto actual
                "proveedor_id": [("project_id", "=", self.proyecto_id.id)],
                # Filtrar objetos de gasto relacionados con el proyecto actual
                "objeto_gasto_detalle_id": [("project_id", "=", self.proyecto_id.id)],
            }
        }

    lineas_detalle_ids = fields.One2many(
        "gestion.operacional.line", "gestion_operacional_id", string="Líneas de Detalle"
    )

    # Nueva relación con documentos relacionados
    documento_ids = fields.One2many(
        "gestion.operacional.documento", "gestion_operacional_id", string="Documentos"
    )

    # Nuevos campos para órdenes de compra y facturas relacionadas
    purchase_order_ids = fields.One2many(
        "purchase.order",
        compute="_compute_purchase_orders",
        string="Órdenes de Compra",
        store=False,
    )

    invoice_ids = fields.One2many(
        "account.move",
        compute="_compute_invoices",
        string="Facturas",
        store=False,
    )

    # Contadores para mostrar en la vista
    purchase_order_count = fields.Integer(
        string="Cantidad de Órdenes", compute="_compute_purchase_orders_count"
    )

    invoice_count = fields.Integer(
        string="Cantidad de Facturas", compute="_compute_invoices_count"
    )

    state = fields.Selection(
        [("borrador", "Borrador"), ("confirmado", "Confirmado")],
        string="Estado",
        default="borrador",
        tracking=True,
    )

    logo_1 = fields.Image(string="Logo 1", related="logo_id.logo_1", readonly=True)
    logo_2 = fields.Image(string="Logo 2", related="logo_id.logo_2", readonly=True)
    logo_3 = fields.Image(string="Logo 3", related="logo_id.logo_3", readonly=True)
    logo_4 = fields.Image(string="Logo 4", related="logo_id.logo_4", readonly=True)

    logo_id = fields.Many2one(
        "gestion.operacional.logo",
        string="Configuración de Logos",
        default=lambda self: self._default_logo(),
    )

    @api.depends("proveedor_id")
    def _compute_proveedor_name(self):
        for record in self:
            record.proveedor_name = (
                record.proveedor_id.partner_id.name if record.proveedor_id else False
            )

    @api.depends("proveedor_id")
    def _compute_proveedor_ruc(self):
        for record in self:
            if record.proveedor_id:
                record.ruc_proveedor = record.proveedor_id.partner_id.ruc
            else:
                record.ruc_proveedor = ""

    @api.model
    def _default_logo(self):
        return self.env["gestion.operacional.logo"].search([], limit=1)

    @api.depends("proyecto_id")
    def _compute_monto_total_proyecto(self):
        for record in self:
            record.monto_total_proyecto = (
                record.proyecto_id.monto_total if record.proyecto_id else 0.0
            )

    @api.depends("proyecto_id")
    def _compute_monto_utilizado(self):
        """Calcula el monto utilizado sumando todos los montos solicitados
        que pertenecen al mismo proyecto (excepto el registro actual)"""
        for record in self:
            if record.proyecto_id:
                # Buscar todos los registros confirmados del mismo proyecto (excepto el actual)
                domain = [
                    ("proyecto_id", "=", record.proyecto_id.id),
                    ("state", "=", "confirmado"),
                ]
                if record.id:  # Si el registro ya está guardado, excluirlo
                    domain.append(("id", "!=", record.id))

                # Sumar todos los montos solicitados
                otros_registros = self.env["gestion.operacional"].search(domain)
                record.monto_utilizado = sum(otros_registros.mapped("monto"))
            else:
                record.monto_utilizado = 0.0

    @api.depends("monto_total_proyecto", "monto_utilizado")
    def _compute_saldo_disponible(self):
        """Calcula el saldo disponible restando el monto utilizado del monto total del proyecto"""
        for record in self:
            record.saldo_disponible = (
                record.monto_total_proyecto - record.monto_utilizado
            )

    @api.depends("proyecto_id", "proveedor_id")
    def _compute_purchase_orders(self):
        for record in self:

            print("buscando ordenes para el proyecto y proveedor")
            print("proyecto_id", record.proyecto_id.id if record.proyecto_id else False)
            print(
                "proveedor_id",
                record.proveedor_id.partner_id.id if record.proveedor_id else False,
            )

            if (
                record.proyecto_id
                and record.proveedor_id
                and record.proveedor_id.partner_id
            ):
                purchase_order = self.env["purchase.order"].search(
                    [
                        ("partner_id", "=", record.proveedor_id.partner_id.id),
                        ("proyect_id", "=", record.proyecto_id.id),
                    ],
                    order="date_order desc",
                )
                record.purchase_order_ids = purchase_order
                print(
                    f"Órdenes de compra encontradas al seleccionar: {purchase_order.mapped('name')}"
                )
            else:
                record.purchase_order_ids = self.env["purchase.order"]

    @api.depends("purchase_order_ids")
    def _compute_invoices(self):
        for record in self:
            if record.purchase_order_ids:
                # Primero obtenemos las órdenes de compra relacionadas con el proyecto
                purchase_orders = record.purchase_order_ids

                # Buscamos las facturas de dos maneras
                # 1. Por origen (campo que contiene referencia a la orden)
                origin_invoices = self.env["account.move"].search(
                    [
                        ("invoice_origin", "in", purchase_orders.mapped("name")),
                        ("move_type", "in", ["in_invoice", "in_refund"]),
                    ]
                )

                # 2. Por líneas de factura relacionadas con líneas de orden
                line_invoices = self.env["account.move"].search(
                    [
                        (
                            "invoice_line_ids.purchase_line_id.order_id",
                            "in",
                            purchase_orders.ids,
                        ),
                        ("move_type", "in", ["in_invoice", "in_refund"]),
                    ]
                )

                # Combinar los resultados
                record.invoice_ids = origin_invoices | line_invoices

                # Verificación para debugging
                if not record.invoice_ids:
                    # Si no hay facturas, podemos verificar si hay órdenes y qué está pasando
                    print(
                        f"No se encontraron facturas para las órdenes: {purchase_orders.mapped('name')}"
                    )
            else:
                record.invoice_ids = self.env["account.move"]

    @api.depends("purchase_order_ids")
    def _compute_purchase_orders_count(self):
        for record in self:
            record.purchase_order_count = len(record.purchase_order_ids)

    @api.depends("invoice_ids")
    def _compute_invoices_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)

    def action_confirmar(self):
        for record in self:
            if record.state == "borrador":
                record.state = "confirmado"

    def action_volver_borrador(self):
        for record in self:
            if record.state == "confirmado":
                record.state = "borrador"

    # Acción para abrir la lista de órdenes de compra relacionadas
    def action_view_purchase_orders(self):
        self.ensure_one()

        # Verificamos que existe el campo correcto
        purchase_model = self.env["purchase.order"]
        purchase_fields = purchase_model._fields

        # Buscamos el campo correcto que podría relacionar con proyectos
        project_field = None
        for field_name in [
            "proyect_id",
            "project_id",
            "proyecto_id",
            "project",
            "proyecto",
        ]:
            if field_name in purchase_fields:
                project_field = field_name
                break

        domain = []

        # Filtrado por proyecto si existe el campo
        if project_field and self.proyecto_id:
            domain.append((project_field, "=", self.proyecto_id.id))

        # Decidir si aplicar filtro por proveedor
        if self.proveedor_id and self.proveedor_id.partner_id:
            # ¿Quieres mostrar sólo las órdenes de este proveedor?
            # Si es así, descomentar la siguiente línea:
            # domain.append(("partner_id", "=", self.proveedor_id.partner_id.id))
            pass

        return {
            "name": "Órdenes de Compra",
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": domain,
        }

    # Acción para abrir la lista de facturas relacionadas
    def action_view_invoices(self):
        self.ensure_one()

        # Identificamos las órdenes de compra primero
        purchase_orders = self.purchase_order_ids

        # Construimos el dominio para facturas relacionadas con esas órdenes
        domain = [
            # Facturas que tienen el número de orden en su campo de origen
            "|",
            ("invoice_origin", "in", purchase_orders.mapped("name")),
            # O facturas vinculadas a través de las líneas de factura
            ("invoice_line_ids.purchase_line_id.order_id", "in", purchase_orders.ids),
            # Asegurarse que sean facturas de proveedor
            ("move_type", "in", ["in_invoice", "in_refund"]),
        ]

        return {
            "name": "Facturas",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": domain,
        }

    def action_view_documentos(self):
        self.ensure_one()
        return {
            "name": "Documentos Relacionados",
            "type": "ir.actions.act_window",
            "res_model": "gestion.operacional.documento",
            "view_mode": "list,form",
            "domain": [("gestion_operacional_id", "=", self.id)],
            "context": {
                "default_gestion_operacional_id": self.id,
            },
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env["gestion.operacional"].browse(docids)
        logo = self.env["gestion.operacional.logo"].search([], limit=1)

        return {
            "doc_ids": docids,
            "doc_model": "gestion.operacional",
            "docs": record,
            "logo_1": logo.logo_1,
            "logo_2": logo.logo_2,
            "logo_3": logo.logo_3,
            "logo_4": logo.logo_4,
        }


class GestionOperacionalLine(models.Model):
    _name = "gestion.operacional.line"
    _description = "Detalle de Gestión Operacional"

    observaciones = fields.Text(string="Observaciones")

    gestion_operacional_id = fields.Many2one(
        "gestion.operacional", string="Gestión Operacional"
    )

    # Estados de cumplimiento
    ESTADOS_CUMPLIMIENTO = [
        ("cumple", "Cumple"),
        ("no_cumple", "No Cumple"),
        ("no_aplica", "No Aplica"),
    ]

    # Campos de documentos con sus estados
    remision_expediente = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Remisión del Expediente"
    )

    nota_solicitud_pago = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Nota de Solicitud de Pago"
    )

    invoice = fields.Selection(ESTADOS_CUMPLIMIENTO, string="Invoice")

    nota_remision = fields.Selection(ESTADOS_CUMPLIMIENTO, string="Nota de Remisión")

    cct = fields.Selection(ESTADOS_CUMPLIMIENTO, string="CCT")

    pago_ultima_djj = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Pago de la Última DJJ"
    )

    constancia_ruc = fields.Selection(ESTADOS_CUMPLIMIENTO, string="Constancia de RUC")

    certificado_social = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Certificado de Seguridad Social"
    )

    formulario_fis = fields.Selection(ESTADOS_CUMPLIMIENTO, string="Formulario FIS")

    formulario_fip = fields.Selection(ESTADOS_CUMPLIMIENTO, string="Formulario FIP")

    contancia_registro_prestadores_servicios = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Constancia de Registro de Prestadores de Servicios",
    )

    nota_prestacion_servicio = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Nota de Prestación de Servicio / Conformidad el Servicio / Acta de Recepción y/o Informe del Admnistrador del Contrato",
    )

    nota_pedido_realizacion_trabajo = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Nota de Pedido de Realización de Trabajo"
    )

    orden_de_compra = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Orden de Compra y/o Servicio"
    )

    informe_mensual_actividades_contratado = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Informe Mensual de Actividades relizadas por el contratado (se adjunta planilla firmada por el proveedor con los detalles segun ordenes)",
    )

    resolucion_nombremiento_encargado = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Resolución de Nombramiento del Encargado de la UOC",
    )

    nota_pedido_interno = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Nota de Pedido Interno para inicio del llamado"
    )

    informe_dictamen_adquisicion = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Informe y Dictamen que fundamente la Adquisición"
    )

    res_aprovacion_programa_anual_contrataciones = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Resolución de Aprobación del Programa Anual de Contrataciones",
    )

    nota_remision_pac_pfi_dncp = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Nota de Remisión del PAC y PFI a la DNCP",
    )

    certificado_disponibilidad_presupuestaria = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Certificado de Disponibilidad Presupuestaria"
    )

    carta_invitacion_proveedores = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Carta de Invitación a Proveedores"
    )

    acta_apertura_sobres = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Acta de Apertura de Sobres"
    )

    informe_comite_evaluacion = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Informe del Comité de Evaluación Técnico Económico y Cuadro Comparativo / Planilla de Comparación de Precios",
    )

    informe_dictamen_contratacion = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Informe o Dictámen sobre Contrataciones - Vía Excepción",
    )

    res_adjudicacion = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Resolución de Adjudicación / Resolución de Adenda"
    )

    copia_contrato = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Copia del Contrato / Copia de Adenda"
    )

    codigo_contrataciones = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Código de Contrataciones (CC) - Se adjunta Formulario de Reactivación de Códigos",
    )

    poliza_seguro_djj = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Póliza de Seguro y DJJ de Fiel Cumplimiento de Contrato (vigente al momeno de la recepción)",
    )

    djj_garantia_anticipo = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="DJJ de Garantía de Anticipo"
    )

    djj_respoponsabilidad_profesional = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="DJJ de Responsabilidad Profesional"
    )

    djj_garantia_mantenimiento_oferta = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="DJJ de Garantía de Mantenimiento de Oferta"
    )

    cert_interdiccion_judicial_quiebra = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Certificado de Interdicción Judicial y Quiebra"
    )

    informe_anotaciones_personales = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Informe de Anotaciones Personales"
    )


class GestionOperacionalLogo(models.Model):
    _name = "gestion.operacional.logo"
    _description = "Logos para Reportes"
    _rec_name = "name"

    name = fields.Char(string="Descripción", required=True, default="Logos de Reporte")
    logo_1 = fields.Image(string="Logo 1", max_width=128, max_height=128)
    logo_2 = fields.Image(string="Logo 2", max_width=128, max_height=128)
    logo_3 = fields.Image(string="Logo 3", max_width=128, max_height=128)
    logo_4 = fields.Image(string="Logo 4", max_width=128, max_height=128)
