from odoo import fields, models, api


class LocationTypeConfiguration(models.Model):
    _name = 'location.type.configuration'
    _description = 'Location Type Configuration'

    name = fields.Char()
    description = fields.Text()
    sequence = fields.Integer()
