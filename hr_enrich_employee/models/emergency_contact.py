from odoo import fields, models, api


class EmergencyContact(models.Model):
    _name = 'emergency.contact.line'
    _description = 'Emergency Contact'
    _order = 'sequence'

    name = fields.Char()
    relation = fields.Char()
    phone = fields.Char()
    address = fields.Text()
    employee_id = fields.Many2one('hr.employee')
    sequence = fields.Integer()
