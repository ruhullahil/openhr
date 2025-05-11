from reportlab.graphics.transform import inverse

from odoo import api, fields, models

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee','utm.mixin']
    _description = 'Hr Employee'


    date_of_joining = fields.Date()
    rank_id = fields.Many2one('hr.job.rank')
    salary = fields.Float(compute='_compute_contract_salary',inverse='_inverse_contract_salary')
    source_employee_id = fields.Many2one('hr.employee')

    @api.depends('contract_id')
    def _compute_contract_salary(self):
        for employee in self:
            employee.salary = employee.contract_id.wage or 0.0

    def _inverse_contract_salary(self):
        for employee in self:
            employee.contract_id.wage = employee.salary




