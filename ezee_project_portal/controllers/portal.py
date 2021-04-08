# -*- encoding: utf-8 -*-
from operator import itemgetter
from collections import OrderedDict

from odoo import http, _
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem
from odoo.exceptions import AccessError, MissingError
from odoo.addons.project.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class ProjectPortal(CustomerPortal):

    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None,
                        sortby=None, filterby=None, search=None,
                        search_in='content', groupby='project', **kw):
        "Override to pass the filter for My Tasks"
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
        slot_obj = request.env['planning.slot']
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'start_date': {
                'label': _('Start Date'), 'order': 'start_datetime desc'
            },
            'end_date': {'label': _('End Date'), 'order': 'end_datetime desc'},
            'employee': {'label': _('Employee'), 'order': 'employee_id'},
        }
        uid = request.env.user.id
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'my_slots': {
                'label': _('My Slots'),
                'domain': [('employee_id.user_id', '=', uid),
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
            domain, order=order, limit=self._items_per_page,
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
