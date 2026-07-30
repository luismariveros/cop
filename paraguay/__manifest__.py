# -*- coding: utf-8 -*-

{
    "name": "Localización Paraguay",
    "version": "18.0.1.0.0",
    "summary": "Configuración contable y fiscal para empresas de Paraguay",
    "description": """
Localización Paraguay
=====================

Proporciona configuraciones contables y fiscales para empresas que operan
en Paraguay.

Funcionalidades principales:

* Plan contable de Paraguay.
* Cuentas contables para compras y ventas.
* Grupos de impuestos.
* Impuestos de IVA del 5 % y 10 %.
* Información fiscal adicional para contactos.
* Ajustes en facturas, diarios y pedidos de venta.
    """,
    "author": "Neurona",
    "maintainer": "Neurona",
    "website": "https://neurona.com.py/",
    "category": "Accounting/Localizations/Account Charts",
    "license": "LGPL-3",
    "icon": "/paraguay/static/description/icon.png",
    "depends": [
        "account",
        "sale",
    ],
    "data": [
        "data/account_chart_template_data.xml",
        "data/account.account.template.csv",
        "data/account_chart_post_data.xml",
        "data/account_tax_group_data.xml",
        "data/account_tax_template_data.xml",
        "data/account_chart_template_try_loading.xml",
        "views/account_move_view.xml",
        "views/partner.xml",
        "views/sale_order.xml",
        "views/account_journal.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "paraguay/static/src/js/map.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}