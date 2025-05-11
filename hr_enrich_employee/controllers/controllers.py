# -*- coding: utf-8 -*-
# from odoo import http


# class HrEnrichEmployee(http.Controller):
#     @http.route('/hr_enrich_employee/hr_enrich_employee', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_enrich_employee/hr_enrich_employee/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_enrich_employee.listing', {
#             'root': '/hr_enrich_employee/hr_enrich_employee',
#             'objects': http.request.env['hr_enrich_employee.hr_enrich_employee'].search([]),
#         })

#     @http.route('/hr_enrich_employee/hr_enrich_employee/objects/<model("hr_enrich_employee.hr_enrich_employee"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_enrich_employee.object', {
#             'object': obj
#         })

