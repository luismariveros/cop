# -*- coding: utf-8 -*-

{
    "name": "Contratos y Proveedores de Proyectos",
    "version": "18.0.1.0.0",
    "summary": "Gestión de contratos, proveedores y facturación de proyectos",
    "description": """
Contratos y Proveedores de Proyectos
====================================

Extiende la gestión de proyectos incorporando información contractual,
proveedores, facturación y seguimiento económico.

Funcionalidades principales:

* Gestión de contratos asociados a proyectos.
* Vinculación de proveedores.
* Estados y seguimiento contractual.
* Facturas relacionadas con proyectos.
* Integración con objetos de gasto.
* Seguimiento mediante partes de horas.
* Procesos programados mediante tareas automáticas.
    """,
    "author": "Neurona",
    "maintainer": "Neurona",
    "website": "https://neurona.com.py/",
    "category": "Project",
    "license": "LGPL-3",
    "icon": "/pos_contrato/static/description/icon.png",
    "depends": [
        "base",
        "project",
        "account",
        "proyecto_update",
        "hr_timesheet",
        "payment",
        "objeto_gasto",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/estados.xml",
        "views/project_kanban_override.xml",
        "views/proyect_frm.xml",
        "views/proveedor.xml",
        "views/facturas.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}