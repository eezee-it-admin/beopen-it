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

from odoo import api, fields, models


class MarketType(models.Model):
    _name = "botc.markettype"

    @api.model
    def _get_currency(self):
        currency = False
        context = self._context or {}
        if context.get('default_journal_id', False):
            currency = self.env['account.journal'].browse(
                context['default_journal_id']).currency_id
        return currency

    name = fields.Char(string="Name", required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Html(string="Description", translate=True)
    price = fields.Monetary(string="Price", required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=_get_currency)

    goal_id = fields.Many2one("botc.goal", string="Goal")
    market_id = fields.Many2one("botc.market", string="Market", required=True)
    template_ids = fields.Many2many("botc.template", string="Templates")
    preferred_flavor_id = fields.Many2one(
        "botc.flavor", string="Preferred Flavor", required=True)

    available_module_ids = fields.One2many(
        "botc.availablemodules", "markettype_id", string="Available Modules")
    available_service_ids = fields.One2many(
        "botc.availableservices", "markettype_id", string="Available Services")
