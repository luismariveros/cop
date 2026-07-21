# -*- coding: utf-8 -*-
{
    "name": "eterp_mesa_entrada_16",
    "icon": "/eterp_mesa_entrada_16/static/description/icon.png",
    "summary": """
        Módulo de Mesa de Entrada, para el registro y seguimiento de documentos""",
    "description": """
        Este módulo proporciona funcionalidades para la gestión de documentos en la Mesa de Entrada, incluyendo:

        - Registro de documentos
        - Asignación de destinatarios
        - Seguimiento de expedientes
        - Generación de reportes
        - Control de acceso a expedientes
        - Notificaciones por correo electrónico
        
        Permite optimizar y monitorear la gestión de documentos de manera eficiente.
    """,
    "author": "Element Tech SRL",
    "website": "https://elementtech.com.py/",
    "category": "Custom",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "mail", "hr"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/mesa_entrada_views.xml",
        "data/data.xml",
        "views/tipo_documento_views.xml",
        "views/providencia_views.xml",
        "views/menu_views.xml",
        "views/wizard_asignacion_views.xml",
        "data/grupos.xml",
        "data/reglas.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
