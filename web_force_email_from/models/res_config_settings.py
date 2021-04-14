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

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mail_server_restrictions = fields.Selection([
        ('no', 'No restrictions'),
        ('domain', 'Domaine name'),
        ('full_email_address', 'E-mail address'),
    ],
        default='no',
        require=True,
        string="Restrictions of the mail server",
        config_parameter="mail.force.from.server.restrictions")

    force_from_email_alias = fields.Char(
        string="Sender E-mail Address",
        config_parameter="mail.force.from.email.alias")

    force_default_bounce_alias = fields.Char(
        config_parameter="mail.default.bounce.alias",
        string="Default Bounce Address")
