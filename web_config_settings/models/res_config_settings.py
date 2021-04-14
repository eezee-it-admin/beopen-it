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

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # module_dynamic_column_listview = fields.Boolean(
    #     "Dynamic Column Listview")
    #
    # module_web_manage_filters = fields.Boolean(
    #     "Manage Filters")
    #
    # module_domain_field_selectable = fields.Boolean(
    #     "Domain Field Selectable")
    #
    module_web_email_queue_limit = fields.Boolean(
        "Limit the number of e-mails sent on e-mail queue")
    module_web_force_email_from = fields.Boolean(
        "Force the sender e-mail address")

    # module_web_export_visibility = fields.Boolean(
    #     "Access right to export")
    #
    # module_web_pinned_filters = fields.Boolean(
    #     "Pin favorite filter")
    #
    # module_web_widget_focus = fields.Boolean(
    #     "Field focus widget")
