# -*- coding: utf-8 -*-
# from odoo import http


# class OcaHrSign(http.Controller):
#     @http.route('/oca_hr_sign/oca_hr_sign', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oca_hr_sign/oca_hr_sign/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('oca_hr_sign.listing', {
#             'root': '/oca_hr_sign/oca_hr_sign',
#             'objects': http.request.env['oca_hr_sign.oca_hr_sign'].search([]),
#         })

#     @http.route('/oca_hr_sign/oca_hr_sign/objects/<model("oca_hr_sign.oca_hr_sign"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oca_hr_sign.object', {
#             'object': obj
#         })

