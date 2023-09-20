# -*- coding: utf-8 -*-
{
    'name': "Purchase Request",

    'summary': """
        Purchase Request""",

    'description': """
        Purchase Request
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','hr'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',

        'views/purchase_request.xml',
        'views/wiz_generate_purchase_order.xml',
        
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
