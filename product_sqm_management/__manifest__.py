# -*- coding: utf-8 -*-
{
    'name': "Product SQM Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing.""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock','sale_fixed_amount_discount','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_sqm_views.xml',
        'views/sale_order_sqm_view.xml',
        'views/account_move_view.xml',
        'views/templates.xml',
        # 'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
