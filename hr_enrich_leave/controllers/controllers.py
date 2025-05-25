# -*- coding: utf-8 -*-
# from odoo import http


# class HrEnrichLeave(http.Controller):
#     @http.route('/hr_enrich_leave/hr_enrich_leave', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_enrich_leave/hr_enrich_leave/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_enrich_leave.listing', {
#             'root': '/hr_enrich_leave/hr_enrich_leave',
#             'objects': http.request.env['hr_enrich_leave.hr_enrich_leave'].search([]),
#         })

#     @http.route('/hr_enrich_leave/hr_enrich_leave/objects/<model("hr_enrich_leave.hr_enrich_leave"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_enrich_leave.object', {
#             'object': obj
#         })

