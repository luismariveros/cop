# -*- coding: utf-8 -*-

{
    "name": "Actualizaciones de Compras",
    "version": "18.0.1.0.0",
    "summary": "Extensiones y controles adicionales para la gestión de compras",
    "description": """
Actualizaciones de Compras
==========================

Extiende la aplicación de Compras incorporando funcionalidades adicionales
para la gestión institucional.

Funcionalidades principales:

* Gestión de objetos de gasto en órdenes de compra.
* Controles y autorizaciones para usuarios de DAF.
* Encabezados y datos adicionales en órdenes de compra.
* Ajustes de fechas y líneas de compra.
* Reportes personalizados de compras.
    """,
    "author": "Neurona",
    "maintainer": "Neurona",
    "website": "https://neurona.com.py/",
    "category": "Purchases",
    "license": "LGPL-3",
    "icon": "/compras_update/static/description/icon.png",
    "depends": [
        "base",
        "purchase",
        "proyecto_update",
    ],
    "data": [
        "data/security_groups.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
        "views/view_encabezados.xml",
        "views/purchase_view_changes.xml",
        "views/purchase_order_line_objeto_gasto_view.xml",
        "views/purchase_view_daf.xml",
        "report/reporte_compras_daf.xml",
        "report/reporte_compras_test.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}