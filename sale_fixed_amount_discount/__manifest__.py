# Copyright 2017-22 Kbizsoft.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Fixed Amount Discount",
    "summary": "Allows to apply fixed amount discounts in sales orders.",
    "version": "16.0.0",
    "category": "Sales",
    "website": "https://Kbizsoft.com",
    "author": "Kbizsoft Software solution Pvt Ltd",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
        "views/account_invoice_views.xml",
        "reports/report_sale_order.xml",
    ],
}
