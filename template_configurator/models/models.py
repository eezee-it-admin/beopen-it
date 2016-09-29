from openerp import models, fields, api, tools

class Market(models.Model):
    _name="botc.market"

    name=fields.Char(string="Market", required=True)


class Goal(models.Model):
    _name="botc.goal"

    name=fields.Char(string="Type", required=True)


class MarketType(models.Model):
    _name="botc.markettype"

    @api.model
    def _get_currency(self):
        currency=False
        context=self._context or {}
        if context.get('default_journal_id', False):
            currency=self.env['account.journal'].browse(context['default_journal_id']).currency_id
        return currency

    name=fields.Char(string="Name", required=True, translate = True)
    code=fields.Char(string="Code", required=True)
    template_database = fields.Char("Template name", required=True)
    template_username = fields.Char("Template username", required=True)
    template_password = fields.Char("Template password", required=True)
    description=fields.Html(string="Description", translate = True)
    price=fields.Monetary(string="Price", required=True)
    currency_id=fields.Many2one('res.currency', string='Currency', default=_get_currency)

    goal_id=fields.Many2one("botc.goal", string="Goal")
    market_id=fields.Many2one("botc.market", string="Market", required=True)

    available_module_ids = fields.One2many("botc.availablemodules", "markettype_id", string="Available Modules")

class Module(models.Model):
    _name="botc.module"

    name=fields.Char(string="Name", required=True, translate = True)
    description=fields.Text(string="Description", translate = True)
    price = fields.Monetary(string="Price", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    active = fields.Boolean(string="Active", default=True)
    image = fields.Binary(string="Image Icon")

    module_ids=fields.Many2many("botc.module", "botc_module_module_dependency", "module_id", "dependent_module_id", string="Dependent Modules")
    odoo_module_name=fields.Char(string="Odoo Module Name", required=True)

class AvailableModules(models.Model):
    _name="botc.availablemodules"
    _rec_name = "module_id"

    module_id=fields.Many2one("botc.module", string="Module", required=True)
    markettype_id = fields.Many2one("botc.markettype", string="Market Type", required=True)
    included = fields.Boolean(string="Included in package", default=False)
    order = fields.Integer(string="Sort Order")
