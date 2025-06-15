# -*- coding: utf-8 -*-
# from odoo import http


# class HrEnrichAttendence(http.Controller):
#     @http.route('/hr_enrich_attendence/hr_enrich_attendence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_enrich_attendence/hr_enrich_attendence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_enrich_attendence.listing', {
#             'root': '/hr_enrich_attendence/hr_enrich_attendence',
#             'objects': http.request.env['hr_enrich_attendence.hr_enrich_attendence'].search([]),
#         })

#     @http.route('/hr_enrich_attendence/hr_enrich_attendence/objects/<model("hr_enrich_attendence.hr_enrich_attendence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_enrich_attendence.object', {
#             'object': obj
#         })

