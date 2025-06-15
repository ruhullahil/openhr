from math import ceil, floor

from odoo import fields, models, api, Command
from odoo.exceptions import ValidationError


class InheritHrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    rounding_type = fields.Selection([('floor', 'Floor'), ('ceil', 'Ceiling')], delault='ceil')
    max_consecutive_period = fields.Integer()
    department_id = fields.Many2one('hr.department')
    auto_alter_max_consecutive_exit = fields.Boolean(string='Automatic change Leave Application')
    alter_sequence = fields.One2many('hr.alter.leave.sequence', 'parent_leave_type')
    is_auto_merge = fields.Boolean(string='Auto Marge')
    # document related fields
    is_document_required = fields.Boolean(string='Required Document')
    is_require_hand_over = fields.Boolean(string='Require Handover')
    is_need_hand_over = fields.Boolean(string='Need Handover')

    # this fields are used for gender specific leave
    # for example paternity leave is only apply for male not female and female can avail maternity leave
    is_gender_specific_leave = fields.Boolean(default=False, string='Gender Related')
    apply_gender = fields.Selection([('male', 'Male'), ('female', 'Female')])

    # this leave are only apply for spacific religion
    # for example pilgrimage leave
    is_religion_specific_leave = fields.Boolean(default=False, string='Religion Related')
    apply_religion = fields.Many2one('hr.religion')

    #  this fields for compensatory_leave
    is_compensatory_leave = fields.Boolean(string='Compensatory Leave')
    allowed_with_in_days = fields.Integer()
    restriction = fields.Selection([('must', 'Must Follow'), ('warning', 'Warning')], default='warning')

    #     leave for extera validity
    is_need_extra_validation = fields.Boolean(string='Extra Validation')
    max_apply_in_year = fields.Float(string='Max Apply In Calender Year')
    max_apply_in_life_time = fields.Float(string='Max Apply In Life Time')
    minimum_apply_interval = fields.Integer(string='Minimum Apply Interval')
    minimum_apply_interval_type = fields.Selection([('day', 'Day'), ('month', 'Month'), ('year', 'Year')])

    leave_validation_type = fields.Selection(
        selection_add=[('manager_hod', 'Manager And HOD'), ('manger_hod_hr', 'Manager, HOD and HR')],
        ondelete={'manager_hod': 'cascade', 'manger_hod_hr': 'cascade'})

    #     auto clear field
    is_check_auto_clear = fields.Boolean(compute='_compute_auto_clear_data', store=True)

    @api.depends('is_auto_merge', 'is_gender_specific_leave', 'is_religion_specific_leave', 'is_compensatory_leave')
    def _compute_auto_clear_data(self):
        for rec in self:
            rec.is_check_auto_clear = not rec.is_check_auto_clear or False
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
            domain.append(('department_id', '=', self.department_id.id))
        if self.is_gender_specific_leave:
            domain.append(('gender', '=', self.apply_gender))
        if self.is_religion_specific_leave:
            domain.append(('religion_id', '=', self.apply_religion.id))
        return domain

    def _get_value_after_rounding(self, value, round='ceil'):
        self.ensure_one()

        if self.rounding_type:
            round = self.rounding_type
        if round == 'ceil':
            return ceil(value)
        return floor(value)

    #     Frozen related fields
    frozen_ids = fields.One2many('frozen.allocation.info', 'leave_type_id')

    #     ---------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                             Base method re write
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------

    # def get_allocation_data(self, employees, target_date=None):
    #     result = super().get_allocation_data(employees,target_date)
    #     return result
    def get_current_frozen_info(self, leave_type_name, employee):
        last_allocation = self.env['hr.leave.allocation'].sudo().search(
            [('holiday_status_id.name', '=', leave_type_name), ('employee_id', '=', employee.id),
             ('employee_company_id', '=', employee.company_id.id), ('state', 'in', ['validate', ])],limit=1,order='id desc')
        if not last_allocation:
            return {}
        return last_allocation._get_previous_frozen_data()

    def get_allocation_data(self, employees, date=None):
        res = super().get_allocation_data(employees, date)
        # domain = [('frozen_ids', '!=', None)]
        # if employees:
        #     domain.append(('frozen_ids.employee_id', 'in', employees.ids))
        #
        # time_off_types = self.env['hr.leave.type'].search(domain)
        # leave_type_names = time_off_types.mapped('name')
        for employee in res:
            for leave_data in res[employee]:
                # if leave_data[0] in leave_type_names:
                frozen_data = self.get_current_frozen_info(leave_data[0],employee)
                leave_data[1]['frozen_leave'] = frozen_data.get('frozen_count', 0.0)
                leave_data[1]['usa_able_frozen_leave'] = frozen_data.get('use_able_frozen', 0.0)
                    # leave_data[1]['virtual_remaining_leaves'] = employee.sudo().total_overtime
                #     leave_data[1]['overtime_deductible'] = True
                # else:
                #     leave_data[1]['overtime_deductible'] = False
        return res

#     short leave

    is_broken_leave = fields.Boolean(string='Broken leave')


    @api.constrains('is_broken_leave','request_unit')
    def broken_leave_constrain_check(self):
        for rec in self:
            if not rec.is_broken_leave:
                continue
            if rec.request_unit not in ('half_day','hour'):
                raise ValidationError('Broken leave must be in hour or half day !!')

