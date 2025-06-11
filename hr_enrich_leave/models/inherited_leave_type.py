from math import ceil, floor

from odoo import fields, models, api, Command


class InheritHrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    rounding_type = fields.Selection([('floor','Floor'),('ceil','Ceiling')],delault='ceil')
    max_consecutive_period = fields.Integer()
    department_id = fields.Many2one('hr.department')
    auto_alter_max_consecutive_exit = fields.Boolean(string='Automatic change Leave Application')
    alter_sequence = fields.One2many('hr.alter.leave.sequence','parent_leave_type')
    is_auto_merge = fields.Boolean(string='Auto Marge')
    # document related fields
    is_document_required = fields.Boolean(string='Required Document')
    is_require_hand_over = fields.Boolean(string='Require Handover')




    # this fields are used for gender specific leave
    # for example paternity leave is only apply for male not female and female can avail maternity leave
    is_gender_specific_leave = fields.Boolean(default=False,string='Gender Related')
    apply_gender = fields.Selection([('male','Male'),('female','Female')])


    # this leave are only apply for spacific religion
    # for example pilgrimage leave
    is_religion_specific_leave = fields.Boolean(default=False,string='Religion Related')
    apply_religion = fields.Many2one('hr.religion')

   #  this fields for compensatory_leave
    is_compensatory_leave = fields.Boolean(string='Compensatory Leave')
    allowed_with_in_days = fields.Integer()
    restriction = fields.Selection([('must','Must Follow'),('warning','Warning')],default='warning')

#     leave for extera validity
    is_need_extra_validation = fields.Boolean(string='Extra Validation')
    max_apply_in_year = fields.Float(string='Max Apply In Calender Year')
    max_apply_in_life_time = fields.Float(string='Max Apply In Life Time')
    minimum_apply_interval = fields.Integer(string='Minimum Apply Interval')
    minimum_apply_interval_type = fields.Selection([('day', 'Day'), ('month', 'Month'), ('year', 'Year')])

    leave_validation_type = fields.Selection(selection_add=[('manager_hod', 'Manager And HOD'),('manger_hod_hr','Manager, HOD and HR')], ondelete={'manager_hod': 'cascade','manger_hod_hr':'cascade'})

#     auto clear field
    is_check_auto_clear = fields.Boolean(compute='_compute_auto_clear_data',store=True)

    @api.depends('is_auto_merge','is_gender_specific_leave','is_religion_specific_leave','is_compensatory_leave')
    def _compute_auto_clear_data(self):
        for rec in self:
            rec.is_check_auto_clear  = not rec.is_check_auto_clear or False
            if not rec.is_auto_merge:
                rec.alter_sequence = [Command.clear()]
                rec.auto_alter_max_consecutive_exit = False
            if not rec.is_gender_specific_leave:
                rec.apply_gender = None
            if not rec.is_religion_specific_leave:
                rec.apply_religion = None
            if not rec.is_compensatory_leave:
                rec.allowed_with_in_days = 0


    def get_applicability_employee_domain(self):
        self.ensure_one()
        domain = []
        if self.department_id:
            domain.append(('department_id','=',self.department_id.id))
        if self.is_gender_specific_leave:
            domain.append(('gender','=',self.apply_gender))
        if self.is_religion_specific_leave:
            domain.append(('religion_id','=',self.apply_religion.id))
        return domain

    def _get_value_after_rounding(self,value,round='ceil'):
        self.ensure_one()

        if self.rounding_type:
            round = self.rounding_type
        if round == 'ceil':
            return ceil(value)
        return floor(value)











