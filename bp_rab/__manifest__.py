# -*- coding: utf-8 -*-
{
    'name': "RAB",

    'summary': """
        RAB""",

    'description': """
        RAB untuk kontraktor bangunan
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock','sale'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',

        'views/wiz_select_rab.xml',
        'views/group.xml',
        'views/master_category.xml',
        'views/master_formula.xml',
        'views/rab.xml',
        'views/rab_formula.xml',
        'views/formula.xml',
        'views/sale.xml',
        
        'views/menu.xml',
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
