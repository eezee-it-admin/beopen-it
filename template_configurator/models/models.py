from openerp import models, fields, api, tools
import paramiko
import logging

_logger = logging.getLogger(__name__)

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
    containerinstance_ids=fields.One2many("botc.containerinstance", "docker_server_id", "Container Instances")

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
    template_ids=fields.Many2many("botc.template", string="Templates")
    preferred_flavor_id=fields.Many2one("botc.flavor", string="Preferred Flavor", required=True)

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
    docker_image_id = fields.Many2one("botc.dockerimage", string="Docker Image", required=True)
    markettype_ids=fields.Many2many("botc.markettype", string="Types")

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

    type = fields.Selection([("filestore","File Store"),("addons", "Addons"),("logging", "Logging")], required=True)
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
    template_id=fields.Many2one("botc.template", string="Template")
    flavor=fields.Char(string="Flavor", related="docker_image_id.flavor_id.name", readonly=True)

    @api.multi
    def create_instance(self, domain, markettype, module_ids_to_install, flavor_id):

        module_ids = [(0,0, {"module_id":module_id.id, "installed_on":fields.Datetime.now()}) for module_id in module_ids_to_install]
        template =  next((template for template in markettype.template_ids if template.docker_image_id.flavor_id.id == int(flavor_id)), None)
        if not template:
            raise ValueError("No template found")

        dbserver = template.dbserver_id
        dockerimage = template.docker_image_id

        #TODO load balance logic
        dockerserver = self.env["botc.dockerserver"].search([], limit = 1)
        httpserver = self.env["botc.httpserver"].search([], limit = 1)

        max_port = 0;
        for container_instance in dockerserver.containerinstance_ids:
            for port_mapping in container_instance.port_mapping_ids:
                if port_mapping.port_map > max_port:
                    max_port = port_mapping.port_map

        if max_port < dockerserver.min_port:
            max_port = dockerserver.min_port

        port_xmlrpc = next((port for port in dockerimage.port_ids if port.type == "xmlrpc"), None)
        port_longpolling = next((port for port in dockerimage.port_ids if port.type == "longpolling"), None)
        if not port_xmlrpc or not port_longpolling:
            raise ValueError("Ports definition error")

        xmlrpc_port = max_port + 1
        longpolling_port = max_port + 2
        port_mapping_ids = [(0, 0, {"port_id": port_xmlrpc.id, "port_map":xmlrpc_port})]
        port_mapping_ids += [(0, 0, {"port_id": port_longpolling.id, "port_map":longpolling_port})]

        volume_addons = next((volume for volume in dockerimage.volume_ids if volume.type == "addons"), None)
        volume_filestore = next((volume for volume in dockerimage.volume_ids if volume.type == "filestore"), None)
        volume_logging = next((volume for volume in dockerimage.volume_ids if volume.type == "logging"), None)
        if not volume_addons or not volume_filestore or not volume_logging:
            raise ValueError("Volume definition error")

        volume_mapping_ids = [(0, 0, {"volume_id":volume_addons.id, "volume_map":"%s/%s/addons" % (dockerserver.data_path, domain)})]
        volume_mapping_ids += [(0, 0, {"volume_id":volume_filestore.id, "volume_map":"%s/%s/filestore" % (dockerserver.data_path, domain)})]
        volume_mapping_ids += [(0, 0, {"volume_id":volume_logging.id, "volume_map":"%s/%s/logging" % (dockerserver.data_path, domain)})]

        container_instance_vals = {"domain": domain,
                              "market_type_id": markettype.id,
                              "module_ids": module_ids,
                              "dbserver_id": dbserver.id ,
                              "httpserver_id": httpserver.id,
                              "docker_image_id":dockerimage.id,
                              "docker_server_id":dockerserver.id,
                              "template_id":template.id,
                              "port_mapping_ids":port_mapping_ids,
                              "volume_mapping_ids":volume_mapping_ids
                              }

        container_instance = self.create(container_instance_vals)
        container_instance.deploy_addons()
        container_instance.deploy_filestore()
        container_instance.deploy_logging()
        container_instance.configure_http_server()
        container_instance.create_docker_container()
        container_instance.start_docker_container()

        return template, dockerserver.ip, xmlrpc_port

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

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username,
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)

        return self.create_action(log)

    @api.multi
    def delete_docker_container(self):
        command = "docker rm %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username,
                                                             self.docker_server_id.pwd, self.docker_server_id.port,
                                                             command)

        return self.create_action(log)

    @api.multi
    def stop_docker_container(self):
        command = "docker stop %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username,
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)
        return self.create_action(log)

    @api.multi
    def start_docker_container(self):
        command = "docker start %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username,
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)

        return self.create_action(log)

    @api.multi
    def inspect_docker_container(self):
        command = "docker inspect %s" % self.domain

        stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(self.docker_server_id.ip, self.docker_server_id.username,
                                                             self.docker_server_id.pwd, self.docker_server_id.port, command)


        return self.create_action(log)

    @api.multi
    def configure_http_server(self):
        try:
            http_server = self.httpserver_id
            filename = "/tmp/%s.conf" %self.domain
            filecontents = http_server.config_template
            filecontents = filecontents.replace("%domain%",self.domain)
            filecontents = filecontents.replace("%docker_server%",self.docker_server_id.ip)
            filecontents = filecontents.replace("%longpolling_port%",str([mapping.port_map for mapping in self.port_mapping_ids if mapping.port_id.type == "longpolling"][0]))
            filecontents = filecontents.replace("%xmlrpc_port%",str([mapping.port_map for mapping in self.port_mapping_ids if mapping.port_id.type == "xmlrpc"][0]))

            log = self.env["botc.executedcommand"].sftp_write_to_file(http_server.ip, http_server.username, http_server.pwd,
                                                                      http_server.port, filename, filecontents)

            move_command = "sudo mv /tmp/%s.conf %s" % (self.domain, self.httpserver_id.config_path)

            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username, http_server.pwd,
                                                                      http_server.port, move_command)

            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username, http_server.pwd,
                                                                      http_server.port, self.httpserver_id.reload_command)
        except Exception as e:
            _logger.info("Exception %s", e)
            return self.create_action(log)

        return self.create_action(log)

    @api.multi
    def unconfigure_http_server(self):
        try:
            http_server = self.httpserver_id

            move_command = "sudo rm %s/%s.conf " % (self.httpserver_id.config_path, self.domain)
            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username,
                                                                                       http_server.pwd,
                                                                                       http_server.port, move_command)

            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(http_server.ip, http_server.username,
                                                                                       http_server.pwd,
                                                                                       http_server.port,
                                                                                       self.httpserver_id.reload_command)
        except:
            return self.create_action(log)

        return self.create_action(log)

    @api.multi
    def deploy_filestore(self):
        try:
            log = ""
            docker_server = self.docker_server_id

            filestore_path = str([mapping.volume_map for mapping in self.volume_mapping_ids if mapping.volume_id.type == "filestore"][0])
            mkdirbase_command = "sudo mkdir -p %s/%s/filestore" % (filestore_path, self.domain)

            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip, docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port, mkdirbase_command)

            if self.template_id:
                local_filestore = self.template_id.template_filestore_location
                zip_file = local_filestore.split("/")[::-1][0]
                log = self.env["botc.executedcommand"].sftp_put_file(docker_server.ip, docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port,local_filestore, "/tmp/%s" % zip_file)

                unzip_command = "sudo unzip /tmp/%s -d %s/%s/filestore" % (zip_file, filestore_path, self.domain)
                stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip,
                                                                                           docker_server.username,
                                                                                           docker_server.pwd,
                                                                                           docker_server.port,
                                                                                           unzip_command)

            chmod_command = "sudo chmod -R 777 %s" % (filestore_path)
            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip, docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port,
                                                                                       chmod_command)


        except Exception as e:
            _logger.info("Exception %s", e)
            return self.create_action(log)

        return self.create_action(log)

    @api.multi
    def deploy_logging(self):
        try:
            log = ""
            docker_server = self.docker_server_id

            logging_path = str([mapping.volume_map for mapping in self.volume_mapping_ids if
                                mapping.volume_id.type == "logging"][0])
            mkdirbase_command = "sudo mkdir -p %s" % (logging_path)

            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip,
                                                                                       docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port,
                                                                                       mkdirbase_command)

            chmod_command = "sudo chmod -R 777 %s" % (logging_path)
            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip, docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port,
                                                                                       chmod_command)

        except Exception as e:
            _logger.info("Exception %s", e)
            return self.create_action(log)


        return self.create_action(log)

    @api.multi
    def deploy_addons(self):
        try:
            log = ""
            docker_server = self.docker_server_id

            addons_path = str([mapping.volume_map for mapping in self.volume_mapping_ids if mapping.volume_id.type == "addons"][0])
            mkdirbase_command = "sudo mkdir -p %s" % (addons_path)
            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip, docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port, mkdirbase_command)




            if self.template_id:
                local_filestore = self.template_id.template_apps_location
                zip_file = local_filestore.split("/")[::-1][0]
                log = self.env["botc.executedcommand"].sftp_put_file(docker_server.ip, docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port,local_filestore, "/tmp/%s" % zip_file)

                unzip_command = "sudo unzip /tmp/%s -d %s" % (zip_file, addons_path)
                stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip,
                                                                                           docker_server.username,
                                                                                           docker_server.pwd,
                                                                                           docker_server.port,
                                                                                           unzip_command)

            chmod_command = "sudo chmod -R 777 %s" % (addons_path)
            stdout, stderr, log = self.env["botc.executedcommand"].execute_ssh_command(docker_server.ip, docker_server.username,
                                                                                       docker_server.pwd,
                                                                                       docker_server.port,
                                                                                       chmod_command)


        except Exception as e:
            _logger.info("Exception %s", e)

            return self.create_action(log)

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
        _logger.info("Executing %s on %s:%s with user %s", command, ip, port, username)
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
        _logger.info("Writing contents to %s in %s:%s with user %s", filename, ip, port, username )
        try:
            file_info = ""
            error = ""

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
        except Exception as e:
            error = e

        vals={"datetime_executed": fields.Datetime.now(), "command":"sftp %s" % filename, "standard_output":file_info, "standard_error":error }

        log = super(ExecutedCommand, self).create(vals)
        return log

    def sftp_put_file(self, ip, username, pwd, port, local_file, remote_file):
        _logger.info("Put file %s to %s in %s:%s with user %s", local_file, remote_file, ip, port, username )

        try:
            file_info = ""
            error = ""

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(ip, username=username, password=pwd, port=port)
            sftp = client.open_sftp()
            file_info = sftp.put(local_file, remote_file)
            client.close()
        except Exception as e:
            error = e

        vals={"datetime_executed": fields.Datetime.now(), "command":"sftp %s to %s" % (local_file, remote_file), "standard_output":file_info, "standard_error":error }
        log = super(ExecutedCommand, self).create(vals)

        return log
