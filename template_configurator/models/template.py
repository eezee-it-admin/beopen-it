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


class Template(models.Model):
    _name = "botc.template"

    name = fields.Char(string="Name", required=True, translate=True)
    template_username = fields.Char("Template username", required=True)
    template_password = fields.Char("Template password", required=True)
    template_apps_location = fields.Char(
        "Template Apps Location (zip)", required=True)
    template_backup_location = fields.Char(
        "Template Backup Location (zip)", required=True)
    docker_image_id = fields.Many2one(
        "botc.dockerimage", string="Docker Image", required=True)
    markettype_ids = fields.Many2many("botc.markettype", string="Types")
