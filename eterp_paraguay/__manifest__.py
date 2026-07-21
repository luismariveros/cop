# -*- coding: utf-8 -*-
{
    "name": "Localización Paraguay",
    "icon": "/eterp_paraguay/static/description/icon.png",
    "summary": """
        Módulo de localización Paraguaya""",
    "description": """
Este módulo agrega funciones para la localización paraguaya, que representa la configuración mínima 
que se necesita para que una empresa opere en Paraguay siguiendo las regulaciones. 

Modulo base para la contabilidad de Paraguay
--------------------------------------------

* Define el Plan contable genérico de Paraguay.
* Genera las cuentas contables del plan.
* Define las cuentas por defecto para ventas y compras.
* Define los impuestos por defecto IVA compras y ventas 5% y 10%
    """,
    "author": "Element Tech SRL",
    "website": "https://elementtech.com.py/",
    "category": "Accounting/Localizations/Account Charts",
    "version": "16.0.0",
    "depends": [
        "account",
        "sale",  # TODO: Verificar y eliminar
        #'eterp_secuencia_timbrado',
        # 'l10n_latam_invoice_document',
        # 'l10n_latam_base',
    ],
    "data": [
        # Chart of Accounts
        "data/account_chart_template_data.xml",
        "data/account.account.template.csv",
        "data/account_chart_post_data.xml",
        # Taxes
        "data/account_tax_group_data.xml",
        "data/account_tax_template_data.xml",
        "data/account_chart_template_try_loading.xml",
        # Init
        # 'data/l10n_latam_identification_type_data.xml',
        # Docs
        # Views
        "views/account_move_view.xml",
        "views/partner.xml",
        "views/sale_order.xml",
        "views/sale_order.xml",
        "views/account_journal.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/eterp_paraguay/static/src/js/map.js",
        ]
    },
    #'uninstall_hook': 'uninstall_hook',
    "installable": True,
    "license": "LGPL-3",
}
