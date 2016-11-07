import json
from openerp import http, api
from openerp.http import request
from openerp.service import db
import xmlrpclib
import logging
import openerp
from contextlib import closing
import time
import thread
import threading
import tempfile
from openerp import SUPERUSER_ID
import os
import sys
from random import choice
import requests
_logger = logging.getLogger(__name__)



class Configurator(http.Controller):

    charsets = [
        'abcdefghijklmnopqrstuvwxyz',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        '0123456789',
        '^!\$%&/()=?{[]}+~#-_.:,;<>|\\',
    ]

    def mkpassword(self, length=16):
        pwd = []
        charset = choice(self.charsets)
        while len(pwd) < length:
            pwd.append(choice(charset))
            charset = choice(list(set(self.charsets) - set([charset])))
        return "".join(pwd)

    def _write_log(self, key, text):
        key = key.lower()

        tempdir = tempfile.gettempdir();
        with open(tempdir + "/" + key + ".txt", "w") as file:
            file.write(text)
            file.flush();
            file.close();

    def _read_log(self, key):
        try:
            key = key.lower()

            tempdir = tempfile.gettempdir();
            with open(tempdir + "/" + key + ".txt", "r") as file:
                text = file.readline()
                file.close()
        except (Exception) as e:
             return "One moment please ..."

        return text

    @http.route("/configurator/<code>", auth="public", website=True)
    def configuratorForCode(self, code, *kw, **kwargs):
        error = dict()

        default_modules, markettype, optional_modules = self.get_markettype(code)

        if not markettype:
            return self.module_prices(kw, kwargs)

        apps_data = {}
        for optional_module in optional_modules:
            apps_data[optional_module.module_id.odoo_module_name] = {"price" : optional_module.module_id.price}

        module_data = {"currency": markettype.currency_id.name,
                "localeLang": {"USD": "en", "EUR": "fr"},
                "current_country": "BE",
                "apps": apps_data
                }

        module_data_json = "'" + json.dumps(module_data) + "'"

        return http.request.render("template_configurator.configurator_for_code", {
            "markettype": markettype,
            "default_modules" : default_modules,
            "optional_modules" : optional_modules,
            "module_data" : module_data_json,
            "error" : error
        })

    @http.route("/configurator/prices", auth="public", website=True)
    def module_prices(self, *kw, **kwargs):

        modules = http.request.env["botc.module"].sudo().search([("active", "=", True)]).sorted(key=lambda r: r.name)

        return http.request.render("template_configurator.module_prices", {
            "modules" : modules
        })

    def get_markettype(self, code):
        markettype = http.request.env["botc.markettype"].sudo().search([("code", "=", code)])
        default_modules = http.request.env["botc.availablemodules"].sudo(). \
            search([("markettype_id", "=", markettype.id), ("included", "=", True)]). \
            sorted(key=lambda r: (r.order, r.module_id.name))
        optional_modules = http.request.env["botc.availablemodules"].sudo(). \
            search([("markettype_id", "=", markettype.id), ("included", "=", False)]). \
            sorted(key=lambda r: (r.order, r.module_id.name))
        return default_modules, markettype, optional_modules

    @http.route("/configurator/createinstance", type="json", auth="public", website=True)
    def createinstance(self, domain, email, market_type, apps, price, flavor_id):

        domain = domain.lower()

        user = email
        password = self.mkpassword(10)
        language = "en"
        country_code = "nl_BE"

        _logger.info("Creating instance for %s", domain)

        default_modules, markettype, optional_modules = self.get_markettype(market_type)

        module_ids_to_install = [module.module_id for module in default_modules]
        module_ids_to_install += [m for (o, m) in [(module.module_id.odoo_module_name, module.module_id) for module in optional_modules] if o in apps]

        admin_pwd, template, ip, port = http.request.env["botc.containerinstance"].sudo().create_instance(domain, markettype, module_ids_to_install, flavor_id)

        modules_to_install = [(module.module_id.odoo_module_name, module.module_id.name) for module in default_modules]
        modules_to_install += [(o,m) for (o,m) in [(module.module_id.odoo_module_name, module.module_id.name) for module in optional_modules] if o in apps]

        description = "URL : http://" + domain + ".beopen.be\n"
        description += "Username : " + user + "\n"
        description += "Password : " + password + "\n\n"
        description += "Package  : " + markettype.name + "\n"
        description += "Installed modules : " + ', '.join([m for (o,m) in modules_to_install]) + "\n"
        description += "Price after trial : " + price + " " + markettype.currency_id.name

        _logger.info("Create lead for %s", domain)

        values_lead = {
            "name": "new database " + domain,
            "description": description,
            "planned_revenue": price,
            "email_from": email
        }

        lead = http.request.env["crm.lead"].sudo().create(values_lead)

        mail_template_id = http.request.env['ir.model.data'].sudo().xmlid_to_res_id('template_configurator.mail_template_configurator')
        if mail_template_id:
            _logger.info("Send mail for %s to %s", domain, email)
            mail_template = http.request.env['mail.template'].sudo().browse(mail_template_id)
            mail_template.send_mail(lead.id, True)
        else:
            _logger.warning("No email template found for sending email to the configurator user")


        template_user = template.template_username
        template_passwd = template.template_password
        template_backup = template.template_backup_location

        _logger.info("Fork process for creating %s", domain)
        p1 = os.fork()
        if p1 != 0:
            _logger.info("Waiting for p1")
            os.waitpid(p1, 0)
            _logger.info("Stopped waiting for p1")
        else:
            p2 = os.fork()
            if p2 != 0:
                _logger.info("Exiting p2")
                os._exit(0)
            else:
                self._create_database(country_code, domain, language, markettype, modules_to_install, password, user,
                                      template_user, template_passwd, ip, port, template_backup, admin_pwd)

            _logger.info("Exiting p1")
            os._exit(0)
        _logger.info("Process forked for %s", domain)

        return {"type": "ok"}

    @http.route("/configurator/checkdbname", type="json", auth="public", website=True)
    def checkdbname(self, domain):
        domain = domain.lower()

        if not domain.isalnum():
            return {"type": "error", "message": "Only alfanumeric characters are allowed."}

        if not domain is None and len(domain) < 5:
            return {"type": "error", "message": "Must be minimum 5 characters."}

        db = openerp.sql_db.db_connect('postgres')
        with closing(db.cursor()) as cr:
            cr.execute("SELECT datname FROM pg_database WHERE datname = %s",
                       (domain,))
            if cr.fetchall():
                return {"type": "error", "message": "Database already exists."}

        return {"type": "ok"}


    @http.route("/configurator/progress", type="json", auth="public", website=True)
    def progress(self, domain):
        text = self._read_log(domain)
        return {"message": text}

    def _create_database(self, country_code, domain, language, markettype, modules_to_install, password, user, template_user,
                         template_passwd, ip, port, template_backup, admin_pwd):
        try:
            _logger.info("Forked process for %s", domain)
            self._write_log(domain, "Creating instance {0}".format(domain))
            # Create database
            url = "http://%s:%s" % (ip, port)

            success = False
            counter = 0
            common = ""

            while not success:
                try:
                    _logger.info("Check Database Manager on %s:%s", ip, port)
                    restore_url = "%s/web/database/manager" % url
                    response = requests.get(restore_url)
                    if response.status_code != 200:
                        raise Exception("Response not 200")
                    success = True
                except Exception as e:
                    _logger.info("Error on Check Database Manager %s", str(e))
                    counter += 1
                    if counter > 5:
                        raise Exception("Aborted after 5 tries...")
                    time.sleep(5)

            if template_backup:
                # master_pwd = openerp.tools.config['admin_passwd']
                _logger.info("Restore database to %s", url)
                restore_url = "%s/web/database/restore" % url
                file = open(template_backup,'r').read()
                files = {'backup_file': ('backup_file', file)}
                response = requests.post(restore_url, data={"name":domain,
                                                            "copy":True,
                                                            "master_pwd":admin_pwd
                                                            }, files=files)

                _logger.info("Response = %s", response)


            else:
                raise ValueError("No database template defined")
                # _logger.info("Create database %s to %s", template_database, domain)
                # db.exp_create_database(domain, False, language, password, user, country_code)

            #authenticate to new created database
            _logger.info("Authenticate on instance %s on %s:%s", domain, ip, port)
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(domain, template_user, template_passwd, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            success = True


            _logger.info("Receiving ID's for modules on instance %s", domain)
            #Install modules
            IDList = []
            for module_to_install in modules_to_install:
                module_record = models.execute_kw(domain, uid, template_passwd, 'ir.module.module', 'search',
                                                  [[['name', '=', module_to_install[0]]]])
                IDList.append((module_record[0], module_to_install[1]))

            _logger.info("ID's for modules on instance %s are %s", domain, IDList)
            if len(IDList) > 0:
                for (id, name) in IDList:
                    self._write_log(domain, "Installing module {0}".format(name.encode('utf-8')))

                    _logger.info("Installing module %s in instance %s", name.encode('utf-8'), domain)

                    models.execute_kw(domain, uid, template_passwd, 'ir.module.module', 'button_immediate_install',
                                      [[id],
                                       {'lang': language, 'tz': 'false', 'uid': uid, 'search_default_app': '1',
                                        'params': {'action': '36'}}])

            _logger.info("Resetting password instance %s", domain)
            models.execute_kw(domain, uid, template_passwd, 'res.users', 'write',[[1], {
                        'login': user, 'password': password
                    }])
            _logger.info("Instance %s ready", domain)
            self._write_log(domain, "Done")

            sys.exit(0)

        except (db.DatabaseExists) as e:
            self._write_log(domain, "ERROR : Unexpected by creating instance %s".format(domain))
            _logger.info("Error by creating instance %s : %s", domain, str(e))
            sys.exit(0)
        except (Exception) as e :
            self._write_log(domain, "ERROR : Unexpected by creating instance %s".format(domain))
            _logger.info("Error by creating instance %s : %s", domain, str(e))
            sys.exit(0)


