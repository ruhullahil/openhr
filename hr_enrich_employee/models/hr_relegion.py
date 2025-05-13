from odoo import fields, models, api


class HrReligion(models.Model):
    _name = 'hr.religion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hr Religion'

    name = fields.Char()
