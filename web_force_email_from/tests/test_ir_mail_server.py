# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright Eezee-It (C) 2017
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
###############################################################################
from odoo.tests import TransactionCase


class TestMailServer(TransactionCase):

    def setUp(self):
        super(TestMailServer, self).setUp()

        config_parameter_env = self.env["ir.config_parameter"].sudo()
        self.set_param = config_parameter_env.set_param

        # Set default values for all tests
        self.set_param('mail.default.bounce.alias', 'default_bounce')
        self.set_param('mail.catchall.domain', 'eezee-it.com')

        # Remove catchall alias to check default bounce address
        catchall = self.env.ref('mail.icp_mail_bounce_alias')
        if catchall:
            catchall.unlink()

    def test___get_default_bounce_alias(self):
        """Test _get_default_bounce_alias method."""

        mail_server_env = self.env['ir.mail_server']
        bounce_alias = mail_server_env._get_default_bounce_alias()

        self.assertEqual(bounce_alias, 'default_bounce')

        self.set_param('mail.default.bounce.alias', '')
        bounce_alias = mail_server_env._get_default_bounce_alias()
        self.assertEqual(bounce_alias, False)

        self.set_param('mail.default.bounce.alias', 'False')
        bounce_alias = mail_server_env._get_default_bounce_alias()
        self.assertEqual(bounce_alias, False)

    def test___get_default_bounce_address(self):
        """Test _get_default_bounce_address method."""

        mail_server_env = self.env['ir.mail_server']
        bounce_alias = mail_server_env._get_default_bounce_address()

        self.assertEqual(bounce_alias, 'default_bounce@eezee-it.com')

        # if not force bounce alias doesn't exists, Odoo use the default
        # alias 'postmaster-odoo'
        self.set_param('mail.default.bounce.alias', '')
        bounce_alias = mail_server_env._get_default_bounce_address()
        self.assertEqual(bounce_alias, 'postmaster-odoo@eezee-it.com')

        self.set_param('mail.default.bounce.alias', 'False')
        bounce_alias = mail_server_env._get_default_bounce_address()
        self.assertEqual(bounce_alias, 'postmaster-odoo@eezee-it.com')

        # No force bounce alias and no catchall domain but a bounce alias
        self.set_param('mail.default.bounce.alias', 'test')
        self.set_param('mail.icp_mail_bounce_alias', 'catchall')
        self.set_param('mail.catchall.domain', '')
        bounce_alias = mail_server_env._get_default_bounce_address()
        self.assertEqual(bounce_alias, None)
