import json
from odoo import http, _
from odoo.service import db
import xmlrpclib
import logging
import time
import tempfile
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
        domain, trial_days = self.get_settings()

        error_message = http.request.env['ir.config_parameter'].sudo().get_param('botc_error_message')
        success_message = http.request.env['ir.config_parameter'].sudo().get_param('botc_success_message')
        logo = http.request.env['ir.config_parameter'].sudo().get_param('botc_logo')

        default_modules, markettype, optional_modules = self.get_markettype(code)

        if not markettype:
            return self.module_prices(kw, kwargs)

        optional_services = http.request.env["botc.availableservices"].sudo(). \
            search([("markettype_id", "=", markettype.id)]). \
            sorted(key=lambda r: (r.order, r.service_id.name))

        apps_data = {}
        for optional_module in optional_modules:
            apps_data[optional_module.module_id.odoo_module_name] = {"price" : optional_module.module_id.price,
                                                                     "flavor" : optional_module.flavor_id.id if optional_module.flavor_id else -1}

        services_data = {}
        for optional_service in optional_services:
            services_data["service_" + str(optional_service.service_id.id)] = {"price" : optional_service.service_id.price,
                                                                               "flavor" : optional_service.flavor_id.id if optional_service.flavor_id else -1,
                                                                               "minimum_amount" : optional_service.service_id.minimum_amount,
                                                                               "fixed_price" : optional_service.service_id.fixed_price,
                                                                               "name" : optional_service.service_id.name}

        module_data = {"price": markettype.price,
                "currency": markettype.currency_id.name,
                "localeLang": {"USD": "en", "EUR": "fr"},
                "current_country": "BE",
                "apps": apps_data,
                "services": services_data,
                "domain" : domain,
                "trial_days": trial_days,
                "success_message": success_message,
                "error_message": error_message
                }

        module_data_json = "'" + json.dumps(module_data) + "'"

        return http.request.render("template_configurator.configurator_for_code", {
            "markettype": markettype,
            "default_modules" : default_modules,
            "optional_modules" : optional_modules,
            "optional_services" : optional_services,
            "module_data" : module_data_json,
            "domain" : domain,
            "trial_days": trial_days,
            "logo": logo
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

    def get_settings(self):
        domain = http.request.env['ir.config_parameter'].sudo().get_param('botc_domain', default='beopen.be')
        trial_days = http.request.env['ir.config_parameter'].sudo().get_param('botc_trial_days', default='30')
        return domain, trial_days

    @http.route("/configurator/createinstance", type="json", auth="public", website=True)
    def createinstance(self, subdomain, email, market_type, apps, services, price, flavor_id):

        try:
            domain, trial_days = self.get_settings()

            subdomain = subdomain.lower()

            user = email
            password = self.mkpassword(10)
            language = "en"
            country_code = "nl_BE"

            _logger.info("Creating instance for %s", subdomain)

            default_modules, markettype, optional_modules = self.get_markettype(market_type)

            module_ids_to_install = [module.module_id for module in default_modules]
            module_ids_to_install += [m for (o, m) in [(module.module_id.odoo_module_name, module.module_id) for module in optional_modules] if o in apps]

            admin_pwd, template, ip, port = http.request.env["botc.containerinstance"].sudo().create_instance(subdomain, markettype, module_ids_to_install, flavor_id)

            modules_to_install = [(module.module_id.odoo_module_name, module.module_id.name) for module in default_modules]
            modules_to_install += [(o,m) for (o,m) in [(module.module_id.odoo_module_name, module.module_id.name) for module in optional_modules] if o in apps]

            description = _("URL : http://{}.{}\n").format(subdomain, domain)
            description += _("Username : {}\n").format(user)
            description += _("Password : {}\n\n").format(password)
            description += _("Package  : {}\n").format(markettype.name)
            description += _("Installed modules : {}\n").format(', '.join([m for (o,m) in modules_to_install]))
            description += _("Requested services : {}\n").format(', '.join([s for s in services]))
            description += _("Price after trial : {} {}").format(str(price) ,markettype.currency_id.name)

            _logger.info("Create lead for %s", subdomain)

            values_lead = {
                "name": "new database %s" % subdomain,
                "description": description,
                "planned_revenue": price,
                "email_from": email
            }

            lead = http.request.env["crm.lead"].sudo().create(values_lead)

            mail_template_id = http.request.env['ir.model.data'].sudo().xmlid_to_res_id('template_configurator.mail_template_configurator')
            if mail_template_id:
                _logger.info("Send mail for %s to %s", subdomain, email)
                mail_template = http.request.env['mail.template'].sudo().browse(mail_template_id)
                mail_template.send_mail(lead.id, True)
            else:
                _logger.warning("No email template found for sending email to the configurator user")

            template_user = template.template_username
            template_passwd = template.template_password
            template_backup = template.template_backup_location

            _logger.info("Fork process for creating %s", subdomain)
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
                    self._create_database(country_code, subdomain, language, markettype, modules_to_install, password, user,
                                          template_user, template_passwd, ip, port, template_backup, admin_pwd)

                _logger.info("Exiting p1")
                os._exit(0)
            _logger.info("Process forked for %s", subdomain)

            return {"type": "ok"}
        except Exception as e:
            self._write_log(subdomain, "ERROR : " + _("Unexpected error by creating instance {}").format(subdomain))
            _logger.info("Error by creating instance %s : %s", subdomain, str(e))

    @http.route("/configurator/checkdbname", type="json", auth="public", website=True)
    def checkdbname(self, subdomain):
        subdomain = subdomain.lower()

        if not subdomain.isalnum():
            return {"type": "error", "message": _("Only alfanumeric characters are allowed.")}

        if not subdomain is None and len(subdomain) < 5:
            return {"type": "error", "message": _("Must be minimum 5 characters.")}

        subdomains = http.request.env["botc.containerinstance"].sudo().search([("domain", "=", subdomain)])

        if subdomains and len(subdomains) > 0:
            return {"type": "error", "message": _("Database already exists.")}

        return {"type": "ok"}

    @http.route("/configurator/progress", type="json", auth="public", website=True)
    def progress(self, subdomain):
        text = self._read_log(subdomain)
        return {"message": text}

    def _create_database(self, country_code, subdomain, language, markettype, modules_to_install, password, user, template_user,
                         template_passwd, ip, port, template_backup, admin_pwd):
        try:
            _logger.info("Forked process for %s", subdomain)
            self._write_log(subdomain, _("Creating instance {0}").format(subdomain))
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
                response = requests.post(restore_url, data={"name":subdomain,
                                                            "copy":True,
                                                            "master_pwd":admin_pwd
                                                            }, files=files)

                _logger.info("Response = %s", response)


            else:
                raise ValueError("No database template defined")

            #authenticate to new created database
            _logger.info("Authenticate on instance %s on %s:%s", subdomain, ip, port)
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(subdomain, template_user, template_passwd, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            success = True


            _logger.info("Receiving ID's for modules on instance %s", subdomain)
            #Install modules
            IDList = []
            for module_to_install in modules_to_install:
                module_record = models.execute_kw(subdomain, uid, template_passwd, 'ir.module.module', 'search',
                                                  [[['name', '=', module_to_install[0]]]])
                if module_record:
                    IDList.append((module_record[0], module_to_install[1]))

            _logger.info("ID's for modules on instance %s are %s", subdomain, IDList)
            if len(IDList) > 0:
                for (id, name) in IDList:
                    self._write_log(subdomain, _("Installing module {0}").format(name.encode('utf-8')))

                    _logger.info("Installing module %s in instance %s", name.encode('utf-8'), subdomain)

                    models.execute_kw(subdomain, uid, template_passwd, 'ir.module.module', 'button_immediate_install',
                                      [[id],
                                       {'lang': language, 'tz': 'false', 'uid': uid, 'search_default_app': '1',
                                        'params': {'action': '36'}}])

            _logger.info("Resetting password instance %s", subdomain)
            models.execute_kw(subdomain, uid, template_passwd, 'res.users', 'write', [[1], {
                        'login': user, 'password': password
                    }])
            _logger.info("Instance %s ready", subdomain)
            self._write_log(subdomain, "Done")

            sys.exit(0)

        except (db.DatabaseExists) as e:
            self._write_log(subdomain, "ERROR : " + _("Unexpected error by creating instance {}").format(subdomain))
            _logger.info("Error by creating instance %s : %s", subdomain, str(e))
            sys.exit(0)
        except (Exception) as e :
            self._write_log(subdomain, "ERROR : " + _("Unexpected error by creating instance {}").format(subdomain))
            _logger.info("Error by creating instance %s : %s", subdomain, str(e))
            sys.exit(0)


