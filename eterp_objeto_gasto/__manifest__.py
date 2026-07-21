# -*- coding: utf-8 -*-
{
    'name': "eterp_objeto_gasto",
    "icon": "/eterp_objeto_gasto/static/description/icon.png",

    'summary': """
            Módulo de ejemplo para la gestión de objetos de gasto""",

    'description': """
        Módulo personalizado para gestionar objetos de gasto en la organización.
        Permite crear, editar y dar seguimiento a los diferentes tipos de gastos
        clasificados por objeto del gasto según el clasificador presupuestario.
        Incluye:
        - Catálogo de objetos de gasto
        - Registro y seguimiento de gastos
        - Reportes y consultas
        - Integración con proyectos y productos
    """,

    "author": "Element Tech SRL",
    "website": "https://elementtech.com.py/",
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/objeto_gasto_views.xml',
        'views/producto_objeto.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
