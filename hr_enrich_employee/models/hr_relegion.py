from odoo import fields, models, api


class HrReligion(models.Model):
    _name = 'hr.religion'
    _description = 'Hr Religion'

    name = fields.Char()
