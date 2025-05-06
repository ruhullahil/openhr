# -*- coding: utf-8 -*-
# from odoo import http


# class DtApproval(http.Controller):
#     @http.route('/dt_approval/dt_approval', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dt_approval/dt_approval/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dt_approval.listing', {
#             'root': '/dt_approval/dt_approval',
#             'objects': http.request.env['dt_approval.dt_approval'].search([]),
#         })

#     @http.route('/dt_approval/dt_approval/objects/<model("dt_approval.dt_approval"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dt_approval.object', {
#             'object': obj
#         })

