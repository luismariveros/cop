# -*- coding: utf-8 -*-
{
    "name": "eterp_compras_update",
    "icon": "/eterp_compras_update/static/description/icon.png",
    "summary": """
        Actualizaciones para el módulo de compras de ETERP16""",
    "description": """
        Actualizaciones para el módulo de compras de ETERP16
    """,
    "author": "Element Tech SRL",
    "website": "https://elementtech.com.py/",
    "category": "Custom",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "purchase"],
    # always loaded
    "data": [
        "data/security_groups.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
        "views/view_encabezados.xml",
        "report/reporte_compras_daf.xml",
        "report/reporte_compras_test.xml",
        "views/purchase_view_changes.xml",
        "views/purchase_order_line_objeto_gasto_view.xml",
        "views/purchase_view_daf.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
