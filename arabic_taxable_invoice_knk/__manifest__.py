# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    "name": "Delivery Slip Invoice",
    "version": "16.0.1.0",
    "summary": "Delivery Slip",
    "description": """
        Delivery slip 
    """,
    "author": "Muhammad Sami Ullah",
    "website": "",
    "category": "Accounting/Accounting",
    "depends": ["account",'sale_stock'],
    "data": [
        "data/report_paperformat.xml",
        "report/account_report.xml",
        "views/invoice_report.xml",
        "views/invoice_view.xml",
        "views/res_company.xml",
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
