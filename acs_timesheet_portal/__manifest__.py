# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                ALMIGHTY CONSULTING SOLUTIONS PVT. LTD.               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://www.almightycs.com                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝
{
    'name': 'Employee Project Timesheet Entry from Portal',
    'summary': """Allow Employees to check and create their Timesheet entry from odoo portal view.""",
    'description': """
    Project Timesheet entry from portal. Portal TimeSheet Portal
    Timesheet portal create timesheet from portal User Portal Employee Portal timesheet activities for portal users time sheet portal
    Allow portal users to manage their timesheets directly in the website. Timesheets management for website

    Projekt-Arbeitszeittabelleneintrag vom Portal.
     Arbeitszeittabellenportal Arbeitszeittabelle aus Portal erstellen Benutzerportal Mitarbeiterportal Arbeitszeitblattaktivitäten für Portalbenutzer
     Erlauben Sie Portalbenutzern, ihre Arbeitszeittabellen direkt auf der Website zu verwalten. Stundenzettelverwaltung für Website
    
    Entrée de la feuille de temps du projet à partir du portail.
     Portail de feuille de temps créer une feuille de temps à partir du portail Portail des employés Portail des activités de la feuille de temps pour les utilisateurs du portail
     Autoriser les utilisateurs du portail à gérer leurs feuilles de temps directement sur le site Web. Gestion des feuilles de temps pour le site Web

    Entrada de la hoja de tiempo del proyecto desde el portal.
     Hojas de horas del portal crear hojas de horas desde el portal del usuario Portal del empleado Actividades de la hoja de horas para usuarios del portal hoja de horarios portal
     Permitir a los usuarios del portal administrar sus hojas de tiempo directamente en el sitio web. Gestión de hojas de tiempo para sitio web.
    """,
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'version': '1.0.1',
    'category': 'Human Resources',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'depends': ['hr_timesheet', 'portal'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/template.xml',
    ],
    'images': [
        'static/description/project_timesheet_portal_odoo_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': False,
    'sequence': 2,
    'price': 51,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: