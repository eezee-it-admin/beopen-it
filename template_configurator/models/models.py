from openerp import models, fields, api, tools


class Market(models.Model):
    _name="botc.market"

    name=fields.Char(string="Market", required=True)


class Goal(models.Model):
    _name="botc.goal"

    name=fields.Char(string="Type", required=True)

class Flavor(models.Model):
    _name="botc.flavor"

    name=fields.Char(String="Flavor")
    version=fields.Float(String="Version", digits=(2, 1))
    edition=fields.Char(String="Edition")

class DbServer(models.Model):
    _name="botc.dbserver"

    name=fields.Char(string="Name", required=True)
    ip=fields.Char(string="IP", required=True)
    port=fields.Integer(string="Port", required=True)
    username=fields.Char(string="Username", required=True)
    pwd=fields.Char(string="Password", required=True)

class DockerServer(models.Model):
    _name="botc.dockerserver"

    name=fields.Char(string="Name", required=True)
    ip=fields.Char(string="IP", required=True)


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

    standard=fields.Boolean(string="Standard", default=True)
    package_file_location=fields.Char(string="Package File Location")

class AvailableModules(models.Model):
    _name="botc.availablemodules"
    _rec_name = "module_id"

    module_id=fields.Many2one("botc.module", string="Module", required=True)
    markettype_id = fields.Many2one("botc.markettype", string="Market Type", required=True)
    included = fields.Boolean(string="Included in package", default=False)
    flavor_id=fields.Many2one("botc.flavor", string="Flavor")
    order = fields.Integer(string="Sort Order")

class DockerImage(models.Model):
    _name="botc.dockerimage"

    name=fields.Char(string="Name", required=True)
    image_name=fields.Char(String="Image Name", required=True)
    flavor_id=fields.Many2one("botc.flavor", string="Flavor")
    volume_ids=fields.One2many("botc.volume", "docker_image_id", "Volumes")
    port_ids = fields.One2many("botc.port", "docker_image_id", "Ports")


class Volume(models.Model):
    _name = "botc.volume"

    name = fields.Char(string="Name", required=True)
    path = fields.Char(string="Path", required=True)
    docker_image_id = fields.Many2one("botc.dockerimage", string="Docker Image", required=True)


class Port(models.Model):
    _name = "botc.port"
    _rec_name = "portnumber"

    portnumber = fields.Integer(string="Portnumber", required=True)
    docker_image_id = fields.Many2one("botc.dockerimage", string="Docker Image", required=True)

class InstanceModule(models.Model):
    _name="botc.instancemodule"
    _rec_name="container_instance_id"

    container_instance_id=fields.Many2one("botc.containerinstance", string="Container Instance", required=True)
    module_id=fields.Many2one("botc.module", string="Module", required=True)
    installed_on = fields.Datetime(string="Installed on")
    uninstalled_on = fields.Datetime(string="Uninstalled on")

class ContainerInstance(models.Model):
    _name="botc.containerinstance"
    _rec_name="domain"

    domain=fields.Char(string="Domain", required=True)
    market_type_id=fields.Many2one("botc.markettype", string="Market Type", required="True")
    module_ids=fields.One2many("botc.instancemodule", "container_instance_id", "Modules")
    dbserver_id=fields.Many2one("botc.dbserver", string="DB Server", required=True)
    port_mapping_ids = fields.One2many("botc.portmapping", "container_instance_id")
    volume_mapping_ids = fields.One2many("botc.volumemapping", "container_instance_id")
    docker_image_id=fields.Many2one("botc.dockerimage", string="Docker Image")
    docker_server_id=fields.Many2one("botc.dockerserver", string="Docker Server")
    flavor=fields.Char(string="Flavor", related="docker_image_id.flavor_id.name", readonly=True)


class PortMapping(models.Model):
    _name="botc.portmapping"
    _rec_name="container_instance_id"

    container_instance_id=fields.Many2one("botc.containerinstance", string="Container Instance", required=True)
    port_id=fields.Many2one("botc.port", string="Port")
    port_map=fields.Integer(string="mapped to")

class VolumeMapping(models.Model):
    _name="botc.volumemapping"
    _rec_name="container_instance_id"

    container_instance_id=fields.Many2one("botc.containerinstance", string="Container Instance", required=True)
    volume_id=fields.Many2one("botc.volume", string="Volume")
    volume_map=fields.Char(string="mapped to")
