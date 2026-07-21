# -*- coding: utf-8 -*-
{
    'name': "eterp_proyecto_update",
    'icon': "/eterp_proyecto_update/static/description/icon.png",

    'summary': """
        Módulo de gestión de proyectos con proveedores y montos asignados.""",

    'description': """
        Módulo de gestión de proyectos que permite:
        - Asignar montos y presupuestos a proyectos
        - Vincular proveedores a proyectos
        - Gestionar objetos de gasto
        - Realizar seguimiento de avances y ejecución
        - Generar reportes y estadísticas
        - Controlar presupuestos por etapa
    """,

    "author": "Element Tech SRL",
    "website": "https://elementtech.com.py/",
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','eterp_objeto_gasto'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
