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
import configparser
import io
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ContainerInstance(models.Model):
    _name = "botc.containerinstance"
    _rec_name = "domain"

    domain = fields.Char(string="Domain", required=True)
    market_type_id = fields.Many2one(
        "botc.markettype", string="Market Type", required="True")
    module_ids = fields.One2many(
        "botc.instancemodule", "container_instance_id", "Modules")
    dbserver_id = fields.Many2one(
        "botc.dbserver", string="DB Server", required=True)
    httpserver_id = fields.Many2one(
        "botc.httpserver", string="HTTP Server", required=True)
    port_mapping_ids = fields.One2many(
        "botc.portmapping", "container_instance_id")
    volume_mapping_ids = fields.One2many(
        "botc.volumemapping", "container_instance_id")
    docker_image_id = fields.Many2one(
        "botc.dockerimage", string="Docker Image", required=True)
    docker_server_id = fields.Many2one(
        "botc.dockerserver", string="Docker Server", required=True)
    template_id = fields.Many2one("botc.template", string="Template")
    restart_policy = fields.Selection([
        ("no", "No"),
        ("on-failure", "On Failure"),
        ("always", "Always"),
        ("unless-stopped", "Unless Stopped")
    ],
        required=True, default="unless-stopped")
    extra_parameters = fields.Char(string="Extra Parameters")
    flavor = fields.Char(
        string="Flavor",
        related="docker_image_id.flavor_id.name", readonly=True)
    http_config = fields.Text(string="Http Config")
    odoo_config = fields.Text(string="Odoo Config")

    @api.multi
    def create_instance(self, domain, markettype, module_ids_to_install,
                        flavor_id):

        domains = self.env["botc.containerinstance"].sudo().search(
            [("domain", "=", domain)])

        if domains and len(domains) > 0:
            raise Exception("Database %s already exists" % domain)

        module_ids = [(0, 0, {
            "module_id": module_id.id,
            "installed_on": fields.Datetime.now()
        }) for module_id in module_ids_to_install]
        template = next(
            (template for template in markettype.template_ids
                if template.docker_image_id.flavor_id.id == int(flavor_id)),
            None)
        if not template:
            raise ValueError("No template found")

        dockerimage = template.docker_image_id

        admin_pwd = ""
        if dockerimage.odoo_config:
            config = configparser.ConfigParser(allow_no_value=True)
            config_io = io.StringIO(dockerimage.odoo_config)
            config.readfp(config_io)

            try:
                admin_pwd = config.get("options", "admin_passwd")
            except configparser.NoOptionError:
                pass

        # TODO load balance logic
        dbserver = self.env["botc.dbserver"].search([], limit=1)
        dockerserver = self.env["botc.dockerserver"].search([], limit=1)
        httpserver = self.env["botc.httpserver"].search([], limit=1)

        max_port = 0
        for container_instance in dockerserver.containerinstance_ids:
            for port_mapping in container_instance.port_mapping_ids:
                if port_mapping.port_map > max_port:
                    max_port = port_mapping.port_map

        if max_port < dockerserver.min_port:
            max_port = dockerserver.min_port

        port_xmlrpc = next(
            (port for port in dockerimage.port_ids if port.type == "xmlrpc"),
            None)
        port_longpolling = next(
            (port for port in dockerimage.port_ids
                if port.type == "longpolling"), None)
        if not port_xmlrpc or not port_longpolling:
            raise ValueError("Ports definition error")

        xmlrpc_port = max_port + 1
        longpolling_port = max_port + 2
        port_mapping_ids = [
            (0, 0, {"port_id": port_xmlrpc.id, "port_map": xmlrpc_port})]
        port_mapping_ids += [(0, 0, {"port_id": port_longpolling.id,
                                     "port_map": longpolling_port})]

        volume_addons = next(
            (volume for volume in dockerimage.volume_ids
                if volume.type == "addons"), None)
        volume_filestore = next(
            (volume for volume in dockerimage.volume_ids
                if volume.type == "filestore"), None)
        volume_logging = next(
            (volume for volume in dockerimage.volume_ids
                if volume.type == "logging"), None)
        if not volume_addons or not volume_filestore or not volume_logging:
            raise ValueError("Volume definition error")

        volume_mapping_ids = [(0, 0, {
            "volume_id": volume_addons.id,
            "volume_map": "%s/%s/addons" % (dockerserver.data_path, domain)
        })]
        volume_mapping_ids += [(0, 0, {
            "volume_id": volume_filestore.id,
            "volume_map": "%s/%s/filestore" % (dockerserver.data_path, domain)
        })]
        volume_mapping_ids += [(0, 0, {
            "volume_id": volume_logging.id,
            "volume_map": "%s/%s/logging" % (dockerserver.data_path, domain)
        })]

        volume_config = next(
            (volume for volume in dockerimage.volume_ids
                if volume.type == "config"), None)
        if volume_config:
            volume_mapping_ids += [(0, 0, {
                "volume_id": volume_config.id,
                "volume_map": "%s/%s/config" % (dockerserver.data_path, domain)
            })]

        http_config = httpserver.config_template
        http_config = http_config.replace("%domain%", domain)
        http_config = http_config.replace("%docker_server%", dockerserver.ip)
        http_config = http_config.replace(
            "%longpolling_port%", str(longpolling_port))
        http_config = http_config.replace("%xmlrpc_port%", str(xmlrpc_port))

        odoo_config = dockerimage.odoo_config
        odoo_config = odoo_config.replace("%domain%", domain)

        extra_parameters = dockerimage.extra_parameters
        extra_parameters = extra_parameters.replace("%domain%", domain)

        container_instance_vals = {
            "domain": domain,
            "market_type_id": markettype.id,
            "module_ids": module_ids,
            "dbserver_id": dbserver.id,
            "httpserver_id": httpserver.id,
            "docker_image_id": dockerimage.id,
            "docker_server_id": dockerserver.id,
            "template_id": template.id,
            "http_config": http_config,
            "odoo_config": odoo_config,
            "port_mapping_ids": port_mapping_ids,
            "volume_mapping_ids": volume_mapping_ids,
            "extra_parameters": extra_parameters
        }

        container_instance = self.create(container_instance_vals)
        container_instance.deploy_addons()
        container_instance.deploy_filestore()
        container_instance.deploy_logging()
        container_instance.deploy_config()
        container_instance.configure_http_server()
        container_instance.create_docker_container()
        container_instance.start_docker_container()

        return admin_pwd, template, dockerserver.ip, xmlrpc_port

    @api.multi
    def create_docker_container(self):

        command = "docker create --name %s" % self.domain
        for port_mapping in self.port_mapping_ids:
            command += " -p %s:%s" % (port_mapping.port_map,
                                      port_mapping.port_id.portnumber)

        command += " --add-host=postgres:%s" % self.dbserver_id.ip
        command += " -e DB_PORT_5432_TCP_ADDR=postgres"
        command += " -e DB_PORT_5432_TCP_PORT=%s" % self.dbserver_id.port
        command += " -e DB_ENV_POSTGRES_USER=%s" % self.dbserver_id.username
        command += " -e DB_ENV_POSTGRES_PASSWORD=%s" % self.dbserver_id.pwd
        command += " -e DBFILTER=^%s$" % self.domain

        if self.restart_policy:
            command += " --restart %s" % self.restart_policy

        if self.extra_parameters:
            command += " %s" % self.extra_parameters

        for volume_mapping in self.volume_mapping_ids:
            command += " -v %s:%s" % (volume_mapping.volume_map,
                                      volume_mapping.volume_id.path)

        command += " %s" % self.docker_image_id.image_name

        executedcommand_env = self.env["botc.executedcommand"]
        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.docker_server_id.ip, self.docker_server_id.username,
            self.docker_server_id.pwd, self.docker_server_id.port, command)

        return executedcommand_env.create_action(log)

    @api.multi
    def delete_docker_container(self):
        command = "docker rm %s" % self.domain

        executedcommand_env = self.env["botc.executedcommand"]
        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.docker_server_id.ip, self.docker_server_id.username,
            self.docker_server_id.pwd, self.docker_server_id.port,
            command)

        return executedcommand_env.create_action(log)

    @api.multi
    def stop_docker_container(self):
        command = "docker stop %s" % self.domain

        executedcommand_env = self.env["botc.executedcommand"]
        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.docker_server_id.ip, self.docker_server_id.username,
            self.docker_server_id.pwd, self.docker_server_id.port, command)

        return executedcommand_env.create_action(log)

    @api.multi
    def start_docker_container(self):
        command = "docker start %s" % self.domain
        executedcommand_env = self.env["botc.executedcommand"]

        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.docker_server_id.ip, self.docker_server_id.username,
            self.docker_server_id.pwd, self.docker_server_id.port, command)

        return executedcommand_env.create_action(log)

    @api.multi
    def inspect_docker_container(self):
        command = "docker inspect %s" % self.domain

        executedcommand_env = self.env["botc.executedcommand"]
        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.docker_server_id.ip, self.docker_server_id.username,
            self.docker_server_id.pwd, self.docker_server_id.port, command)

        return executedcommand_env.create_action(log)

    @api.multi
    def configure_http_server(self):
        try:
            http_server = self.httpserver_id
            filename = "/tmp/%s.conf" % self.domain
            filecontents = self.http_config

            executedcommand_env = self.env["botc.executedcommand"]
            log = executedcommand_env.sftp_write_to_file(
                http_server.ip, http_server.username, http_server.pwd,
                http_server.port, filename, filecontents)

            move_command = "sudo mv /tmp/%s.conf %s" % (
                self.domain, self.httpserver_id.config_path)

            stdout, stderr, log = executedcommand_env.execute_ssh_command(
                http_server.ip, http_server.username, http_server.pwd,
                http_server.port, move_command)

            stdout, stderr, log = executedcommand_env.execute_ssh_command(
                http_server.ip, http_server.username, http_server.pwd,
                http_server.port, self.httpserver_id.reload_command)
        except Exception as e:
            _logger.info("Exception %s", e)
            return executedcommand_env.create_action(log)

        return executedcommand_env.create_action(log)

    @api.multi
    def unconfigure_http_server(self):
        try:
            http_server = self.httpserver_id

            move_command = "sudo rm %s/%s.conf " % (
                self.httpserver_id.config_path, self.domain)

            executedcommand_env = self.env["botc.executedcommand"]
            stdout, stderr, log = executedcommand_env.execute_ssh_command(
                http_server.ip, http_server.username,
                http_server.pwd,
                http_server.port, move_command)

            stdout, stderr, log = executedcommand_env.execute_ssh_command(
                http_server.ip, http_server.username,
                http_server.pwd,
                http_server.port,
                self.httpserver_id.reload_command)
        except:
            return executedcommand_env.create_action(log)

        return executedcommand_env.create_action(log)

    @api.multi
    def deploy_filestore(self):
        try:
            log = None
            docker_server = self.docker_server_id
            executedcommand_env = self.env["botc.executedcommand"]

            filestore_path = next(
                (mapping.volume_map for mapping in self.volume_mapping_ids
                 if mapping.volume_id.type == "filestore"), None)
            if filestore_path:
                mkdirbase_command = "sudo mkdir -p %s" % (filestore_path)

                stdout, stderr, log = executedcommand_env.execute_ssh_command(
                    docker_server.ip, docker_server.username,
                    docker_server.pwd,
                    docker_server.port, mkdirbase_command)

                chmod_command = "sudo chmod -R 777 %s" % (filestore_path)
                stdout, stderr, log = executedcommand_env.execute_ssh_command(
                    docker_server.ip, docker_server.username,
                    docker_server.pwd,
                    docker_server.port,
                    chmod_command)

        except Exception as e:
            _logger.info("Exception %s", e)
            return executedcommand_env.create_action(log)

        return executedcommand_env.create_action(log)

    @api.multi
    def deploy_logging(self):
        executedcommand_env = self.env["botc.executedcommand"]

        try:
            log = None
            docker_server = self.docker_server_id

            logging_path = next(
                (mapping.volume_map for mapping in self.volume_mapping_ids if
                 mapping.volume_id.type == "logging"), None)
            if logging_path:
                mkdirbase_command = "sudo mkdir -p %s" % (logging_path)

                stdout, stderr, log = executedcommand_env.execute_ssh_command(
                    docker_server.ip,
                    docker_server.username,
                    docker_server.pwd,
                    docker_server.port,
                    mkdirbase_command)

                chmod_command = "sudo chmod -R 777 %s" % (logging_path)
                stdout, stderr, log = executedcommand_env.execute_ssh_command(
                    docker_server.ip, docker_server.username,
                    docker_server.pwd,
                    docker_server.port,
                    chmod_command)

        except Exception as e:
            _logger.info("Exception %s", e)
            return executedcommand_env.create_action(log)

        return executedcommand_env.create_action(log)

    @api.multi
    def deploy_config(self):
        try:
            log = None
            docker_server = self.docker_server_id
            executedcommand_env = self.env["botc.executedcommand"]
            config_path = next(
                (mapping.volume_map for mapping in self.volume_mapping_ids if
                 mapping.volume_id.type == "config"), None)

            if config_path and self.odoo_config:
                mkdirbase_command = "sudo mkdir -p %s" % (config_path)

                stdout, stderr, log = executedcommand_env.execute_ssh_command(
                    docker_server.ip,
                    docker_server.username,
                    docker_server.pwd,
                    docker_server.port,
                    mkdirbase_command)

                chmod_command = "sudo chmod -R 777 %s" % (config_path)
                stdout, stderr, log = executedcommand_env.execute_ssh_command(
                    docker_server.ip, docker_server.username,
                    docker_server.pwd,
                    docker_server.port,
                    chmod_command)

                filecontents = self.odoo_config

                log = executedcommand_env.sftp_write_to_file(
                    docker_server.ip, docker_server.username,
                    docker_server.pwd,
                    docker_server.port, config_path + "/openerp-server.conf",
                    filecontents)

        except Exception as e:
            _logger.info("Exception %s", e)
            return executedcommand_env.create_action(log)

        return executedcommand_env.create_action(log)

    @api.multi
    def deploy_addons(self):
        try:
            log = None
            docker_server = self.docker_server_id
            executedcommand_env = self.env["botc.executedcommand"]

            addons_path = next(
                (mapping.volume_map for mapping in self.volume_mapping_ids
                 if mapping.volume_id.type == "addons"), None)
            if not addons_path:
                return

            mkdirbase_command = "sudo mkdir -p %s" % (addons_path)
            stdout, stderr, log = executedcommand_env.execute_ssh_command(
                docker_server.ip, docker_server.username,
                docker_server.pwd,
                docker_server.port, mkdirbase_command)

            if self.template_id:
                local_filestore = self.template_id.template_apps_location
                zip_file = local_filestore.split("/")[::-1][0]
                log = executedcommand_env.sftp_put_file(
                    docker_server.ip, docker_server.username,
                    docker_server.pwd,
                    docker_server.port, local_filestore,
                    "/tmp/%s" % zip_file)

                unzip_command = "sudo unzip /tmp/%s -d %s" % (
                    zip_file, addons_path)
                stdout, stderr, log = executedcommand_env.execute_ssh_command(
                    docker_server.ip,
                    docker_server.username,
                    docker_server.pwd,
                    docker_server.port,
                    unzip_command)

            chmod_command = "sudo chmod -R 777 %s" % (addons_path)
            stdout, stderr, log = executedcommand_env.execute_ssh_command(
                docker_server.ip, docker_server.username,
                docker_server.pwd,
                docker_server.port,
                chmod_command)

        except Exception as e:
            _logger.info("Exception %s", e)

            return executedcommand_env.create_action(log)

        return executedcommand_env.create_action(log)

    @api.multi
    def image_history(self):
        command = "docker history %s" % self.docker_image_id.image_name
        executedcommand_env = self.env["botc.executedcommand"]
        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.docker_server_id.ip, self.docker_server_id.username,
            self.docker_server_id.pwd, self.docker_server_id.port,
            command)

        return executedcommand_env.create_action(log)

    @api.multi
    def container_top(self):
        command = "docker top %s" % self.domain
        executedcommand_env = self.env["botc.executedcommand"]
        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.docker_server_id.ip, self.docker_server_id.username,
            self.docker_server_id.pwd, self.docker_server_id.port,
            command)

        return executedcommand_env.create_action(log)

    @api.multi
    def list_containers(self):

        return self.docker_server_id.list_containers()

    @api.multi
    def docker_info(self):

        return self.docker_server_id.docker_info()

    @api.multi
    def docker_images(self):

        return self.docker_server_id.docker_images()
