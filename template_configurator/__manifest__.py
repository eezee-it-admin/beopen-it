# -*- coding: utf-8 -*-
{
    'name': "BeOpen Template Configurator",

    'summary': """BeOpen Template Configurator""",

    'description': """
        BeOpen Template Configurator
    """,

    'author': "BeOpen NV",
    'website': "http://www.beopen.be",
    'category': 'Configurator',
    'version': '10.1',
    'depends': ['website', 'mail', 'crm'],
    'data': [
        'security/configurator_security.xml',
        'security/ir.model.access.csv',
        'views/template_configurator.xml',
        'views/view_configurator_for_code.xml',
        'views/view_module_prices.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}