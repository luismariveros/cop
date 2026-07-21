# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderDateChanges(models.Model):
    _inherit = "purchase.order"

    # Nuevo campo para fecha de orden (sin hora)
    fecha_orden = fields.Date(
        string="Fecha de Orden",
        help="Fecha de la orden de compra sin incluir hora",
        default=fields.Date.context_today,
        tracking=True,
    )

    # Sobreescribir el método que se ejecuta al confirmar la orden
    def button_confirm(self):
        res = super(PurchaseOrderDateChanges, self).button_confirm()
        # Establecer la fecha de orden al confirmar
        for order in self:
            if not order.fecha_orden:
                order.fecha_orden = fields.Date.context_today(self)
        return res

    # Al crear una orden, establecer la fecha de orden automáticamente
    @api.model
    def create(self, vals):
        # Si no se proporciona una fecha de orden, establecer la fecha actual
        if "fecha_orden" not in vals:
            vals["fecha_orden"] = fields.Date.context_today(self)
        return super(PurchaseOrderDateChanges, self).create(vals)
