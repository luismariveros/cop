# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    proveedor_ids = fields.One2many(
        "project.proveedor", "project_id", string="Proveedores"
    )
    pagos_ids = fields.One2many("project.pagos", "project_id", string="Pagos")

    # Nuevo campo para relacionar con objetos de gasto
    objeto_gasto_ids = fields.One2many(
        "project.objeto.gasto", "project_id", string="Objetos de Gasto"
    )

    monto_total = fields.Float(
        string="Monto Total del Proyecto",
        compute="_compute_monto_total",
        store=True,
        help="Suma de los importes asignados a todos los proveedores.",
    )
    monto_disponible = fields.Float(
        string="Monto Disponible",
        compute="_compute_monto_disponible",
        store=True,
        help="Monto total menos el importe calculado de todos los proveedores.",
    )

    departamento_id = fields.Many2one(
        "hr.department", string="Departamento", store=True, traking=True
    )

    juridica_ids = fields.One2many(
        "project.juridica", "project_id", string="Juridica del Proyecto"
    )

    monto_total_proyecto = fields.Monetary(
        string="Monto Total del Proyecto",
        compute="_compute_monto_total_proyecto",
        store=True,
        help="Suma de los importes asignados a todos los proveedores.",
    )

    monto_obligado_proyecto = fields.Monetary(
        string="Monto Obligado del Proyecto",
        store=True,
        compute="_compute_monto_obligado_proyecto",
    )

    fecha_project = fields.Date(string="Fecha de Proyecto", store=True, traking=True)

    # calcular obligado, tiene que sumar el monto obligado de project.pagos
    @api.depends("pagos_ids.monto_obligado")
    def _compute_monto_obligado_proyecto(self):
        for project in self:
            project.monto_obligado_proyecto = sum(
                pago.monto_obligado for pago in project.pagos_ids
            )

    @api.depends("proveedor_ids.importe_total")
    def _compute_monto_total_proyecto(self):
        for project in self:
            project.monto_total_proyecto = sum(
                proveedor.importe_total for proveedor in project.proveedor_ids
            )

    @api.depends("proveedor_ids.importe_total")
    def _compute_monto_total(self):
        for project in self:
            project.monto_total = sum(
                proveedor.importe_total for proveedor in project.proveedor_ids
            )

    @api.depends("monto_total", "proveedor_ids.importe_calculado")
    def _compute_monto_disponible(self):
        for project in self:
            project.monto_disponible = project.monto_total - sum(
                proveedor.importe_calculado for proveedor in project.proveedor_ids
            )


# Nuevo modelo para objetos de gasto
class ProjectObjetoGasto(models.Model):
    _name = "project.objeto.gasto"
    _description = "Objeto de Gasto del Proyecto"

    project_id = fields.Many2one(
        "project.project", string="Proyecto", required=True, ondelete="cascade"
    )
    objeto_gasto_id = fields.Many2one(
        "objeto.gasto.detalle", string="Objeto de Gasto", required=True
    )
    importe = fields.Float(string="Importe", required=True)
    descripcion = fields.Text(string="Descripción")

    # Campo relacionado para facilitar agrupaciones y búsquedas
    nombre_gasto = fields.Char(
        string="Nombre del Objeto de Gasto", related="objeto_gasto_id.name", store=True
    )


class ProjectJuridica(models.Model):
    _name = "project.juridica"
    _description = "Juridica del Proyecto"

    project_id = fields.Many2one("project.project", string="Proyecto", required=True)
    resolucion_snd = fields.Char(string="Resolución SND N°", store=True, traking=True)
    fecha_resolucion = fields.Date(
        string="Fecha de Resolución", store=True, traking=True
    )
    convenio_uep = fields.Char(string="Convenio UEP N°", store=True, traking=True)
    contrato_nro = fields.Char(string="Nro. de Contrato", store=True, traking=True)
    contrato_fecha = fields.Date(string="Fecha de Contrato", store=True, traking=True)
    adjunto_contrato = fields.Binary(
        string="Adjunto de Contrato", store=True, traking=True
    )

    def name_get(self):
        result = []
        for record in self:
            display_name = record.resolucion_snd or "Sin Resolución"
            result.append((record.id, display_name))
        return result


class ProjectPagos(models.Model):
    _name = "project.pagos"
    _description = "Pagos del Proyecto"

    project_id = fields.Many2one("project.project", string="Proyecto", required=True)

    resolucion_snd = fields.Many2one(
        "project.juridica",
        string="Resolución SND",
        domain="[('project_id', '=', project_id)]",  # Filtro por proyecto
        required=True,
    )

    str_resolucion_snd = fields.Char(string="STR N°")
    fecha_str = fields.Date(string="Fecha de STR")
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    monto_obligado = fields.Monetary(
        string="Monto Obligado",
        currency_id="currency_id",
    )

    fecha_vencimiento_str = fields.Date(string="Fecha de Vencimiento de STR")


class ProjectProveedor(models.Model):
    _name = "project.proveedor"
    _description = "Proveedor del Proyecto"
    _rec_name = "partner_id"

    project_id = fields.Many2one("project.project", string="Proyecto", required=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Proveedor",
        required=True,
        
    )
    importe_total = fields.Float(string="Importe Total")
    producto_ids = fields.One2many(
        "project.proveedor.producto", "proveedor_id", string="Productos"
    )
    importe_calculado = fields.Float(
        string="Importe Calculado", compute="_compute_importe_calculado", store=True
    )
    descripcion = fields.Text(string="Descripción")
    saldo_disponible = fields.Float(
        string="Saldo Disponible", compute="_compute_saldo_disponible", store=True
    )

    @api.depends("producto_ids")
    def _compute_importe_calculado(self):
        for record in self:
            record.importe_calculado = sum(
                producto.importe for producto in record.producto_ids
            )

    @api.depends("importe_total", "importe_calculado")
    def _compute_saldo_disponible(self):
        for record in self:
            record.saldo_disponible = record.importe_total - record.importe_calculado

    @api.constrains("importe_calculado", "importe_total")
    def _check_importe_total(self):
        for proveedor in self:
            if proveedor.importe_calculado > proveedor.importe_total:
                raise ValidationError(
                    _(
                        "El importe calculado no puede superar el importe total asignado al proveedor."
                    )
                )

    def action_view_productos(self):
        return {
            "name": _("Productos"),
            "view_mode": "tree",
            "res_model": "project.proveedor.producto",
            "type": "ir.actions.act_window",
            "view_id": self.env.ref(
                "proyecto_update.view_project_proveedores_product_tree"
            ).id,
            "domain": [("proveedor_id", "=", self.id)],
            "context": {
                "default_proveedor_id": self.id,
            },
        }


class ProjectProveedorProducto(models.Model):
    _name = "project.proveedor.producto"
    _description = "Producto del Proveedor"

    proveedor_id = fields.Many2one(
        "project.proveedor", string="Proveedor", required=True, ondelete="cascade"
    )
    nombre_proveedor = fields.Char(
        string="Proveedor",
        compute="_compute_nombre_proveedor",
        store=True,  # Agregar store=True si necesitas búsqueda y filtrado
    )
    objeto_gasto_id = fields.Many2one(
        "objeto.gasto.detalle", string="Objeto de Gasto", required=True
    )
    product_id = fields.Many2one("product.product", string="Producto", required=True)
    nombre_gasto = fields.Char(
        string="Objeto de Gasto", related="objeto_gasto_id.name", store=True
    )

    importe = fields.Float(string="Importe", required=True)
    descripcion = fields.Text(string="Descripción del Producto")

    @api.depends("proveedor_id.partner_id")
    def _compute_nombre_proveedor(self):
        for record in self:
            record.nombre_proveedor = (
                record.proveedor_id.partner_id.name
                if record.proveedor_id.partner_id
                else ""
            )
