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

from odoo import fields, models


class HttpServer(models.Model):
    _name = "botc.httpserver"

    name = fields.Char(string="Name", required=True)
    ip = fields.Char(string="IP", required=True)
    port = fields.Integer(string="SSH Port", required=True)
    username = fields.Char(string="SSH Username", required=True)
    pwd = fields.Char(string="SSH Password", required=True)
    config_path = fields.Char(string="Config Location", required=True)
    config_template = fields.Text(string="Config Template", required=True)
    reload_command = fields.Char("Reload Command", required=True)
