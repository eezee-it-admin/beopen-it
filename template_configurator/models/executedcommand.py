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
import logging
import paramiko
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ExecutedCommand(models.Model):
    _name = "botc.executedcommand"
    _rec_name = "datetime_executed"

    datetime_executed = fields.Datetime(string="Time Executed", readonly=True)
    command = fields.Text(string="Command", readonly=True)
    standard_output = fields.Text(string="Standard Output", readonly=True)
    standard_error = fields.Text(string="Standard Error", readonly=True)

    @api.model
    def create_action(self, log):
        if not log:
            return {}

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

    def execute_ssh_command(self, ip, username, pwd, port, command):
        _logger.info("Executing %s on %s:%s with user %s",
                     command, ip, port, username)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(ip, username=username, password=pwd, port=port)
        stdin, stdout, stderr = client.exec_command(command)
        stdout_string = stdout.read()
        stderr_string = stderr.read()
        client.close()

        vals = {
            "datetime_executed": fields.Datetime.now(),
            "command": command,
            "standard_output": stdout_string,
            "standard_error": stderr_string
        }

        log = super(ExecutedCommand, self).create(vals)
        return stdout_string, stderr_string, log

    def sftp_write_to_file(self, ip, username, pwd, port, filename,
                           filecontents):
        _logger.info("Writing contents to %s in %s:%s with user %s",
                     filename, ip, port, username)
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

        vals = {
            "datetime_executed": fields.Datetime.now(),
            "command": "sftp %s" % filename,
            "standard_output": file_info,
            "standard_error": error
        }

        log = super(ExecutedCommand, self).create(vals)
        return log

    def sftp_put_file(self, ip, username, pwd, port, local_file, remote_file):
        _logger.info("Put file %s to %s in %s:%s with user %s",
                     local_file, remote_file, ip, port, username)

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

        vals = {
            "datetime_executed": fields.Datetime.now(),
            "command": "sftp %s to %s" % (local_file, remote_file),
            "standard_output": file_info,
            "standard_error": error
        }
        log = super(ExecutedCommand, self).create(vals)

        return log
