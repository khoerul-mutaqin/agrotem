# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    "name": "PDF name on product label report",
    "version": "17.0.0.0.0",
    "license": "OPL-1",
    "summary": "Fix PDF name on product label report",
    "category": "Tools",
    "author": "CLuedoo",
    "website": "https://www.cluedoo.com",
    "support": "support@cluedoo.com",
    "description": """
    """,
    "depends": [
        "product",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "wizard/cdp_print_product_label_stock.xml",
        "wizard/product_label_layout_views.xml",
        "report/cdp_product_product_templates.xml",
        "report/cdp_product_template_templates.xml",
        "report/cdp_product_reports.xml",
        "report/product_product_templates.xml",
        "report/product_reports.xml",
        "report/product_template_templates.xml",
    ],
    "images": [],
    "demo": [],
    "currency": "USD",
    "application": False,
}
