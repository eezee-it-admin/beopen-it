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


class Module(models.Model):
    _name = "botc.module"

    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Text(string="Description", translate=True)
    active = fields.Boolean(string="Active", default=True)
    image = fields.Binary(string="Image Icon")

    module_ids = fields.Many2many(
        "botc.module", "botc_module_module_dependency",
        "module_id", "dependent_module_id", string="Dependent Modules")
    odoo_module_name = fields.Char(string="Odoo Module Name", required=True)

    standard = fields.Boolean(string="Standard", default=True)
    package_file_location = fields.Char(string="Package File Location")

    product_template_id = fields.Many2one(
        "product.template", string="Product", required=True)
