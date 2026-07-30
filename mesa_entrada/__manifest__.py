{
    "name": "Mesa de Entrada",
    "version": "18.0.1.0.0",
    "summary": "Registro, asignación y seguimiento de documentos",
    "description": """
Sistema de Mesa de Entrada para la gestión de documentos institucionales.

Funcionalidades:
- Registro de documentos.
- Clasificación por tipo de documento.
- Asignación de responsables.
- Gestión de providencias.
- Seguimiento de expedientes.
- Control de acceso.
- Notificaciones.
    """,
    "author": "Neurona",
    "maintainer": "Neurona",
    "website": "https://neurona.com.py",
    "category": "Administration",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
    ],

    "data": [
        "data/grupos.xml",
        "security/ir.model.access.csv",
        "data/reglas.xml",
        "data/data.xml",
        "views/tipo_documento_views.xml",
        "views/providencia_views.xml",
        "views/mesa_entrada_views.xml",
        "views/wizard_asignacion_views.xml",
        "views/menu_views.xml",
    ],

    "demo": [
        "demo/demo.xml",
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}