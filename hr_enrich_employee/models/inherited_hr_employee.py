from dateutil.relativedelta import relativedelta
from reportlab.graphics.transform import inverse

from odoo import api, fields, models

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee','utm.mixin']
    _description = 'Hr Employee'


    date_of_joining = fields.Date()
    salary = fields.Monetary(compute='_compute_contract_salary',inverse='_inverse_contract_salary',currency_field='currency_id')
    contract_type_id = fields.Many2one('hr.contract.type',compute='_compute_contract_type_id',inverse='_inverse_contract_contract_type_id')
    is_source_employee_invisible = fields.Boolean(compute='_compute_is_source_employee_invisible')
    source_employee_id = fields.Many2one('hr.employee')
    employment_location_id = fields.Many2one('location.configuration')
    age = fields.Integer(compute='_compute_age')
    employment_year = fields.Integer(compute='_compute_employment_year')


    father_name = fields.Char()
    mother_name = fields.Char()


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

    # reg related info
    reg_submission_date = fields.Date()
    last_working_date = fields.Date()
    final_setelment_date = fields.Date()


    @api.depends('source_id','source_id.is_internal')
    def _compute_is_source_employee_invisible(self):
        for employee in self:
                employee.is_source_employee_invisible = not employee.source_id.is_internal

    @api.depends('birthday')
    def _compute_age(self):
        for rec in self:
            rec.age = rec._get_age() or 0

    @api.depends('date_of_joining')
    def _compute_employment_year(self):
        for rec in self:
            target_date = fields.Date.context_today(self.env.user)
            rec.employment_year = relativedelta(target_date, self.date_of_joining).years if self.date_of_joining else 0





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
            employee.contract_type_id = employee.contract_id.contract_type_id or None

    def _inverse_contract_contract_type_id(self):
        for employee in self:
            employee.contract_id.contract_type_id = employee.contract_type_id


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    rank_id = fields.Many2one('hr.job.rank')
    religion_id = fields.Many2one('hr.religion')
    blood_group = fields.Selection(
        [('a_positive', 'A+'), ('a_neg', 'A-'), ('b_positive', 'B+'), ('b_neg', 'B-'), ('ab_positive', 'AB+'),
         ('ab_neg', 'AB-')])









