# ############################################################################
#
#    Copyright Eezee-It (C) 2016
#    Author: Eezee-It <info@eezee-it.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "BeOpen Template Configurator",
    'summary': """BeOpen Template Configurator""",
    'description': """
        BeOpen Template Configurator
    """,
    'author': "Beopen NV",
    'website': "http://www.beopen.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/
    # module/module_data.xml
    # for the full list
    'category': 'Configurator',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'website',
        'mail',
        'crm',
        'sale',
        'website_quote',
        'sale_subscription',
    ],

    # always loaded
    'data': [
        'security/configurator_security.xml',
        'security/ir.model.access.csv',

        'views/main_menu.xml',
        'views/containerinstance.xml',
        'views/dbserver.xml',
        'views/dockerimage.xml',
        'views/dockerserver.xml',
        'views/executedcommand.xml',
        'views/flavor.xml',
        'views/goal.xml',
        'views/httpserver.xml',
        'views/market.xml',
        'views/markettype.xml',
        'views/module.xml',
        'views/service.xml',
        'views/template.xml',

        'templates/assets_frontend.xml',
        'templates/configurator_for_code.xml',
        'templates/module_prices.xml',

        'data/data.xml',
        'data/mails.xml',
        'data/crons.xml',
        'data/product_template.xml',
        'data/botc_service.xml',
        'data/botc_market.xml',
        'data/botc_module.xml',
    ],
}
