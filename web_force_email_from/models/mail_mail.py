# -*- coding: utf-8 -*-
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
from odoo import api, models


class MailMail(models.Model):
    _name = 'mail.mail'
    _inherit = ['mail.mail']

    @api.model
    def create(self, values):
        """Override standard Odoo method"""
        has_mail_server_restriction = self._has_mail_server_restriction()

        if not has_mail_server_restriction:
            return super(MailMail, self).create(values)

        if 'email_from' in values and not self._check_sender(
                values['email_from']):
            if not values.get('reply_to', False):
                values['reply_to'] = values['email_from']

            values['email_from'] = self._get_force_from()

        return super(MailMail, self).create(values)

    def send(self, auto_commit=False, raise_exception=False):
        """Override standard Odoo method"""
        has_mail_server_restriction = self._has_mail_server_restriction()

        if not has_mail_server_restriction:
            return super(MailMail, self).send(auto_commit, raise_exception)

        for record in self:
            if record.email_from and not self._check_sender(record.email_from):
                if not record.reply_to:
                    record.reply_to = record.email_from
                record.email_from = self._get_force_from()

        return super(MailMail, self).send(auto_commit, raise_exception)

    @api.model
    def _check_sender(self, email_from):
        """Check the email_from field.

        Check if the sender is valid for the mail server.
        For mail restricted on domain, the method check if the domain is on
        the sender email address.
        For mail restricted by a knowed email address on the mail server,
        the method check if the sender e-mail is the knowed email address.
        """

        if not self._has_mail_server_restriction():
            return True

        mail_server_restriction = self._get_mail_server_restriction()

        if mail_server_restriction == 'domain':
            domain = self._get_force_from_domain()
            return '@' + domain in email_from

        force_email_from = self._get_force_from_email()
        return force_email_from in email_from

    @api.model
    def _has_mail_server_restriction(self):
        mail_server_restriction = self._get_mail_server_restriction()
        return mail_server_restriction and mail_server_restriction != 'no'

    @api.model
    def _get_mail_server_restriction(self):
        ir_config_parameter_env = self.env["ir.config_parameter"].sudo()
        return ir_config_parameter_env.get_param(
            "mail.force.from.server.restrictions")

    @api.model
    def _get_force_from(self):
        """Return the entire sender e-mail address.

        Return the sender with the sender name and the sender e-mail address.

        """
        name = self._get_force_from_name()
        email = self._get_force_from_email()
        return '%s <%s>' % (name, email)

    @api.model
    def _get_force_from_email(self):
        """Return the sender e-mail address.

        if an alias and a domain for the sender exists, the method return
        the entire mail address, otherwire return the mail alias.

        return alias@domain or alias
        """
        mail_alias = self._get_force_from_alias()
        mail_domain = self._get_force_from_domain()

        if mail_alias and mail_domain:
            return '%s@%s' % (mail_alias, mail_domain)

        if not mail_domain:
            return mail_alias

    @api.model
    def _get_force_from_name(self):
        """Return the sender email name.

        on a mail address we can add a sender name with the notation:
        "sender name <email>""

        this method return the sender name, by default is the main company name

        """
        company = self.env.ref('base.main_company')
        return company.name

    @api.model
    def _get_force_from_domain(self):
        """Return the email domain to use on on the sender email address.

        By default return the param "mail.catchall.domain"

        """
        alias_domain = self.env["ir.config_parameter"].sudo().get_param(
            "mail.catchall.domain")

        return alias_domain

    @api.model
    def _get_force_from_alias(self):
        """Return the alias to use on on the sender email address.

        the alias is the first part on an e-mail address
        alias@domain

        if the param exists return the alias, False otherwise.
        """
        alias = self.env["ir.config_parameter"].sudo().get_param(
            "mail.force.from.email.alias")

        if alias == 'False':
            return False

        return alias
