# -*- coding: utf-8 -*-

{
    "name": "Gestión Operacional",
    "version": "18.0.1.0.0",
    "summary": "Gestión y seguimiento de operaciones institucionales",
    "description": """
Gestión Operacional
===================

Aplicación para administrar y controlar procesos operacionales vinculados
a proyectos institucionales.

Funcionalidades principales:

* Gestión de procesos operativos.
* Control de operaciones y actividades.
* Vinculación con proyectos.
* Seguimiento de la ejecución operacional.
* Generación de reportes operacionales.
* Reportes asociados a objetos de gasto.
    """,
    "author": "Neurona",
    "maintainer": "Neurona",
    "website": "https://neurona.com.py/",
    "category": "Operations",
    "license": "LGPL-3",
    "icon": "/gestion_operacional/static/description/icon.png",
    "depends": [
        "base",
        "mail",
        "project",
        "proyecto_update",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
        "report/report.xml",
        "report/report839.xml",
        "report/report879.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}