# -*- coding: utf-8 -*-
{
    'name': "Sales Policy",

    'summary': """
        Elwafa""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','sale_management','stock','purchase'],

    # always loaded
    'data': [
        'security/contact.xml',
        'security/ir.model.access.csv',
        'views/area.xml',
        'views/pricelist_co.xml',
        'views/customer.xml',
        'views/cars.xml',
        'views/sales_quotation.xml',
        'views/car_fix.xml',
        'views/target.xml',
        'views/area.xml',
        'views/workshop.xml',
        'reports/car_reception_detection.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}