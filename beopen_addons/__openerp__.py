# -*- coding: utf-8 -*-
{
    'name': "Beopen addons",

    'summary': """Beopen addons""",

    'description': """
        Beopen addons
    """,
    'depends': ['web', "base"],
    'auto_install': True,
    'author': "BeOpen-IT",
    'website': "http://www.beopen.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Addons',
    'version': '0.1',
    # always loaded
    'data': [
        'views/template.xml',
    ],
}