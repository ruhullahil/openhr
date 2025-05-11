from odoo import fields, models, api


class InheritWorkLocations(models.Model):
    _inherit = 'hr.work.location'
    is_depo = fields.Boolean(default=False)


