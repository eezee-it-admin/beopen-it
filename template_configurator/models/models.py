from openerp import models, fields, api, tools
import paramiko


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
    port=fields.Integer(string="DB Port", required=True)
    username=fields.Char(string="DB Username", required=True)
    pwd=fields.Char(string="DB Password", required=True)

class HttpServer(models.Model):
    _name="botc.httpserver"

    name=fields.Char(string="Name", required=True)
    ip=fields.Char(string="IP", required=True)
    port=fields.Integer(string="SSH Port", required=True)
    username=fields.Char(string="SSH Username", required=True)
    pwd=fields.Char(string="SSH Password", required=True)
    config_path=fields.Char(string="Config Location", required=True)
    config_template = fields.Text(string="Config Template", required=True)
    reload_command=fields.Char("Reload Command", required=True)


class DockerServer(models.Model):
    _name="botc.dockerserver"

    name=fields.Char(string="Name", required=True)
    ip=fields.Char(string="IP", required=True)
    port=fields.Integer(string="SSH Port", required=True)
    username=fields.Char(string="SSH Username", required=True)
    pwd=fields.Char(string="SSH Password", required=True)
    data_path=fields.Char(string="Data Path", required=True)
    min_port=fields.Integer(string="Minimum port", required=True)
    max_port=fields.Integer(string="Maximum port", required=True)

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
    description=fields.Html(string="Description", translate = True)
    price=fields.Monetary(string="Price", required=True)
    currency_id=fields.Many2one('res.currency', string='Currency', default=_get_currency)

    goal_id=fields.Many2one("botc.goal", string="Goal")
    market_id=fields.Many2one("botc.market", string="Market", required=True)
    template_id=fields.Many2one("botc.template", string="Template")

    available_module_ids = fields.One2many("botc.availablemodules", "markettype_id", string="Available Modules")

class Template(models.Model):
    _name="botc.template"

    name = fields.Char(string="Name", required=True, translate=True)
    template_database = fields.Char("Template database", required=True)
    template_username = fields.Char("Template username", required=True)
    template_password = fields.Char("Template password", required=True)
    template_apps_location = fields.Char("Template Apps Location (zip)", required=True)
    template_filestore_location = fields.Char("Template Filestore Location (zip)", required=True)
    dbserver_id = fields.Many2one("botc.dbserver", string="DB Server", required=True)

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
    _rec_name = "type"

    type = fields.Selection([("filestore","File Store"),("addons", "Addons")], required=True)
    path = fields.Char(string="Path", required=True)
    docker_image_id = fields.Many2one("botc.dockerimage", string="Docker Image", required=True)


class Port(models.Model):
    _name = "botc.port"
    _rec_name = "type"

    type = fields.Selection([("xmlrpc","XML RPC"),("longpolling", "LongPolling")], required=True)
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
    httpserver_id=fields.Many2one("botc.httpserver", string="HTTP Server", required=True)
    port_mapping_ids = fields.One2many("botc.portmapping", "container_instance_id")
    volume_mapping_ids = fields.One2many("botc.volumemapping", "container_instance_id")
    docker_image_id=fields.Many2one("botc.dockerimage", string="Docker Image", required=True)
    docker_server_id=fields.Many2one("botc.dockerserver", string="Docker Server", required=True)
    flavor=fields.Char(string="Flavor", related="docker_image_id.flavor_id.name", readonly=True)

    @api.multi
    def create_docker_container(self):

        command = "docker create --name %s" % self.domain
        for port_mapping in self.port_mapping_ids:
            command += " -p %s:%s" % (port_mapping.port_map, port_mapping.port_id.portnumber)

        command += " --add-host=postgres:%s" % self.dbserver_id.ip
        command += " -e DB_PORT_5432_TCP_ADDR=postgres"
        command += " -e DB_PORT_5432_TCP_PORT=%s" % self.dbserver_id.port
        command += " -e DB_ENV_POSTGRES_USER=%s" % self.dbserver_id.username
        command += " -e DB_ENV_POSTGRES_PASSWORD=%s" % self.dbserver_id.pwd
        command += " -e DBFILTER=%s" % self.domain

        for volume_mapping in self.volume_mapping_ids:
            command += " -v %s:%s" % (volume_mapping.volume_map, volume_mapping.volume_id.path)

        command += " %s" % self.docker_image_id.image_name

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username, \
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)

        return self.create_action(log)

    @api.multi
    def delete_docker_container(self):
        command = "docker rm %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username, \
                                                             self.docker_server_id.pwd, self.docker_server_id.port,
                                                             command)

        return self.create_action(log)

    @api.multi
    def stop_docker_container(self):
        command = "docker stop %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username, \
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)
        return self.create_action(log)

    @api.multi
    def start_docker_container(self):
        command = "docker start %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username, \
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)

        return self.create_action(log)

    @api.multi
    def inspect_docker_container(self):
        command = "docker inspect %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username, \
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)


        return self.create_action(log)

    @api.multi
    def configure_http_server(self):
        http_server = self.httpserver_id
        filename = "/tmp/%s.conf" %self.domain
        filecontents = http_server.config_template
        filecontents = filecontents.replace("%domain%",self.domain)
        filecontents = filecontents.replace("%docker_server%",self.docker_server_id.ip)
        filecontents = filecontents.replace("%longpolling_port%",str([mapping.port_map for mapping in self.port_mapping_ids if mapping.port_id.type == "longpolling"][0]))
        filecontents = filecontents.replace("%xmlrpc_port%",str([mapping.port_map for mapping in self.port_mapping_ids if mapping.port_id.type == "xmlrpc"][0]))

        log = self.env["botc.executedcommand"].sftp_write_to_file(http_server.ip, http_server.username, http_server.pwd, \
                                                                  http_server.port, filename, filecontents)

        move_command = "sudo mv /tmp/%s.conf %s" % (self.domain, self.httpserver_id.config_path)
        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username, http_server.pwd, \
                                                                  http_server.port, move_command)

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username, http_server.pwd, \
                                                                  http_server.port, self.httpserver_id.reload_command)

        return self.create_action(log)

    @api.multi
    def unconfigure_http_server(self):
        http_server = self.httpserver_id

        move_command = "sudo rm %s/%s.conf " % (self.httpserver_id.config_path, self.domain)
        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username, http_server.pwd, \
                                                                  http_server.port, move_command)

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username, http_server.pwd, \
                                                                  http_server.port, self.httpserver_id.reload_command)

        return self.create_action(log)

    def create_action(self, log):
        action = {
            "type": "ir.actions.act_window",
            "name": "Execution Log",
            "res_model": "botc.executedcommand",
            "domain": [("id", "=", log.id)],
            "view_type": "form",
            "view_mode": "form,tree",
            'view_id': False,
            "target": "new",
            'res_id': log.id
        }
        return action


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


class ExecutedCommand(models.Model):
    _name="botc.executedcommand"
    _rec_name="datetime_executed"

    datetime_executed=fields.Datetime(string="Time Executed", readonly=True)
    command=fields.Text(string="Command", readonly=True)
    standard_output=fields.Text(string="Standard Output", readonly=True)
    standard_error=fields.Text(string="Standard Error", readonly=True)

    def execute_ssh_command(self, ip, username, pwd, port, command):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(ip, username=username, password=pwd, port=port)
        stdin, stdout, stderr = client.exec_command(command)
        stdout_string = stdout.read()
        stderr_string = stderr.read()
        client.close()

        vals={"datetime_executed": fields.Datetime.now(), "command":command, "standard_output":stdout_string, "standard_error":stderr_string }

        log = super(ExecutedCommand, self).create(vals)
        return stdout_string, stderr_string, log

    def sftp_write_to_file(self, ip, username, pwd, port, filename, filecontents):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(ip, username=username, password=pwd, port=port)
        sftp = client.open_sftp()
        f = sftp.open(filename, "w")
        f.write(filecontents)
        f.close()
        file_info = sftp.stat(filename)
        client.close()

        vals={"datetime_executed": fields.Datetime.now(), "command":"sftp %s" % filename, "standard_output":file_info, "standard_error":"" }

        log = super(ExecutedCommand, self).create(vals)
        return log
