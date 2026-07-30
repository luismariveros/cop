# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sin_secuencia = fields.Boolean(
        string="Sin Secuencia",
        default=False,
    )

    proyect_id = fields.Many2one(
        "project.project",
        string="Proyecto",
    )

    importe_proveedor_proyecto = fields.Float(
        string="Importe Proveedor Proyecto",
        store=True,
    )

    # Añadimos campos relacionados para mostrar el importe total y obligado del proyecto
    proyecto_monto_total = fields.Float(
        string="Importe Total del Proyecto",
        related="proyect_id.monto_total",
        readonly=True,
        store=False,
    )

    proyecto_monto_obligado = fields.Float(
        string="Importe Obligado del Proyecto",
        readonly=True,
        store=False,
        compute="_compute_proyecto_monto_obligado",
    )

    saldo_monto_obligado = fields.Float(
        string="Saldo Disponible",
        compute="_compute_saldo_monto_obligado",
        store=False,
        readonly=True,
    )

    # Campo relacional para almacenar todos los objetos de gasto del proyecto
    objetos_gasto_proyecto_ids = fields.Many2many(
        "project.objeto.gasto",
        string="Objetos de Gasto Disponibles",
        compute="_compute_objetos_gasto_proyecto",
        store=False,
    )

    # Campo HTML para mostrar la información detallada de los objetos de gasto
    objetos_gasto_display = fields.Html(
        string="Detalles de Objetos de Gasto",
        compute="_compute_objetos_gasto_display",
        sanitize=False,
        store=False,
    )

    # Nuevo campo para seleccionar objeto de gasto
    objeto_gasto_id = fields.Many2one(
        "project.objeto.gasto",
        string="Objeto de Gasto",
        domain="[('project_id', '=', proyect_id)]",
    )

    # Campo para mostrar el importe asignado al objeto de gasto
    importe_objeto_gasto = fields.Float(
        string="Importe Asignado",
        related="objeto_gasto_id.importe",
        readonly=True,
    )

    # Campo para mostrar el nombre del objeto de gasto seleccionado
    nombre_objeto_gasto = fields.Char(
        string="Nombre del Objeto de Gasto",
        related="objeto_gasto_id.objeto_gasto_id.name",
        readonly=True,
        store=True,
    )

    # Campos para mostrar información del objeto de gasto
    objeto_gasto_monto_asignado = fields.Float(
        string="Monto Asignado",
        related="objeto_gasto_id.importe",
        readonly=True,
    )

    objeto_gasto_monto_utilizado = fields.Float(
        string="Monto Utilizado",
        compute="_compute_objeto_gasto_montos",
        store=False,
        readonly=True,
    )

    objeto_gasto_saldo = fields.Float(
        string="Saldo Disponible",
        compute="_compute_objeto_gasto_montos",
        store=False,
        readonly=True,
    )

    # Campos para mostrar información del proveedor en el proyecto
    proveedor_monto_asignado = fields.Float(
        string="Monto Asignado",
        compute="_compute_proveedor_montos",
        readonly=True,
    )

    proveedor_monto_utilizado = fields.Float(
        string="Monto Utilizado",
        compute="_compute_proveedor_montos",
        store=False,
        readonly=True,
    )

    proveedor_saldo = fields.Float(
        string="Saldo Disponible",
        compute="_compute_proveedor_montos",
        store=False,
        readonly=True,
    )

    @api.depends("proyect_id")
    def _compute_objetos_gasto_proyecto(self):
        """Calcula todos los objetos de gasto disponibles en el proyecto seleccionado"""
        for order in self:
            if order.proyect_id:
                objetos_gasto = self.env["project.objeto.gasto"].search(
                    [("project_id", "=", order.proyect_id.id)]
                )
                order.objetos_gasto_proyecto_ids = objetos_gasto
            else:
                order.objetos_gasto_proyecto_ids = False

    @api.depends("proyect_id")
    def _compute_proyecto_monto_obligado(self):
        """Calcula el importe total obligado del proyecto"""
        for order in self:
            if order.proyect_id:
                order.proyecto_monto_obligado = order.proyect_id.monto_obligado_proyecto

            else:
                order.proyecto_monto_obligado = 0.0

    @api.onchange("proyect_id")
    def _onchange_proyect_id(self):
        if self.proyect_id:
            # Buscar todos los proveedores asociados al proyecto seleccionado
            project_proveedor = self.env["project.proveedor"].search(
                [("project_id", "=", self.proyect_id.id)]
            )

            # Limpiar el objeto de gasto cuando cambia el proyecto
            self.objeto_gasto_id = False

            # Actualizar el dominio del campo partner_id
            return {
                "domain": {
                    "partner_id": [
                        ("id", "in", project_proveedor.mapped("partner_id").ids)
                    ],
                    "objeto_gasto_id": [("project_id", "=", self.proyect_id.id)],
                }
            }
        return {"domain": {"partner_id": [], "objeto_gasto_id": []}}

    @api.onchange("objeto_gasto_id")
    def _onchange_objeto_gasto_id(self):
        # Se puede agregar lógica adicional cuando cambia el objeto de gasto
        # Por ejemplo, filtrar productos relacionados con ese objeto de gasto
        pass

    @api.onchange("partner_id", "proyect_id")
    def _onchange_partner_id(self):
        result = {}
        if self.partner_id:
            if not self.proyect_id:
                # Buscar todos los proyectos donde el partner_id es proveedor
                project_proveedor = self.env["project.proveedor"].search(
                    [("partner_id", "=", self.partner_id.id)]
                )

                # Actualizar el dominio del campo proyect_id
                result = {
                    "domain": {
                        "proyect_id": [
                            ("id", "in", project_proveedor.mapped("project_id").ids)
                        ]
                    }
                }

            # Si ya tenemos proyecto y proveedor, actualizar el importe_proveedor_proyecto
            # y los productos asociados
            if self.proyect_id:
                proveedor_proyecto = self.env["project.proveedor"].search(
                    [
                        ("project_id", "=", self.proyect_id.id),
                        ("partner_id", "=", self.partner_id.id),
                    ],
                    limit=1,
                )

                if proveedor_proyecto:
                    # Actualizar el importe del proveedor en el proyecto
                    self.importe_proveedor_proyecto = proveedor_proyecto.importe_total

                    # Limpiar líneas existentes
                    self.order_line = [(5, 0, 0)]

                    # Buscar productos asociados al proveedor en el proyecto
                    productos_proveedor = self.env["project.proveedor.producto"].search(
                        [("proveedor_id", "=", proveedor_proyecto.id)]
                    )

                    # Crear líneas de pedido basadas en los productos asociados
                    order_lines = []
                    for producto in productos_proveedor:
                        if producto.product_id:
                            line_vals = {
                                "product_id": producto.product_id.id,
                                "name": producto.descripcion
                                or producto.product_id.name,
                                "product_qty": 1.0,
                                "price_unit": producto.importe,
                                "date_planned": fields.Datetime.now(),
                                "product_uom": producto.product_id.uom_id.id,
                            }
                            order_lines.append((0, 0, line_vals))

                    if order_lines:
                        self.order_line = order_lines

        return result

    @api.model
    def create(self, vals):
        # El primer error es que estás tratando de acceder a self.sin_secuencia antes de que el registro exista
        # En el método create, necesitas usar vals.get('sin_secuencia') en lugar de self.sin_secuencia
        if vals.get("sin_secuencia", False):
            vals["name"] = "Solicitud: ---"

        # Llamar al método super con los valores modificados
        record = super(PurchaseOrder, self).create(vals)

        # Si tiene proyecto y proveedor, actualizamos el importe
        if record.proyect_id and record.partner_id:
            proveedor_proyecto = self.env["project.proveedor"].search(
                [
                    ("project_id", "=", record.proyect_id.id),
                    ("partner_id", "=", record.partner_id.id),
                ],
                limit=1,
            )
            if proveedor_proyecto:
                # Uso de método write para garantizar triggers y constraints
                record.write(
                    {"importe_proveedor_proyecto": proveedor_proyecto.importe_total}
                )
        return record

    def write(self, vals):
        # Si se está activando sin_secuencia y el registro no tiene aún ese valor,
        # entonces cambiamos el nombre a "Solicitud: ---"
        if "sin_secuencia" in vals and vals["sin_secuencia"]:
            for record in self:
                # Solo modificar el nombre si sin_secuencia cambia de False a True
                # Y si el registro tiene un nombre generado por secuencia (no es Solicitud: ---)
                if not record.sin_secuencia and record.name != "Solicitud: ---":
                    vals["name"] = "Solicitud: ---"

        res = super(PurchaseOrder, self).write(vals)

        # Si ha cambiado el proyecto o el proveedor, actualizamos el importe
        if "proyect_id" in vals or "partner_id" in vals:
            for record in self:
                if record.proyect_id and record.partner_id:
                    proveedor_proyecto = self.env["project.proveedor"].search(
                        [
                            ("project_id", "=", record.proyect_id.id),
                            ("partner_id", "=", record.partner_id.id),
                        ],
                        limit=1,
                    )
                    if proveedor_proyecto:
                        # Actualización directa para evitar recursión
                        self._cr.execute(
                            """UPDATE purchase_order 
                               SET importe_proveedor_proyecto = %s 
                               WHERE id = %s""",
                            (proveedor_proyecto.importe_total, record.id),
                        )
        return res

    def button_confirm(self):
        """Evitar que se genere una secuencia en la confirmación si 'sin_secuencia' está activado"""
        for order in self:
            # Solo asignar secuencia si sin_secuencia NO está activado
            # y el nombre no tiene una secuencia válida
            if not order.sin_secuencia and (
                not order.name or order.name == "Solicitud: ---" or order.name == "/"
            ):
                order.name = (
                    self.env["ir.sequence"].next_by_code("purchase.order") or "/"
                )
        return super(PurchaseOrder, self).button_confirm()

    # Sobrescribir el método que se llama después de agregar un producto para mantener el precio original
    @api.onchange("order_line")
    def _onchange_order_line(self):
        if self.proyect_id and self.partner_id:
            proveedor_proyecto = self.env["project.proveedor"].search(
                [
                    ("project_id", "=", self.proyect_id.id),
                    ("partner_id", "=", self.partner_id.id),
                ],
                limit=1,
            )

            if proveedor_proyecto:
                # Obtener un diccionario de productos y sus importes
                productos_importes = {}
                productos_proveedor = self.env["project.proveedor.producto"].search(
                    [("proveedor_id", "=", proveedor_proyecto.id)]
                )

                for producto in productos_proveedor:
                    if producto.product_id:
                        productos_importes[producto.product_id.id] = producto.importe

                # Actualizar precios en las líneas existentes si corresponde
                for line in self.order_line:
                    if line.product_id and line.product_id.id in productos_importes:
                        # Solo actualizar si el precio viene de la lista de precios estándar
                        # (es decir, no ha sido modificado manualmente)
                        if line.product_id.id in productos_importes:
                            line.price_unit = productos_importes[line.product_id.id]


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    monto_usd = fields.Float(
        string="Moneda Extranjera",
        store=True,
    )


class ProjectObjetoGasto(models.Model):
    _inherit = "project.objeto.gasto"

    def name_get(self):
        result = []
        for record in self:
            # Mostrar el nombre del objeto de gasto y quizás una descripción corta
            name = record.objeto_gasto_id.name
            if record.descripcion:
                # Si hay descripción, mostrarla acortada
                short_desc = (
                    record.descripcion[:30] + "..."
                    if len(record.descripcion) > 30
                    else record.descripcion
                )
                name = f"{name} - {short_desc}"
            result.append((record.id, name))
        return result

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'
    
    currency_custom_id = fields.Many2one(
        'res.currency', 
        string='Moneda',
        store=True
    )
    
    @api.model
    def default_get(self, fields_list):
        # Heredamos default_get para establecer PYG como moneda predeterminada
        res = super(PurchaseOrderInherit, self).default_get(fields_list)
        # Buscar la moneda PYG
        pyg_currency = self.env['res.currency'].search([('name', '=', 'PYG')], limit=1)
        if pyg_currency:
            res.update({
                'currency_id': pyg_currency.id,
                'currency_custom_id': pyg_currency.id
            })
        return res
    
    @api.model
    def create(self, vals):
        # Al crear órdenes nuevas, aseguramos que currency_id sea PYG
        pyg_currency = self.env['res.currency'].search([('name', '=', 'PYG')], limit=1)
        if pyg_currency:
            vals['currency_id'] = pyg_currency.id
            
        if 'currency_custom_id' not in vals and pyg_currency:
            vals['currency_custom_id'] = pyg_currency.id
            
        return super(PurchaseOrderInherit, self).create(vals)
    
    def write(self, vals):
        # Si se intenta cambiar currency_id, lo forzamos a PYG
        if 'currency_id' in vals:
            pyg_currency = self.env['res.currency'].search([('name', '=', 'PYG')], limit=1)
            if pyg_currency:
                vals['currency_id'] = pyg_currency.id
        
        return super(PurchaseOrderInherit, self).write(vals)
