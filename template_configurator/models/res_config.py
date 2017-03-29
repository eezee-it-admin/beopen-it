from odoo  import models, fields

class TemplateConfiguratorConfiguration(models.TransientModel):
    _name = 'botc.config.settings'
    _inherit = 'res.config.settings'

    domain = fields.Char(string="Domain")
    trial_days = fields.Integer("Trial period (days)")
    success_message = fields.Char(string="Success message")
    error_message = fields.Char(string="Error message")
    logo = fields.Binary(string="Logo")
    salesdocument_type = fields.Selection([('lead', 'Lead'), ('quotation', 'Quotation'), ('sales order', 'Sales order')], required=True,
        help="Type of sales document to be created when configuration is confirmed")

    def set_domain(self):
        self.env['ir.config_parameter'].set_param(
            'botc_domain', (self.domain or '').strip(), groups=['base.group_system'])

    def get_default_domain(self, fields):
        domain = self.env['ir.config_parameter'].get_param('botc_domain', default='beopen.be')
        return dict(domain=domain)

    def set_trial_days(self):
        self.env['ir.config_parameter'].set_param(
            'botc_trial_days', (str(self.trial_days) or '').strip(), groups=['base.group_system'])

    def get_default_trial_days(self, fields):
        trial_days = self.env['ir.config_parameter'].get_param('botc_trial_days', default='30')
        return dict(trial_days=int(trial_days))

    def set_success_message(self):
        self.env['ir.config_parameter'].set_param(
            'botc_success_message', (self.success_message or '').strip(), groups=['base.group_system'])

    def get_default_success_message(self, fields):
        success_message = self.env['ir.config_parameter'].get_param('botc_success_message', default='Your BeOpen experience is ready at <a target=\\"_blank\\" href=\\"http://<subdomain>.<domain>\\">http://<subdomain>.<domain>.</a> <br/>You can login with your credentials that have been sent to <email>')
        return dict(success_message=success_message)

    def set_error_message(self):
        self.env['ir.config_parameter'].set_param(
            'botc_error_message', (self.error_message or '').strip(), groups=['base.group_system'])

    def get_default_error_message(self, fields):
        error_message = self.env['ir.config_parameter'].get_param('botc_error_message', default='Oops..., an unexpected error occured.<br/>Please <a href=\\"https://beopen.be/page/contactus\\">contact us</a> to set up your environment manually.')
        return dict(error_message=error_message)

    def set_logo(self):
        self.env['ir.config_parameter'].set_param(
            'botc_logo', (self.logo or '').strip(), groups=['base.group_system'])

    def get_default_logo(self, fields):
        logo = self.env['ir.config_parameter'].get_param('botc_logo')
        return dict(logo=logo)


    def set_salesdocument_type(self):
        self.env['ir.config_parameter'].set_param(
            'salesdocument_type', (self.salesdocument_type or '').strip(), groups=['base.group_system'])

    def get_default_salesdocument_type(self, fields):
        salesdocument_type = self.env['ir.config_parameter'].get_param('salesdocument_type')
        if not salesdocument_type:
            if self.env['res.users'].has_group('crm.group_use_lead'):
                salesdocument_type = 'lead'
            else:
                salesdocument_type = 'sales order'
        return dict(salesdocument_type=salesdocument_type)