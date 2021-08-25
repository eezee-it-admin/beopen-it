# -*- encoding: utf-8 -*-
from odoo.http import request
from odoo import fields, http, _
from odoo.addons.website_helpdesk.controllers.main import WebsiteHelpdesk


class EzeeWebsiteHelpdesk(WebsiteHelpdesk):

    @http.route(['/helpdesk/<model("helpdesk.team"):team>/about_team'],
                type='http', auth="public", website=True, sitemap=True)
    def website_helpdesk_about_teams(self, team=None, **kwargs):
        res = self.website_helpdesk_teams(team, **kwargs)
        return request.render("website_helpdesk.about_team", res.qcontext)
