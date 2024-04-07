{
    "name": "Delivery Slip Invoice",
    "version": "16.0.1.0",
    "summary": "Delivery Slip",
    "description": """
        Delivery slip 
    """,
    "author": "Muhammad Minhal",
    "website": "https://www.skylarkconsultingservices.com",
    "category": "Accounting/Accounting",
    "depends": ["account",'sale','sale_stock','sale_stock', 'sale_management'],
    "data": [
        "data/report_paperformat.xml",
        "report/account_report.xml",
        "views/invoice_report.xml",
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
