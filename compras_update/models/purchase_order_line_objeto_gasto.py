# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLineObjetoGasto(models.Model):
    _inherit = "purchase.order.line"

    objeto_gasto_id = fields.Many2one(
        "project.objeto.gasto",
        string="Objeto de Gasto",
        domain="[('project_id', '=', parent.proyect_id)]",
    )

    @api.onchange("objeto_gasto_id")
    def _onchange_objeto_gasto_id(self):
        """
        Al cambiar el objeto de gasto, podríamos actualizar información relacionada
        como categorías de productos o restricciones específicas.
        """
        pass

    # Este método se llama cuando se añade una línea desde el pedido principal
    @api.model
    def default_get(self, fields_list):
        """
        Establece valores predeterminados, como el objeto de gasto seleccionado
        en el encabezado del pedido si existe.
        """
        res = super(PurchaseOrderLineObjetoGasto, self).default_get(fields_list)

        # Intentar obtener el contexto del pedido principal
        if self.env.context.get("default_order_id"):
            order_id = self.env.context.get("default_order_id")
            order = self.env["purchase.order"].browse(order_id)
            if order and order.objeto_gasto_id:
                res["objeto_gasto_id"] = order.objeto_gasto_id.id

        return res


class PurchaseOrderLineProductOnchange(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def _onchange_product_id_preserve_objeto_gasto(self):
        """
        Preservar el objeto de gasto cuando se cambia el producto.
        Este método debe ejecutarse después del onchange estándar del producto.
        """
        # Almacenar el objeto de gasto actual
        objeto_gasto_id = self.objeto_gasto_id

        # Llamar al método original (si lo hay, del módulo base)
        if hasattr(
            super(PurchaseOrderLineProductOnchange, self), "_onchange_product_id"
        ):
            result = super(
                PurchaseOrderLineProductOnchange, self
            )._onchange_product_id()
        else:
            result = {}

        # Restaurar el objeto de gasto si el contexto lo indica
        if self.env.context.get("preserve_objeto_gasto") and objeto_gasto_id:
            self.objeto_gasto_id = objeto_gasto_id

        return result
