# -*- coding: utf-8 -*-
{
    'name': "Company Sales System",

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
    'depends': ['base','mail','crm','calendar'],

    # always loaded
    'data': [
        'security/contact.xml',
        'security/ir.model.access.csv',
        'views/pipeline.xml',
        'views/reason_lost.xml',
        'views/pricelist.xml',
        'views/meetings.xml',
        'views/calendar.xml',
        'views/cronjob.xml',
        'views/mail_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}