# -*- coding: utf-8 -*-
{
    "name": "eterp_gestion_operacional",
    "icon": "/eterp_gestion_operacional/static/description/icon.png",
    "summary": """
            Módulo de Gestión Operacional""",
    "description": """
        Este módulo proporciona funcionalidades para la gestión operacional, incluyendo:

        - Gestión de procesos operativos
        - Control de operaciones diarias
        - Seguimiento de actividades
        - Generación de reportes operacionales
        

        Permite optimizar y monitorear las operaciones del negocio de manera eficiente.
    """,
    "author": "Element Tech SRL",
    "website": "https://elementtech.com.py/",
    "category": "Custom",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "mail",
        "project",
        "eterp_proyecto_update",
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
        "report/report.xml",
        "report/report839.xml",
        "report/report879.xml",
        # "views/logos.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
