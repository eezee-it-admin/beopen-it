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


class DockerServer(models.Model):
    _name = "botc.dockerserver"

    name = fields.Char(string="Name", required=True)
    ip = fields.Char(string="IP", required=True)
    port = fields.Integer(string="SSH Port", required=True)
    username = fields.Char(string="SSH Username", required=True)
    pwd = fields.Char(string="SSH Password", required=True)
    data_path = fields.Char(string="Data Path", required=True)
    min_port = fields.Integer(string="Minimum port", required=True)
    max_port = fields.Integer(string="Maximum port", required=True)
    containerinstance_ids = fields.One2many(
        "botc.containerinstance", "docker_server_id", "Container Instances")

    @api.multi
    def list_containers(self):
        command = "docker ps"

        executedcommand_env = self.env["botc.executedcommand"]

        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.ip, self.username, self.pwd, self.port,
            command)

        return executedcommand_env.create_action(log)

    @api.multi
    def docker_info(self):
        command = "docker info"

        executedcommand_env = self.env["botc.executedcommand"]

        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.ip, self.username,
            self.pwd, self.port,
            command)

        return executedcommand_env.create_action(log)

    @api.multi
    def docker_images(self):
        command = "docker images"

        executedcommand_env = self.env["botc.executedcommand"]

        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.ip, self.username,
            self.pwd, self.port,
            command)

        return executedcommand_env.create_action(log)

    @api.multi
    def docker_stats(self):
        command = "docker stats --no-stream"

        executedcommand_env = self.env["botc.executedcommand"]
        stdout, stderr, log = executedcommand_env.execute_ssh_command(
            self.ip, self.username,
            self.pwd, self.port,
            command)

        return executedcommand_env.create_action(log)
