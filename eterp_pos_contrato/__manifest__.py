# -*- coding: utf-8 -*-
{
    'name': "eterp_pos_contrato",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project', 'account', 'eterp_proyecto_update', 'hr_timesheet','payment','eterp_objeto_gasto'], 

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_kanban_override.xml',
        'views/estados.xml',
        'views/proyect_frm.xml',
        'views/proveedor.xml',
        'views/facturas.xml',
        'data/cron.xml',
        
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
