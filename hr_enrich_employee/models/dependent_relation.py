from odoo import fields, models, api


class HrDependentRelation(models.Model):
    _name = 'hr.dependent.relation'
    _description = 'Hr Dependent Relation'

    name = fields.Char()
    date_of_birth = fields.Date()
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Other')])
    relation = fields.Char()
    employee_id = fields.Many2one('hr.employee')
