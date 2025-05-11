from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.base.models.assetsbundle import AssetsBundle
from odoo.addons.portal.controllers.portal import CustomerPortal


# class OcaHrOffering(http.Controller):
#     @http.route('/oca_hr_offering/oca_hr_offering', auth='public')
#     def index(self, **kw):
#         return "Hello, world"
#
#     @http.route('/oca_hr_offering/oca_hr_offering/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('oca_hr_offering.listing', {
#             'root': '/oca_hr_offering/oca_hr_offering',
#             'objects': http.request.env['oca_hr_offering.oca_hr_offering'].search([]),
#         })
#
#     @http.route('/oca_hr_offering/oca_hr_offering/objects/<model("oca_hr_offering.oca_hr_offering"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oca_hr_offering.object', {
#             'object': obj
#         })

