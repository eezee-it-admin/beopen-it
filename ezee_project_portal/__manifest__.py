# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright BeOpen-It (C) 2019
#    Author: BeOpen-It <info@beopen.be>
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
{
    "name": "EzeeIT Project Portal",
    "version": "14.0.1.0.0",
    "author": "Eezee-It",
    "website": "https://beopenit.beopen.be",
    "category": "Website/eLearning",
    "license": "LGPL-3",
    "depends": [
        "project",
        "project_forecast",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/portal_task_template.xml",
        "views/project_planning_template.xml",
    ],
    "installable": True,
}
