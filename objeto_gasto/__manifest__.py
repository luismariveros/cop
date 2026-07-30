# -*- coding: utf-8 -*-

{
    "name": "Objetos de Gasto",
    "version": "18.0.1.0.0",
    "summary": "Catálogo y clasificación presupuestaria de objetos de gasto",
    "description": """
Objetos de Gasto
================

Permite administrar el catálogo institucional de objetos de gasto según
el clasificador presupuestario.

Funcionalidades principales:

* Catálogo de objetos de gasto.
* Clasificación presupuestaria.
* Vinculación con productos.
* Seguimiento y consulta de objetos de gasto.
* Integración con proyectos y otros procesos administrativos.
    """,
    "author": "Neurona",
    "maintainer": "Neurona",
    "website": "https://neurona.com.py/",
    "category": "Accounting",
    "license": "LGPL-3",
    "icon": "/objeto_gasto/static/description/icon.png",
    "depends": [
        "base",
        "mail",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/objeto_gasto_views.xml",
        "views/producto_objeto.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}