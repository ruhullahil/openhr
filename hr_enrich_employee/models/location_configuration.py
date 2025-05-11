from odoo import fields, models, api


class LocationConfiguration(models.Model):
    _name = 'location.configuration'
    _description = 'Location Configuration'

    name = fields.Char()
    location_type_id = fields.Many2one('location.type.configuration')
    parent_id = fields.Many2one('location.configuration')
    child_ids = fields.One2many('location.configuration','parent_id')
