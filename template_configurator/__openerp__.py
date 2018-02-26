# -*- coding: utf-8 -*-
{
    'name': "BeOpen Template Configurator",

    'summary': """BeOpen Template Configurator""",

    'description': """
        BeOpen Template Configurator
    """,

    'author': "BeOpen-IT",
    'website': "http://www.beopen.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Configurator',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website', 'mail', 'crm'],

    # always loaded
    'data': [
        'security/configurator_security.xml',
        'security/ir.model.access.csv',
 #       'templates.xml',
        'views/template_configurator.xml',
        'views/view_configurator_for_code.xml',
        'views/view_module_prices.xml',
        'data/data.xml',
 #       'views/session_board.xml',
 #       'reports.xml',
    ],
    'installable': True,
    # only loaded in demonstration mode
#    'demo': [
#        'demo.xml',
#    ],
}