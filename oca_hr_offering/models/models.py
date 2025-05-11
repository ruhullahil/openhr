from odoo import models, fields, api


class HrOffering(models.Model):
    _name = 'hr.employee.offer'
    _inherit = ['portal.mixin',
                'mail.alias.mixin.optional',
                'mail.thread',
                'mail.activity.mixin',
                ]
    _description = 'Employee Offer'


    name = fields.Char()
    job_id = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department')
    address_id = fields.Many2one('res.partner')
    employment_type_id = fields.Many2one('hr.contract.type')
    salary_structure_id = fields.Many2one('hr.payroll.structure')
    employee_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract')
    candidate_id = fields.Many2one('hr.candidate')
    applicant_id = fields.Many2one('hr.applicant')
    company_id = fields.Many2one('res.company')
    currency_id = fields.Many2one('res.currency')
    monthly_pay_amount = fields.Monetary()
    total_leave_count = fields.Float()
    other_offerings = fields.Html()
    state = fields.Selection([
        ('draft','Draft'),
        ('send','Send'),
        ('accepted','Accepted'),
        ('correction','Asked Correction'),
        ('rejected','Rejected'),
    ])

    @api.depends("access_token")
    def _compute_access_url(self):
        result = super()._compute_access_url()
        for record in self:
            record.access_url = f"/hr/offer/{record.id}/{record.access_token}"
        return result




