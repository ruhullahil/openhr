from dateutil.relativedelta import relativedelta
from reportlab.graphics.transform import inverse

from odoo import api, fields, models
from odoo.api import private


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
    driving_license = fields.Char()
    relation_with_em_contact = fields.Char()
    tin = fields.Char(string='TIN')
    identification_type = fields.Selection([('nid','NID'),('birth','Birth Certificate')])

    # permanent Address
    permanent_street = fields.Char(string="Permanent Street", groups="base.group_user")
    permanent_street2 = fields.Char(string="Permanent Street2", groups="base.group_user")
    permanent_city = fields.Char(string="Permanent City", groups="base.group_user")
    permanent_state_id = fields.Many2one(
        "res.country.state", string="Permanent State",
        domain="[('country_id', '=?', permanent_country_id)]",
        groups="base.group_user")
    permanent_zip = fields.Char(string="Permanent Zip", groups="base.group_user")
    permanent_country_id = fields.Many2one("res.country", string="Permanent Country", groups="base.group_user")

    # reg related info
    reg_submission_date = fields.Date()
    last_working_date = fields.Date()
    final_setelment_date = fields.Date(string='Final Settlement Date')


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



    def fetch(self, field_names):
        if self.browse().has_access('read'):
            return super().fetch(field_names)
        # TODO : have to re-write comment
        # HACK: retrieve publicly available values from hr.employee.public and
        # copy them to the cache of self; non-public data will be missing from
        # cache, and interpreted as an access error
        public_fields = self.env['hr.employee.public']._fields
        new_fields = [fname for fname in field_names if fname in public_fields]
        res = super().fetch(new_fields)
        return res


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    rank_id = fields.Many2one('hr.job.rank')
    religion_id = fields.Many2one('hr.religion')
    blood_group = fields.Selection(
        [('a_positive', 'A+'), ('a_neg', 'A-'), ('b_positive', 'B+'), ('b_neg', 'B-'), ('ab_positive', 'AB+'),
         ('ab_neg', 'AB-')])

    @api.depends('department_id')
    def _compute_parent_id(self):
        for employee in self:
            employee.parent_id = None

HR_WRITABLE_FIELDS = [
        'blood_group',
        'father_name',
        'mother_name',
        'permanent_street',
        'permanent_street2',
        'permanent_city',
        'permanent_state_id',
        'permanent_zip',
        'permanent_country_id',
        'tin',
        'driving_license',
        'identification_type',

    ]

HR_READABLE_FIELDS = [
    'job_rank_id',
    'religion_id',
    'date_of_joining',
    'employment_year',
    'barcode',
    'relation_with_em_contact',
]


class InheritResUser(models.Model):
    _inherit = 'res.users'



    job_rank_id = fields.Many2one(related='employee_id.rank_id', readonly=False, related_sudo=False)
    religion_id = fields.Many2one(related='employee_id.religion_id', readonly=False, related_sudo=False)
    blood_group = fields.Selection(related='employee_id.blood_group', readonly=False, related_sudo=False)
    father_name = fields.Char(related='employee_id.father_name', readonly=False, related_sudo=False)
    mother_name = fields.Char(related='employee_id.mother_name', readonly=False, related_sudo=False)

    permanent_street = fields.Char(string="Permanent Street", related='employee_id.permanent_street', readonly=False, related_sudo=False)
    permanent_street2 = fields.Char(string="Permanent Street2", related='employee_id.permanent_street2', readonly=False, related_sudo=False)
    permanent_city = fields.Char(string="Permanent City", related='employee_id.permanent_city', readonly=False, related_sudo=False)
    permanent_state_id = fields.Many2one(
        "res.country.state", string="Permanent State",related='employee_id.permanent_state_id', readonly=False, related_sudo=False)
    permanent_zip = fields.Char(string="Permanent Zip", related='employee_id.permanent_zip', readonly=False, related_sudo=False)
    permanent_country_id = fields.Many2one("res.country", string="Permanent Country", related='employee_id.permanent_country_id', readonly=False, related_sudo=False)
    date_of_joining = fields.Date(related='employee_id.date_of_joining', readonly=True, related_sudo=False)
    tin = fields.Char(related='employee_id.tin', readonly=True, related_sudo=False)
    driving_license = fields.Char(related='employee_id.driving_license', readonly=True, related_sudo=False)
    relation_with_em_contact = fields.Char(related='employee_id.relation_with_em_contact', readonly=True, related_sudo=False)
    identification_type = fields.Selection(related='employee_id.identification_type', readonly=True, related_sudo=False)
    employment_year = fields.Integer(related='employee_id.employment_year')
    barcode = fields.Char(related='employee_id.barcode')

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + HR_READABLE_FIELDS + HR_WRITABLE_FIELDS

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + HR_WRITABLE_FIELDS














