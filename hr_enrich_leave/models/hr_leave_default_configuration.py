from datetime import date, timedelta

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval, datetime, time


# ---------------------------------------------------------------------------------------------------
#                                                   Condition related models
#
#   use case
#
# -----------------------------------------------------------------------------------------------------

class AllocationCondition(models.Model):
    _name = 'leave.condition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Leave Condition'

    name = fields.Char()
    condition_for = fields.Selection([('allocation', 'Allocation'), ('carry_over', 'Carry Over')], tracking=True)
    condition_type = fields.Selection([('formula', 'Formula'), ('condition', 'Condition')], tracking=True)
    amount_python_compute = fields.Text(
        string="Python Code",
        default="""# Available variables:
    #-------------------------------
    # employee: hr.employee object
    # line: hr.default.leave.configuration.line object
    # Example:
    #-------------------------------
    # result = line.allocation_duration * (1/12 * line.remain_month)""",  # noqa: E501
    )
    application_condition = fields.Selection([('date', 'Date Range'), ('value', 'Value Range')],
                                             help='This field use for applicability for date range ignore the year year will be ignored in calculation',
                                             tracking=True)

    condition_line_ids = fields.One2many('leave.condition.line', 'condition_id')

    def _execute_python_code(self, local_dict):

        try:
            safe_eval(self.amount_python_compute, locals_dict=local_dict, mode="exec", nocopy=True)
            # print('local dict',local_dict)
            return local_dict.get('result', 0)
        except:
            raise UserError(
                _(f'{self.amount_python_compute} not executable !!'))

    def _get_condition_line_base_on_joining(self, joining_date_current_year):
        for line in self.condition_line_ids:
            start_date = line.from_date.replace(year=joining_date_current_year.year)
            end_date = line.to_date.replace(year=joining_date_current_year.year)
            if start_date <= joining_date_current_year and end_date >= joining_date_current_year:
                return line
        return self.env['leave.condition.line']

    def condition_allocation_execute(self, local_dict):
        self.ensure_one()
        config_line = local_dict['line']
        employee = local_dict['employee']
        if self.condition_type != 'condition':
            return 0

        if config_line.allocation_condition_based_in == 'joining':
            current_date = fields.Date.context_today(self)
            employee_joining_date = employee.date_of_joining or current_date
            joining_date_current_year = employee_joining_date.replace(year=current_date.year)
            condition_line = self._get_condition_line_base_on_joining(joining_date_current_year)
            if not condition_line:
                return 0
            return condition_line.quantity
        elif config_line.allocation_condition_based_in == 'present':
            # TODO : Have to add present related functionality in attendance module
            return 0

        return 0

    def _get_allocation_amount(self, local_dict):
        self.ensure_one()
        employee = local_dict['employee']
        line = local_dict['line']
        if not self.condition_for or self.condition_for != 'allocation':
            return 0
        if self.condition_type == 'formula':
            if 'result' not in local_dict:
                local_dict['result'] = 0
            return self._execute_python_code(local_dict)
        return self.condition_allocation_execute(local_dict)

    def _get_carry_over_amount(self, local_dict):
        self.ensure_one()
        employee = local_dict['employee']
        line = local_dict['line']
        if not self.condition_for or self.condition_for != 'carry_over':
            return 0
        if self.condition_type == 'formula':
            if 'result' not in local_dict:
                local_dict['result'] = 0
            return self._execute_python_code(local_dict)
        return self.condition_allocation_execute(local_dict)


class LeaveConditionLine(models.Model):
    _name = 'leave.condition.line'
    _description = 'LeaveConditionLine'
    _rec_name = 'condition_id'

    condition_id = fields.Many2one('leave.condition')
    from_date = fields.Date()
    to_date = fields.Date()
    from_range = fields.Integer()
    to_range = fields.Integer()
    quantity = fields.Float()


# ----------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------
#                                               configuration models
# ------------------------------------------------------------------------------------------------------------------------


class HrDefaultConfiguration(models.Model):
    _name = 'hr.default.leave.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HrDefaultConfiguration'
    _rec_name = 'name'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id, tracking=True)
    department_id = fields.Many2one('hr.department', tracking=True)
    name = fields.Char(tracking=True)
    start_from = fields.Date(tracking=True, required=1)
    end_date = fields.Date(tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('running', 'Running'), ('expire', 'Expire')],
                             default='draft', tracking=True)
    configuration_lines = fields.One2many('hr.default.leave.configuration.line', 'configuration_id')

    def _check_validation(self):
        self.ensure_one()
        domain = [('start_from', '<=', self.start_from), '|', ('end_date', '=', False),
                  ('end_date', '>=', self.end_date)]
        domain += [('state', 'in', ['running']), ('id', 'not in', self.ids)]
        if self.company_id:
            domain += [('company_id', 'in', self.company_id.ids)]
        if self.department_id:
            domain += [('department_id', 'in', self.department_id.ids)]

        count = self.search_count(domain)
        if count >= 1:
            raise ValidationError('Not Allowed to do this operation !!')
        return True

    def btn_confirm(self):
        current_date = fields.Date.context_today(self)
        for config in self:
            if config.state not in ('draft', 'waiting'):
                continue
            if current_date > config.start_from and config._check_validation():
                config.state = 'running'

    def btn_expire(self):
        current_date = fields.Date.context_today(self)
        for rec in self:
            if rec.state not in ('running'):
                continue
            rec.state = 'expire'
            rec.end_date = current_date - relativedelta(days=1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'default.leave.con.seq') or _("New")
        return super().create(vals_list)

    def configurate_expiration_check(self):
        current_date = fields.Date.context_today(self)
        if self.state == 'expire' and not self.end_date:
            self.end_date = current_date
        elif self.state == 'running' and self.end_date and self.end_date < current_date:
            self.state = 'expire'
        return self.state == 'running'

    # TODO : This method need to add in corn

    def condition_wise_auto_allocation(self, employees=None):
        # for auto allocation to users
        # we allocate two stage because first priority is for his own departmental allocation
        # if don't have any department related allocation then get company related allocation
        #
        # departmental allocation
        configurations = self.sudo().search([('department_id', '!=', False)])
        for configuration in configurations:
            if not configuration.configurate_expiration_check():
                continue
            configuration.configuration_lines.auto_allocation(employees)
        # generic allocation
        configurations = self.sudo().search([('department_id', '=', False)])
        for configuration in configurations:
            if not configuration.configurate_expiration_check():
                continue
            configuration.configuration_lines.auto_allocation(employees)


class HrDefaultConfigLine(models.Model):
    _name = 'hr.default.leave.configuration.line'
    _description = 'HrDefaultConfigLine'
    _rec_name = 'configuration_id'

    configuration_id = fields.Many2one('hr.default.leave.configuration')
    company_id = fields.Many2one('res.company', related='configuration_id.company_id', store=True)
    department_id = fields.Many2one('hr.department', related='configuration_id.department_id', store=True)
    leave_type_id = fields.Many2one('hr.leave.type', domain="[('allocation_validation_type','=','no_validation')]")

    # renew related fields
    is_auto_renew = fields.Boolean()
    renew_cycle = fields.Selection(
        [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')])
    renew_base = fields.Selection([('fixed', 'Fixed'), ('join_date', 'Join Date'), ('fiscal', 'Fiscal Year')])
    # fiscal year field is visible for fiscal selection and if we select it , renew base on fiscal year
    #
    fiscal_year_id = fields.Many2one('account.fiscal.year')
    renew_day = fields.Integer(help='count hole year as 365 day and day is year of that day')
    remain_month = fields.Integer(compute='_compute_remain_month')

    def _get_end_date(self):
        self.ensure_one()
        current_yer_last_date = fields.Date.context_today(self).replace(month=12, day=31)
        return self.fiscal_year_id.date_to or current_yer_last_date

    @api.depends('renew_base', 'fiscal_year_id', 'renew_day', 'renew_day')
    def _compute_remain_month(self):
        date = fields.Date.context_today(self)
        for line in self:
            end_day = line._get_end_date()
            duration = relativedelta(end_day, date)
            months = duration.months
            days = duration.days
            months += 1 if days > 15 else 0
            line.remain_month = 1 if date > end_day else months
            # print('remain month', line.remain_month)

    # carry over related fields
    is_able_carry_over = fields.Boolean()
    carry_over_type = fields.Selection([('conditional', 'Conditional'), ('fixed', 'Fixed')])
    max_carry_over_year = fields.Float()
    max_carry_over = fields.Float(compute='_compute_max_carry_over', store=True, readonly=False)
    carry_condition_based_in = fields.Selection([('joining', 'Joining'), ('present', 'Present Day')])
    carry_over_condition_id = fields.Many2one('leave.condition', domain="[('condition_for','=','carry_over')]")
    is_able_use_carry_over = fields.Boolean()
    max_carry_over_use = fields.Float()

    @api.depends('carry_over_type')
    def _compute_max_carry_over(self):
        for rec in self:
            if rec.carry_over_type == 'fixed':
                rec.max_carry_over = 0
            else:
                rec.max_carry_over = 0

    def _get_carry_over_amount(self, local_dict):
        line = local_dict['line']
        if line.allocation_type == 'fixed':
            return line.allocation_duration
        elif line.allocation_type == 'conditional':
            return line.allocation_condition_id._get_carry_over_amount(local_dict)

        return 0

    # Allocation related fields
    allocation_type = fields.Selection([('fixed', 'Fixed'), ('conditional', 'Conditional')])
    allocation_condition_based_in = fields.Selection([('joining', 'Joining'), ('present', 'Present Day')])
    allocation_condition_id = fields.Many2one('leave.condition', domain="[('condition_for','=','allocation')]")
    allocation_duration = fields.Float()
    allocation_ids = fields.One2many('hr.leave.allocation', 'config_line_id')

    def _get_allocation_amount(self, local_dict):
        line = local_dict['line']
        if line.allocation_type == 'fixed':
            return line.allocation_duration
        elif line.allocation_type == 'conditional':
            return line.allocation_condition_id._get_allocation_amount(local_dict)

        return 0

    # eligibility  related fields
    is_need_eligibility = fields.Boolean(default=True)
    eligibility_from = fields.Selection([('joining', 'Joining')])
    eligibility_interval = fields.Selection([('day', 'Day'), ('month', 'Month'), ('year', 'Year')])
    eligibility_time = fields.Float()

    #     -----------------------------------------------------------------------------------------------------------------------------------------------
    #                                    Business Method
    # ---------------------------------------------------------------------------------------------------------------------------------------------------

    def _get_applicable_employees(self):
        self.ensure_one()
        # add leave type related domain
        pre_domain = self.leave_type_id.get_applicability_employee_domain()
        if self.company_id:
            pre_domain += [('company_id', 'in', self.company_id.ids)]
        if self.department_id:
            pre_domain.append(('department_id', 'in', self.department_id.ids))
        employees = self.env['hr.employee'].sudo().search(pre_domain)
        return employees

    def _get_interval_end(self, start_date):
        self.ensure_one()
        end_date = start_date
        if self.renew_cycle == 'daily':
            end_date = start_date + relativedelta(days=1)
        elif self.renew_cycle == 'weekly':
            end_date = start_date + relativedelta(weeks=1) - relativedelta(days=1)
        elif self.renew_cycle == 'monthly':
            end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
        elif self.renew_cycle == 'yearly':
            end_date = start_date + relativedelta(years=1) - relativedelta(days=1)
        return end_date

    def _get_renew_base_start_date(self):
        start_date = fields.Date.context_today(self)
        if self.renew_cycle == 'daily':
            return start_date
        elif self.renew_cycle == 'weekly':
            week_day = start_date.weekday()
            return start_date - relativedelta(days=week_day)
        elif self.renew_cycle == 'monthly':
            return start_date.replace(day=1)
        elif self.renew_cycle == 'yearly':
            return start_date.replace(month=1, day=1)
        return start_date

    def _get_start_date(self, employee):
        self.ensure_one()

        start_date = self._get_renew_base_start_date()
        if self.renew_base == 'fixed':
            start_date += relativedelta(days=(self.renew_day - 1))
        elif self.renew_base == 'join_date':
            start_date = employee.date_of_joining.replace(
                year=start_date.year) if employee.date_of_joining else start_date
        elif self.renew_cycle == 'fiscal':
            start_date = self.fiscal_year_id.date_from or start_date
        return start_date

    def check_previous_allocation_related_info(self, employee):
        self.ensure_one()
        allocation_info = None
        domain = [('state', 'not in', ['refuse']),
                  ('employee_company_id', '=', employee.company_id.id or self.env.company.id),
                  ('employee_id', '=', employee.id), ('holiday_status_id', '=', self.leave_type_id.id)]
        if self.renew_cycle:
            start_date = self._get_start_date(employee)
            end_date = self._get_interval_end(start_date)
            date_domain = [('date_from', '<=', start_date), '|', ('date_to', '=', False), ('date_to', '>=', end_date)]
            domain += date_domain

        allocation_info = self.env['hr.leave.allocation'].sudo().search(domain, order='id desc', limit=1)
        return allocation_info

    def _get_eligibility_date_from_joining(self, joining):
        if self.eligibility_interval == 'day':
            return joining + relativedelta(days=self.eligibility_time) - relativedelta(days=1)
        elif self.eligibility_interval == 'month':
            return joining + relativedelta(months=self.eligibility_time) - relativedelta(days=1)
        elif self.eligibility_interval == 'year':
            return joining + relativedelta(years=self.eligibility_time) - relativedelta(days=1)
        else:
            return joining

    def _check_eligibility_of_employee(self, employee):
        self.ensure_one()
        if not self.is_need_eligibility:
            return True
        if self.eligibility_from != 'joining':
            return True
        current_date = fields.Date.context_today(self)
        eligible_date = self._get_eligibility_date_from_joining(employee.date_of_joining or current_date)
        if current_date >= eligible_date:
            return True
        return False

    def check_can_allocate_able(self, employee):
        self.ensure_one()
        # check eligible of employee
        if not self._check_eligibility_of_employee(employee):
            return False
        # Previous allocation Related check
        allocation = self.check_previous_allocation_related_info(employee)
        if not allocation:
            return True
        return False

    def _generate_local_dict(self, employee):
        self.ensure_one()
        local_dict = {
            'env': self.env,
            'line': self,
            'employee': employee,
            'date': date,
            'datetime': datetime,
            'timedelta': timedelta,
            'time': time,

        }
        return local_dict

    def prepare_employee_allocation(self, employee):
        self.ensure_one()
        start_date = self._get_start_date(employee)
        end_date = self._get_interval_end(start_date) if self.renew_cycle else None
        local_dict = self._generate_local_dict(employee)
        # location
        allocation_count = self.leave_type_id._get_value_after_rounding(
            self._get_allocation_amount(local_dict=local_dict))
        allocation_unit = 'number_of_days' if self.leave_type_id.request_unit != 'hour' else 'number_of_hours'
        data = {'employee_id': employee.id, 'date_from': start_date, 'date_to': end_date,
                'config_id': self.configuration_id.id, 'config_line_id': self.id,
                'holiday_status_id': self.leave_type_id.id, allocation_unit: allocation_count}
        return data

    def prepare_frozen_info(self, allocation):
        allocate_leave = allocation.max_leaves
        used_leave = allocation.leaves_taken
        available_leave = allocate_leave - used_leave
        local_dict = self._generate_local_dict(allocation.employee_id)
        carry_over_count = self.leave_type_id._get_value_after_rounding(
            self._get_carry_over_amount(local_dict=local_dict))
        data = {
            'allocation_id': allocation.id,
            'frozen_leave': available_leave,
            'carry_able_leave': carry_over_count
        }
        return data

    def auto_allocation(self, employees=None):
        allocation_datas = list()
        is_fixed_employee = True if employees else False
        for line in self:
            if not is_fixed_employee:
                employees = line._get_applicable_employees()
            for employee in employees:
                if line.check_can_allocate_able(employee):
                    allocation_datas.append(line.prepare_employee_allocation(employee))
        allocations = self.env['hr.leave.allocation'].sudo().create(allocation_datas)
        # Frozen data related works
        carry_allocation = allocations.filtered(lambda l: l.is_carry_over_allocation)
        frozen_data_list = list()
        for allocation in carry_allocation:
            previous_allocation = allocation.get_previous_allocation()
            if not previous_allocation or not previous_allocation.config_line_id:
                continue
            frozen_data_list.append(previous_allocation.config_line_id.prepare_frozen_info(previous_allocation))
        frozen_datas = self.env['frozen.allocation.info'].sudo().create(frozen_data_list)
        return allocations,frozen_datas

