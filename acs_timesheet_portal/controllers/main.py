# -*- coding: utf-8 -*-

from odoo import http, _
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import base64
from odoo.tools import groupby as groupbyelem
from collections import OrderedDict
from operator import itemgetter
from odoo.osv.expression import OR
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import datetime


class TimesheetPortal(CustomerPortal):

    @http.route('/timesheet/create', type="http", auth="user", website=True)
    def timesheet_create_ticket(self, **kw):
        projects = request.env['project.project'].search([])
        data = {
            'projects': projects,
        }
        return request.render('acs_timesheet_portal.create_timesheet', data)

    @http.route('/timesheet/create/submit', type="http", auth="user", website=True)
    def submit_timesheet(self, **kwargs):
        tm_date = datetime.datetime.strptime(kwargs.get('date', False), '%m/%d/%Y')
        task = kwargs.get('task', False)
        splited_unit_amount = kwargs.get('unit_amount',"00:00").split(':')

        dur_h = (_('%0*d')%(2,float(splited_unit_amount[0])))
        dur_m = (_('%0*d')%(2,float(splited_unit_amount[1])*1.677966102))
        unit_amount = dur_h+'.'+dur_m

        project_id = int(kwargs['project']) if kwargs.get('project') else False
        if not project_id:
            project_id = request.env['project.task'].search([('id','=',task)]).project_id.id

        new_timesheet = request.env['account.analytic.line'].sudo().create({
            'name': kwargs['name'],
            'project_id': project_id, 
            'task_id': int(task) if task else False,
            'employee_id': http.request.env.user.employee_ids and http.request.env.user.employee_ids[0].id or False,
            'user_id': http.request.env.user.id,
            'date': tm_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
            'unit_amount': unit_amount,
        })
        return request.redirect('/my/timesheets')

    @http.route(['/acs/tasks/<int:project>'], type='json', auth="public", methods=['POST'], website=True)
    def task_infos(self, project, **kw):
        if project:
            tasks = request.env['project.task'].search([('project_id', '=', project)])
        else:
            tasks = request.env['project.task'].search([('project_id', '!=', False)])
        data = {}
        for task in tasks:
            data[task.id] = [task.id,task.name]
        return data
