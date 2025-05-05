# -*- coding: utf-8 -*-
# from odoo import http


# class DtMrMi(http.Controller):
#     @http.route('/dt_mr_mi/dt_mr_mi', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dt_mr_mi/dt_mr_mi/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dt_mr_mi.listing', {
#             'root': '/dt_mr_mi/dt_mr_mi',
#             'objects': http.request.env['dt_mr_mi.dt_mr_mi'].search([]),
#         })

#     @http.route('/dt_mr_mi/dt_mr_mi/objects/<model("dt_mr_mi.dt_mr_mi"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dt_mr_mi.object', {
#             'object': obj
#         })

