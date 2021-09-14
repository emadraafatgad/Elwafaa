# -*- coding: utf-8 -*-
{
    'name': "Manfucturing",

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
    'depends': ['base','mail','stock'],

    # always loaded
    'data': [
        'security/contact.xml',
        'security/ir.model.access.csv',
        'views/mrp_request.xml',
        'views/bom_template.xml',
        'views/operation.xml',
        'views/manfucturing_steps.xml',
        'views/mrp_order.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}