# -*- coding: utf-8 -*-
{
    'name': "RAB to Purchase Request",

    'summary': """
        RAB to Purchase Request""",

    'description': """
        Create purchase request from RAB
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['bp_rab','bp_purchase_request'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_request.xml',
        'views/purchase.xml',
        'views/stock_scrap.xml',
        'views/v_rab_product.xml',
        'views/wiz_generate_purchase_request.xml',
        'views/wiz_generate_purchase_order.xml',
        'views/rab.xml',

        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
