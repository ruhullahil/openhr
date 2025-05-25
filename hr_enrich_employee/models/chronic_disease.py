from odoo import fields, models, api


class ChronicDisease(models.Model):
    _name = 'hr.chronic.disease'
    _description = 'Chronic Disease'

    name = fields.Char()
    description = fields.Text()
