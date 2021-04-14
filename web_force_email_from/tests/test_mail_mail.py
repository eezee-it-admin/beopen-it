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
from odoo.addons.mail.tests import common as mail_common
from odoo.tests import TransactionCase


class TestMail(TransactionCase, mail_common.MockEmail):

    def setUp(self):
        super(TestMail, self).setUp()

        config_parameter_env = self.env["ir.config_parameter"].sudo()
        mail_env = self.env['mail.mail']
        set_param = config_parameter_env.set_param

        # Set default values for all tests
        set_param('mail.force.from.server.restrictions', 'no')
        set_param('mail.force.from.email.alias', 'info')
        set_param('mail.default.bounce.alias', 'default_bounce')
        set_param('mail.catchall.domain', 'eezee-it.com')

        force_from = mail_env._get_force_from()

        self.tests = []
        # no restriction, the email_from is not changed
        self.tests.append({
            'restriction': 'no',
            'email_from': 'private@test.com',
            'email_from_expected': 'private@test.com',
            'reply_to': False,
            'reply_to_expected': False,
            'error_message': 'no: private@test.com replaced!',
        })

        # domain restriction, email_from with a domain not matching
        # 'mail.catchall.domain', so it's replaced
        self.tests.append({
            'restriction': 'domain',
            'email_from': 'private@test.com',
            'email_from_expected': force_from,
            'reply_to': False,
            'reply_to_expected': 'private@test.com',
            'error_message': 'domain: private@test.com not replaced!',
        })

        # Same test but with an another reply-to, reply-to should not be
        # replaced
        self.tests.append({
            'restriction': 'domain',
            'email_from': 'private@test.com',
            'email_from_expected': force_from,
            'reply_to': 'reply-to@test.com',
            'reply_to_expected': 'reply-to@test.com',
            'error_message': 'domain: private@test.com not replaced!',
        })

        # domain restriction, email_from with a domain matching
        # 'mail.catchall.domain', so it's not replaced
        self.tests.append({
            'restriction': 'domain',
            'email_from': 'private@eezee-it.com',
            'email_from_expected': 'private@eezee-it.com',
            'reply_to': False,
            'reply_to_expected': False,
            'error_message': 'domain: private@eezee.com replaced!',
        })

        # full_email_address restriction, email_from with an email not matching
        # the force from email, so it's replaced
        self.tests.append({
            'restriction': 'full_email_address',
            'email_from': 'private@test.com',
            'email_from_expected': force_from,
            'reply_to': False,
            'reply_to_expected': 'private@test.com',
            'error_message':
                'full_email_address: private@test.com not replaced!',
        })

        # full_email_address restriction, email_from with an email not matching
        # the force from email, so it's replaced
        self.tests.append({
            'restriction': 'full_email_address',
            'email_from': 'private@eezee-it.com',
            'email_from_expected': force_from,
            'reply_to': False,
            'reply_to_expected': 'private@eezee-it.com',
            'error_message':
                'full_email_address: private@eezee-it.com not replaced!',
        })

        # full_email_address restriction, email_from with an email matching
        # the force from email, so it's not replaced
        self.tests.append({
            'restriction': 'full_email_address',
            'email_from': 'info@eezee-it.com',
            'email_from_expected': 'info@eezee-it.com',
            'reply_to': False,
            'reply_to_expected': False,
            'error_message':
                'full_email_address: info@eezee-it.com replaced!',
        })

    def test__check_sender(self):
        """Test _check_sender method."""
        config_parameter_env = self.env["ir.config_parameter"].sudo()
        mail_env = self.env['mail.mail']
        set_param = config_parameter_env.set_param

        # Already True
        set_param('mail.force.from.server.restrictions', 'no')
        self.assertTrue(mail_env._check_sender('private@test.com'))

        # True if the domain is eezee-it.com
        set_param('mail.force.from.server.restrictions', 'domain')
        self.assertFalse(mail_env._check_sender('private@test.com'))
        self.assertTrue(mail_env._check_sender('private@eezee-it.com'))
        self.assertTrue(mail_env._check_sender('info@eezee-it.com'))

        # True if the email_from is info@eezee-it.com
        set_param('mail.force.from.server.restrictions', 'full_email_address')
        self.assertFalse(mail_env._check_sender('private@test.com'))
        self.assertFalse(mail_env._check_sender('private@eezee-it.com'))
        self.assertTrue(mail_env._check_sender('info@eezee-it.com'))

    def test___has_mail_server_restriction(self):
        """Test _has_mail_server_restriction method."""
        config_parameter_env = self.env["ir.config_parameter"].sudo()
        mail_env = self.env['mail.mail']
        set_param = config_parameter_env.set_param

        set_param('mail.force.from.server.restrictions', 'no')
        self.assertFalse(mail_env._has_mail_server_restriction())

        set_param('mail.force.from.server.restrictions', 'domain')
        self.assertTrue(mail_env._has_mail_server_restriction())

        set_param('mail.force.from.server.restrictions', 'full_email_address')
        self.assertTrue(mail_env._has_mail_server_restriction())

    def test_create_email(self):
        """Test the creation of new mail.mail object."""
        config_parameter_env = self.env["ir.config_parameter"].sudo()
        set_param = config_parameter_env.set_param

        for test in self.tests:
            set_param('mail.force.from.server.restrictions',
                      test['restriction'])

            mail = self.create_mail_mail(test['email_from'], test['reply_to'])

            self.assertEqual(mail.email_from, test['email_from_expected'],
                             test['error_message'])

            self.assertEqual(mail.reply_to, test['reply_to_expected'],
                             test['error_message'])

    def test_send_email(self):
        """Test the send of mails."""
        config_parameter_env = self.env["ir.config_parameter"].sudo()
        set_param = config_parameter_env.set_param

        for test in self.tests:
            set_param('mail.force.from.server.restrictions',
                      test['restriction'])

            # create e-mail with a right address e-mail to check
            # if e-mail address are changed before send.
            mail = self.create_mail_mail('info@eezee-it.com', test['reply_to'])
            mail.email_from = test['email_from']
            mail.send()

            self.assertEqual(mail.email_from, test['email_from_expected'],
                             test['error_message'])
            self.assertEqual(mail.reply_to, test['reply_to_expected'])

    def test___get_force_from_email(self):
        """Test _get_force_from_email method."""
        config_parameter_env = self.env["ir.config_parameter"].sudo()
        set_param = config_parameter_env.set_param

        mail_env = self.env['mail.mail']
        force_from_email = mail_env._get_force_from_email()

        self.assertEqual(force_from_email, 'info@eezee-it.com')

        set_param('mail.catchall.domain', '')
        force_from_email = mail_env._get_force_from_email()
        self.assertEqual(force_from_email, 'info')

        set_param('mail.force.from.email.alias', 'False')
        force_from_email = mail_env._get_force_from_email()
        self.assertEqual(force_from_email, False)

    def create_mail_mail(self, email_from, reply_to):
        return self.env['mail.mail'].create({
            'body_html': '<p>Test</p>',
            'email_to': 'no_reply@eezee-it.com',
            'email_from': email_from,
            'reply_to': reply_to,
            'auto_delete': False,
        })
