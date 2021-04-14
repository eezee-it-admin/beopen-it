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
from odoo import models, api


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def _get_default_bounce_address(self):
        # For many customer, the system parameter "mail.bounce.alias"
        # should removed because Odoo create a special bounce email but
        # emails with not existing account on mail server of customer are
        # refused.
        # Overide the Odoo method, just change the "default=" param
        get_param = self.env['ir.config_parameter'].sudo().get_param
        default_bounce_alias = self._get_default_bounce_alias()

        if not default_bounce_alias:
            return super(IrMailServer, self)._get_default_bounce_address()

        postmaster = get_param('mail.bounce.alias',
                               default=default_bounce_alias)
        domain = get_param('mail.catchall.domain')

        if postmaster and domain:
            return '%s@%s' % (postmaster, domain)

        return super(IrMailServer, self)._get_default_bounce_address()

    @api.model
    def _get_default_bounce_alias(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        default_bounce_alias = get_param("mail.default.bounce.alias")

        if default_bounce_alias == 'False':
            return False

        return default_bounce_alias
