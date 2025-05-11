from reportlab.graphics.transform import inverse

from odoo import api, fields, models

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee','utm.mixin']
    _description = 'Hr Employee'


    date_of_joining = fields.Date()
    rank_id = fields.Many2one('hr.job.rank')
    salary = fields.Float(compute='_compute_contract_salary',inverse='_inverse_contract_salary')
    contract_type_id = fields.Float(compute='_compute_contract_type_id',inverse='_inverse_contract_contract_type_id')
    source_employee_id = fields.Many2one('hr.employee')
    employment_location_id = fields.Many2one('location.configuration')
    father_name = fields.Char()
    mother_name = fields.Char()
    religion_id = fields.Many2one('hr.religion')
    blood_group = fields.Selection([('a_positive','A+'),('a_neg','A-'),('b_positive','B+'),('b_neg','B-'),('ab_positive','AB+'),('ab_neg','AB-')])
    # permanent Address
    permanent_street = fields.Char(string="Permanent Street", groups="hr.group_hr_user")
    permanent_street2 = fields.Char(string="Permanent Street2", groups="hr.group_hr_user")
    permanent_city = fields.Char(string="Permanent City", groups="hr.group_hr_user")
    permanent_state_id = fields.Many2one(
        "res.country.state", string="Permanent State",
        domain="[('country_id', '=?', permanent_country_id)]",
        groups="hr.group_hr_user")
    permanent_zip = fields.Char(string="Permanent Zip", groups="hr.group_hr_user")
    permanent_country_id = fields.Many2one("res.country", string="Permanent Country", groups="hr.group_hr_user")
    reg_submission_date = fields.Date()
    last_working_date = fields.Date()
    final_setelment_date = fields.Date()



    @api.depends('contract_id','contract_id.wage')
    def _compute_contract_salary(self):
        for employee in self:
            employee.salary = employee.contract_id.wage or 0.0

    def _inverse_contract_salary(self):
        for employee in self:
            employee.contract_id.wage = employee.salary

    @api.depends('contract_id','contract_id.contract_type_id')
    def _compute_contract_type_id(self):
        for employee in self:
            employee.contract_type_id = employee.contract_id.contract_type_id or 0.0

    def _inverse_contract_contract_type_id(self):
        for employee in self:
            employee.contract_id.contract_type_id = employee.contract_type_id




