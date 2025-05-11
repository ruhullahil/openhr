from odoo import fields, models, api


class InheritUtmSource(models.Model):
    _inherit = 'utm.source'


    is_internal = fields.Boolean(default=False)
