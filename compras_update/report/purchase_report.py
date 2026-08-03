# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from num2words import num2words
from odoo.exceptions import UserError


class PurchaseOrderReport(models.AbstractModel):
    _name = "report.compras_update.report_purchase_order"
    _description = "Reporte de Orden de Compra"

    @api.model
    def _get_report_values(self, docids, data=None):
        # Verificar si al menos una de las órdenes está autorizada
        docs = self.env["purchase.order"].browse(docids)

        # Filtrar solo las órdenes autorizadas para el reporte oficial
        authorized_docs = docs.filtered(lambda d: d.daf_authorized)

        # Si no hay órdenes autorizadas, mostrar solo el mensaje de acceso denegado
        if not authorized_docs:
            # No interrumpimos el flujo, pero pasamos documentos vacíos para que la plantilla
            # muestre el mensaje de error
            docs = self.env["purchase.order"]
        else:
            # Usar solo las órdenes autorizadas
            docs = authorized_docs

        # Obtener el encabezado predeterminado o el primero activo
        encabezado = self.env["report.encabezado"].search(
            [("predeterminado", "=", True)], limit=1
        )
        if not encabezado:
            encabezado = self.env["report.encabezado"].search(
                [("active", "=", True)], limit=1
            )

        # Preparar datos para el reporte
        importe_letras = ""
        departamento = ""

        if docs:
            importe_letras = num2words(docs[0].amount_total, lang="es").upper()
            # obtener el departamento asociado al proyecto
            if docs[0].proyect_id:
                departamento = docs[0].proyect_id.departamento_id.name

        # Formatear la fecha actual en español
        meses = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        fecha_actual = datetime.now()
        fecha_formateada = f"{fecha_actual.day} de {meses[fecha_actual.month - 1]} del {fecha_actual.year}"

        return {
            "doc_ids": docids,
            "doc_model": "purchase.order",
            "docs": docs,
            "encabezado": encabezado,
            "fecha_formateada": fecha_formateada,
            "importe_letras": importe_letras,
            "departamento": departamento,
        }


class PurchaseOrderTestReport(models.AbstractModel):
    _name = "report.compras_update.report_purchase_order_test"
    _description = "Reporte de Prueba de Orden de Compra"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["purchase.order"].browse(docids)

        # Obtener el encabezado predeterminado o el primero activo
        encabezado = self.env["report.encabezado"].search(
            [("predeterminado", "=", True)], limit=1
        )
        if not encabezado:
            encabezado = self.env["report.encabezado"].search(
                [("active", "=", True)], limit=1
            )

        importe_letras = num2words(docs.amount_total, lang="es").upper()

        # obtener el departamento asociado al proyecto
        if docs.proyect_id:
            departamento = docs.proyect_id.departamento_id.name
        else:
            departamento = ""

        # Formatear la fecha actual en español
        meses = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        fecha_actual = datetime.now()
        fecha_formateada = f"{fecha_actual.day} de {meses[fecha_actual.month - 1]} del {fecha_actual.year}"

        return {
            "doc_ids": docids,
            "doc_model": "purchase.order",
            "docs": docs,
            "encabezado": encabezado,
            "fecha_formateada": fecha_formateada,
            "importe_letras": importe_letras,
            "departamento": departamento,
        }
