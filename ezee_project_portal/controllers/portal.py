# -*- encoding: utf-8 -*-
from operator import itemgetter
from collections import OrderedDict
from dateutil.relativedelta import relativedelta

from odoo.http import request
from odoo import fields, http, _
from odoo.osv.expression import OR, AND
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.exceptions import AccessError, MissingError
from odoo.addons.project.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal


class EzeeTimesheetPortal(TimesheetCustomerPortal):

    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None,
                             search=None, search_in='all', groupby='project',
                             **kw):
        """Overwrite to add the Projects filter"""
        Timesheet_sudo = request.env['account.analytic.line'].sudo()
        values = self._prepare_portal_layout_values()
        domain =\
            request.env['account.analytic.line']._timesheet_get_portal_domain()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
        }

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            # Customization Start
            'my_entries': {
                'label': _('My Entries'),
                'domain': [("employee_id.user_id", "=", request.env.user.id)]
            },
            # Customization End
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'week': {
                'label': _('This week'),
                'domain': [('date', '>=', date_utils.start_of(today, "week")),
                           ('date', '<=', date_utils.end_of(today, 'week'))]
            },
            'month': {
                'label': _('This month'),
                'domain': [('date', '>=', date_utils.start_of(today, 'month')),
                           ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {
                'label': _('This year'),
                'domain': [('date', '>=', date_utils.start_of(today, 'year')),
                           ('date', '<=', date_utils.end_of(today, 'year'))]
            },
            'quarter': {
                'label': _('This Quarter'),
                'domain': [('date', '>=', quarter_start),
                           ('date', '<=', quarter_end)]
            },
            'last_week': {
                'label': _('Last week'),
                'domain': [('date', '>=', date_utils.start_of(last_week,
                                                              "week")),
                           ('date', '<=', date_utils.end_of(last_week,
                                                            'week'))]
            },
            'last_month': {
                'label': _('Last month'),
                'domain': [('date', '>=', date_utils.start_of(last_month,
                                                              'month')),
                           ('date', '<=', date_utils.end_of(last_month,
                                                            'month'))]
            },
            'last_year': {
                'label': _('Last year'),
                'domain': [('date', '>=', date_utils.start_of(last_year,
                                                              'year')),
                           ('date', '<=', date_utils.end_of(last_year,
                                                            'year'))]
            },
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'

        # Cutomization Start
        new_search_filters = searchbar_filters.copy()
        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search([])
        for project in projects:
            new_search_filters.update({
                str(project.id): {
                    'label': project.name,
                    'domain': [('project_id', '=', project.id)]
                }
            })

        # extends filterby criteria with project
        # (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        project_groups = Timesheet_sudo.read_group(
            [('project_id', 'not in', projects.ids)],
            ['project_id'], ['project_id']
        )
        for group in project_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name =\
                group['project_id'][1] if group['project_id'] else _('Others')
            new_search_filters.update({
                str(proj_id): {
                    'label': proj_name,
                    'domain': [('project_id', '=', proj_id)]
                }
            })

        # Add domain for multiple filters
        new_domain = []
        for fltr_by in filterby.split(','):
            new_domain = AND([new_domain, new_search_filters[fltr_by]['domain']])
        # Cutomization End

        timesheets = Timesheet_sudo
        grouped_timesheets = []
        if search and search_in:
            new_domain = AND([new_domain, [('name', 'ilike', search)]])

        timesheet_count = Timesheet_sudo.search_count(new_domain)
        # pager
        pager = portal_pager(
            url="/my/timesheets",
            url_args={
                'sortby': sortby,
                'search_in': search_in,
                'search': search,
                'filterby': fltr_by
            },
            total=timesheet_count,
            page=page,
            step=self._items_per_page
        )

        if groupby == 'project':
            order = "project_id, %s" % order
        timesheets |= Timesheet_sudo.search(new_domain, order=order,
                                           limit=self._items_per_page,
                                           offset=pager['offset'])
        if groupby == 'project':
            grouped_timesheets += [
                Timesheet_sudo.concat(*g) for k, g in groupbyelem(
                    timesheets, itemgetter('project_id'))]
        else:
            grouped_timesheets += [timesheets]

        grouped_timesheets = list(set(grouped_timesheets))
        values.update({
            'timesheets': timesheets,
            'grouped_timesheets': grouped_timesheets,
            'page_name': 'timesheet',
            'default_url': '/my/timesheets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(
                sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("hr_timesheet.portal_my_timesheets", values)


class ProjectPortal(CustomerPortal):

    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None,
                        sortby=None, filterby=None, search=None,
                        search_in='content', groupby='project', **kw):
        "Overwrite to pass the filter for My Tasks"
        task_obj = request.env['project.task']
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {
                'label': _('Last Stage Update'),
                'order': 'date_last_stage_update desc'
            },
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            # Customization start
            'my_tasks': {
                'label': _('My Tasks'),
                'domain': [('user_id', '=', request.env.user.id)],
            },
           # Customization end
        }
        searchbar_inputs = {
            'content': {
                'input': 'content',
                'label': _('Search <span class="nolabel"> (in Content)</span>')
            },
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {
                'input': 'customer',
                'label': _('Search in Customer')
            },
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
        }

        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search([])
        for project in projects:
            searchbar_filters.update({
                str(project.id): {
                    'label': project.name,
                    'domain': [('project_id', '=', project.id)]
                }
            })

        # extends filterby criteria with project
        # (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        project_groups = task_obj.read_group(
            [('project_id', 'not in', projects.ids)],
            ['project_id'], ['project_id']
        )
        for group in project_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name =\
                group['project_id'][1] if group['project_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {
                    'label': proj_name,
                    'domain': [('project_id', '=', proj_id)]
                }
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby,
                                       searchbar_filters.get('all'))['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups(
            'project.task', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR(
                    [search_domain, ['|', ('name', 'ilike', search),
                                     ('description', 'ilike', search)]]
                )
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain,
                                    [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain,
                                    [('message_ids.body', 'ilike', search)]])
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain,
                                    [('stage_id', 'ilike', search)]])
            domain += search_domain

        # task count
        task_count = task_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tasks",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'project':
            # force sort on project first to group by project in view
            order = "project_id, %s" % order
        tasks = task_obj.search(
            domain, order=order, limit=self._items_per_page,
            offset=(page - 1) * self._items_per_page)
        request.session['my_tasks_history'] = tasks.ids[:100]
        if groupby == 'project':
            grouped_tasks = [
                task_obj.concat(*g) for k, g in groupbyelem(
                    tasks, itemgetter('project_id'))]
        else:
            grouped_tasks = [tasks]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'task',
            'archive_groups': archive_groups,
            'default_url': '/my/tasks',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters':
                OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("project.portal_my_tasks", values)

    @http.route(['/my/task/<int:task_id>/edit'], type='http',
                auth="user", website=True)
    def portal_my_task_edit(self, task_id, access_token=None, **kw):
        try:
            task_sudo = self._document_check_access('project.task', task_id,
                                                    access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        return request.render("ezee_project_portal.portal_my_task_edit",
                              values)

    @http.route('/taske/save', type="http", auth="user", website=True)
    def submit_task(self, **kwargs):
        if kwargs.get('task_id') and kwargs.get('planned_hours'):
            splited_hours = kwargs.get('planned_hours', "00:00").split(':')
            hrs = (_('%0*d') % (2, float(splited_hours[0])))
            mins = (_('%0*d') % (2, float(splited_hours[1]) * 1.677966102))
            planned_hours = hrs + '.' + mins
            # Update Planned Hours in task
            request.env['project.task'].sudo().browse(
                int(kwargs.get('task_id'))
            ).write({'planned_hours': planned_hours})
        return request.redirect("/my/task/%s" % kwargs.get('task_id'))

    def _prepare_home_portal_values(self):
        values = super(ProjectPortal, self)._prepare_home_portal_values()
        slot_obj = request.env['planning.slot'].sudo()
        values['planning_slots_count'] = slot_obj.search_count([])
        return values

    @http.route(['/my/planning_slots', '/my/planning_slots/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_planning_slots(self, page=1, date_begin=None, date_end=None,
                        sortby=None, filterby=None, search=None,
                        search_in='content', groupby='project', **kw):
        "Override to pass the filter for My Tasks"
        slot_obj = request.env['planning.slot'].sudo()
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'start_date': {
                'label': _('Start Date'), 'order': 'start_datetime desc'
            },
            'end_date': {'label': _('End Date'), 'order': 'end_datetime desc'},
            'employee': {'label': _('Employee'), 'order': 'employee_id'},
        }
        today = fields.Date.today()
        uid = request.env.user.id
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("start_datetime", "=", today)]},
            'week': {
                'label': _('This week'),
                'domain': [('start_datetime', '>=', date_utils.start_of(today, "week")),
                           ('start_datetime', '<=', date_utils.end_of(today, 'week'))]
            },
            'my_slots': {
                'label': _('My Slots'),
                'domain': ['|', ('employee_id.user_id', '=', uid),
                           ('task_id.user_id', '=', uid)],
            },
        }
        searchbar_inputs = {
            'content': {
                'input': 'content',
                'label': _('Search <span class="nolabel"> (in Content)</span>')
            },
            'employee': {
                'input': 'employee',
                'label': _('Search in Employee')
            },
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
        }

        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search([])
        for project in projects:
            searchbar_filters.update({
                str(project.id): {
                    'label': project.name,
                    'domain': [('project_id', '=', project.id)]
                }
            })

        # extends filterby criteria with project
        # (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        project_groups = slot_obj.read_group(
            [('project_id', 'not in', projects.ids)],
            ['project_id'], ['project_id']
        )
        for group in project_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name =\
                group['project_id'][1] if group['project_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {
                    'label': proj_name,
                    'domain': [('project_id', '=', proj_id)]
                }
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby,
                                       searchbar_filters.get('all'))['domain']

        # Cutomization Start
        new_search_filters = searchbar_filters.copy()
        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search([])
        for project in projects:
            new_search_filters.update({
                str(project.id): {
                    'label': project.name,
                    'domain': [('project_id', '=', project.id)]
                }
            })
        # Add domain for multiple filters
        new_domain = []
        for fltr_by in filterby.split(','):
            new_domain = AND([new_domain, new_search_filters[fltr_by]['domain']])
        if new_domain:
            domain = new_domain
        # Cutomization End

        if date_begin and date_end:
            domain += [('start_datetime', '>=', date_begin),
                       ('end_datetime', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR(
                    [search_domain, [('name', 'ilike', search)]]
                )
            if search_in in ('employee', 'all'):
                search_domain = OR(
                    [search_domain, [('employee_id', 'ilike', search)]]
                )
            domain += search_domain

        # slot count
        slot_count = slot_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/planning_slots",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=slot_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'project':
            # force sort on project first to group by project in view
            order = "project_id, %s" % order
        slots = slot_obj.search(
            domain, order='start_datetime desc', limit=self._items_per_page,
            offset=(page - 1) * self._items_per_page)
        request.session['my_slots_history'] = slots.ids[:100]
        if groupby == 'project':
            grouped_slots = [
                slot_obj.concat(*g) for k, g in groupbyelem(
                    slots, itemgetter('project_id'))]
        else:
            grouped_slots = [slots]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_slots': grouped_slots,
            'page_name': 'slot',
            'default_url': '/my/planning_slots',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters':
                OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("ezee_project_portal.portal_my_slots", values)

    @http.route(['/get_planning'], type='json', auth="user", website=True)
    def planning(self, **kwargs):
        slot = request.env['planning.slot'].sudo().browse(kwargs.get('slot_id'))
        slot_data = {
            'display_name': '[#' + str(slot.id) + '] ' + slot.display_name,
            'employee': slot.employee_id.name,
            'start_datetime': slot.start_datetime,
            'end_datetime': slot.end_datetime,
            'allocated_hours': slot.allocated_hours,
            'name': slot.name,
            'project': slot.project_id.name,
            'task_id': slot.task_id.id,
            'task': slot.task_id.name,
            'color': self._format_planning_shifts(slot.role_id.color),
        }
        return request.env['ir.ui.view'].render_template('ezee_project_portal.modal_content', slot_data)

    @staticmethod
    def _format_planning_shifts(color_code):
        switch_color = {
            0: '#008784',   # No color (doesn't work actually...)
            1: '#EE4B39',   # Red
            2: '#F29648',   # Orange
            3: '#F4C609',   # Yellow
            4: '#55B7EA',   # Light blue
            5: '#71405B',   # Dark purple
            6: '#E86869',   # Salmon pink
            7: '#008784',   # Medium blue
            8: '#267283',   # Dark blue
            9: '#BF1255',   # Fushia
            10: '#2BAF73',  # Green
            11: '#8754B0'   # Purple
        }
        return switch_color[color_code]
