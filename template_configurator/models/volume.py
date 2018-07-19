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


class Volume(models.Model):
    _name = "botc.volume"
    _rec_name = "type"

    type = fields.Selection([
        ("filestore", "File Store"),
        ("addons", "Addons"),
        ("logging", "Logging"),
        ("config", "Configuration")
    ], required=True)
    path = fields.Char(string="Path", required=True)
    docker_image_id = fields.Many2one(
        "botc.dockerimage", string="Docker Image", required=True)
