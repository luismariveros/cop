# -*- coding: utf-8 -*-

{
    "name": "Actualizaciones de Proyectos",
    "version": "18.0.1.0.0",
    "summary": "Presupuestos, proveedores y objetos de gasto en proyectos",
    "description": """
Actualizaciones de Proyectos
============================

Extiende la gestión de proyectos incorporando información presupuestaria
y administrativa.

Funcionalidades principales:

* Asignación de montos y presupuestos.
* Vinculación de proveedores.
* Gestión de objetos de gasto por proyecto.
* Seguimiento de avances y ejecución.
* Control presupuestario.
* Reportes y estadísticas relacionadas con proyectos.
    """,
    "author": "Neurona",
    "maintainer": "Neurona",
    "website": "https://neurona.com.py/",
    "category": "Project",
    "license": "LGPL-3",
    "icon": "/proyecto_update/static/description/icon.png",
    "depends": [
        "base",
        "project",
        "objeto_gasto",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}