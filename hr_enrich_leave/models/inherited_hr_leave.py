from datetime import datetime, time
from math import ceil

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.tools.safe_eval import pytz


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    max_consecutive_period = fields.Integer(related='holiday_status_id.max_consecutive_period', store=True)
    info_message = fields.Html(compute='_compute_info_message')
    fiscal_year = fields.Many2one('account.fiscal.year', compute='_compute_fiscal_year', store=True)

    # support document mandatory fields and functions

    is_document_required = fields.Boolean(related='holiday_status_id.is_document_required')
    #
    # def document_required_constrains(self):
    #     for rec in self:
    #         if not rec.is_document_required or rec.state not in ('confirm','validate1'):
    #             continue
    #         if not rec.supported_attachment_ids:
    #             raise ValidationError('For this leave type you need document')

    # ----------------------------------------------------------------------------------------------------------------

    # compensatory leave related fields
    is_compensatory_leave = fields.Boolean(related='holiday_status_id.is_compensatory_leave')
    compensatory_id = fields.Many2one('hr.compensatory.day')
    compensatory_allowed_with_in_days = fields.Integer(related='holiday_status_id.allowed_with_in_days')
    compensatory_restriction = fields.Selection(related='holiday_status_id.restriction')

    @api.constrains('is_compensatory_leave', 'compensatory_id', 'state')
    def check_compensatory_related_validation(self):
        for rec in self:
            today = fields.Date.context_today(self)
            if not rec.is_compensatory_leave:
                continue
            if rec.leave_type_request_unit == 'hour':
                raise ValidationError('Compensatory leave unit would be days !! please contact with Admin')
            if rec.number_of_days > 1.0001:
                raise ValidationError('Compensatory day must be 1 day')
            if rec.compensatory_id and rec.compensatory_allowed_with_in_days > 0.0001:
                compensatory_date = rec.compensatory_id.date
                max_date = compensatory_date + relativedelta(days=rec.compensatory_allowed_with_in_days)
                if rec.restriction == 'must' and max_date < today:
                    raise ValidationError('It is not possible to apply from you !! please contact with Admin')
                if rec.restriction == 'warning' and max_date < today:
                    rec.info_message = """<p class="text-danger"> you allowed compensatory date exited !!</p>"""

    @api.depends('employee_id', 'holiday_status_id', 'date_from', 'date_to')
    def _compute_fiscal_year(self):
        AccountFiscalYear = self.env["account.fiscal.year"]
        for leave in self:
            fiscalyear = AccountFiscalYear._get_fiscal_year(
                leave.company_id, leave.date_from, leave.date_to
            )
            leave.fiscal_year = fiscalyear or None

    @api.depends('employee_id', 'holiday_status_id', 'date_from', 'date_to')
    def _compute_info_message(self):
        for leave in self:
            leave.info_message = ''

    def _get_durations(self, check_leave_type=True, resource_calendar=None):
        result = {}
        for leave in self:
            hours, days = (0, 0)
            if not leave.employee_id or not leave.holiday_status_id.is_auto_merge:
                continue
            duration = leave.date_to - leave.date_from
            days = ceil(duration.total_seconds() / (24 * 3600))
            hours = ceil(duration.total_seconds() / 3600)
            result[leave.id] = (days, hours)
        if not result:
            return super(HrLeave, self)._get_durations(check_leave_type, resource_calendar)
        return result

    def _get_consecutive_number_of_time(self):
        self.ensure_one()
        # print(f'date fom : {self.date_from}')
        # # time_zone = self.employee_id.tz
        # ut_time = pytz.timezone(pytz.UTC)
        contract_start = self.date_from.astimezone(pytz.UTC)
        # check previous day leave
        last_work_day = self.employee_id._get_previous_working_daya(contract_start)
        leave = self.employee_id.get_leave_id(last_work_day)
        if leave and leave.holiday_status_id.id == self.holiday_status_id.id and self.holiday_status_id.is_auto_merge:
            duration = self.date_to - leave.date_from
            con_time = ceil(duration.total_seconds() / (24 * 3600)) if self.leave_type_request_unit != 'hour' else ceil(
                duration.total_seconds() / 3600)
            return con_time
        # next day leave check
        next_work_day = self.employee_id.get_next_work_days(contract_start)
        leave = self.employee_id.get_leave_id(next_work_day)
        if leave and leave.holiday_status_id.id == self.holiday_status_id.id and self.holiday_status_id.is_auto_merge:
            duration = leave.date_to - self.date_from
            con_time = ceil(duration.total_seconds() / (24 * 3600)) if self.leave_type_request_unit != 'hour' else ceil(
                duration.total_seconds() / 3600)
            return con_time
        return self.number_of_days if self.leave_type_request_unit != 'hour' else self.number_of_hours

    @api.constrains('max_consecutive_period', 'leave_type_request_unit', 'state')
    def _check_max_consecutive_period_validation(self):
        for rec in self:
            if rec.state in ('refuse', 'cancel'):
                continue
            if rec.max_consecutive_period <= 0:
                continue
            # number_of_days
            # number_of_hours
            number_max_consecutive_period = rec._get_consecutive_number_of_time()
            if rec.leave_type_request_unit != 'hour' and rec.max_consecutive_period < number_max_consecutive_period:
                raise ValidationError('You can not do this application !! because you exited max consecutive time !! ')
            elif rec.leave_type_request_unit == 'hour' and rec.max_consecutive_period < number_max_consecutive_period:
                raise ValidationError('You can not do this application !! because you exited max consecutive time !! ')

    #     -------------------------------------------------------------------------------------------------------------------------------------
    #                           Extra validation
    # -----------------------------------------------------------------------------------------------------------------------------------------

    is_need_extra_validation = fields.Boolean(related='holiday_status_id.is_need_extra_validation')

    def _check_max_apply_in_year(self):
        self.ensure_one()
        max_apply_year = self.holiday_status_id.max_apply_in_year or 0.0
        if not (max_apply_year > 0.001):
            return
        current_date = fields.Date.context_today(self)
        start_date = current_date.replace(day=1, month=1)
        end_date = current_date.replace(day=31, month=12)
        domain = [('company_id', '=', self.company_id.id), ('employee_id', '=', self.employee_id.id),
                  ('state', 'not in', ('cancel', 'refuse')), ('holiday_status_id', '=', self.holiday_status_id.id)]
        date_related_domain = [('date_to', '>=', start_date), ('date_to', '<=', end_date)]
        domain += date_related_domain
        appy_count = self.sudo().search_count(domain)
        if appy_count > max_apply_year:
            raise ValidationError(
                f'You can not appy {self.holiday_status_id.display_name} !! Your limit is over for this year.')

    def _check_max_in_life_time(self):
        self.ensure_one()
        max_life_time = self.holiday_status_id.max_apply_in_life_time or 0.0
        if not (max_life_time > 0.001):
            return
        domain = [('company_id', '=', self.company_id.id), ('employee_id', '=', self.employee_id.id),
                  ('state', 'not in', ('cancel', 'refuse')), ('holiday_status_id', '=', self.holiday_status_id.id)]
        appy_count = self.sudo().search_count(domain)
        if appy_count > max_life_time:
            raise ValidationError(
                f'You can not appy {self.holiday_status_id.display_name} !! Your limit is over for this leave type.')

    def _check_minimum_applied_interval(self):
        self.ensure_one()
        minimum_interval = self.holiday_status_id.minimum_apply_interval or 0.0
        minimum_interval_type = self.holiday_status_id.minimum_apply_interval_type or 'day'
        if not (minimum_interval > 0.0):
            return

        domain = [('company_id', '=', self.company_id.id), ('employee_id', '=', self.employee_id.id),
                  ('state', 'not in', ('cancel', 'refuse')), ('holiday_status_id', '=', self.holiday_status_id.id)]
        last_application = self.sudo().search(domain, order='date_to desc', limit=1)
        if not last_application:
            return

        last_application_to_date = last_application.date_to
        apply_datetime = self.date_from or datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
        if minimum_interval_type == 'day':
            duration = relativedelta(days=minimum_interval)
        elif minimum_interval_type == 'month':
            duration = relativedelta(months=minimum_interval)
        else:
            duration = relativedelta(years=minimum_interval)

        not_applicable_last_date = last_application_to_date + duration
        if apply_datetime < not_applicable_last_date:
            raise ValidationError(f'You are not allow to do {self.holiday_status_id.display_name}.')

    @api.constrains('is_need_extra_validation', 'state')
    def check_extra_validation(self):
        for rec in self:
            if not rec.is_need_extra_validation:
                continue
            # yearly validation check
            rec._check_max_apply_in_year()
            # life time max check
            rec._check_max_in_life_time()
            # minimum interval application
            rec._check_minimum_applied_interval()

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                           Approval layer related works
    # --------------------------------------------------------------------------------------------------------------------------------
    #     Handover related info
    is_require_hand_over = fields.Boolean(related='holiday_status_id.is_require_hand_over')
    is_need_hand_over = fields.Boolean(related='holiday_status_id.is_need_hand_over')
    hanover_employee = fields.Many2one('hr.employee')

    state = fields.Selection(selection_add=[('validate2', 'Third Approval'), ('validate',)],
                             ondelete={'validate2': 'cascade'})
    alternative_manager_id = fields.Many2one('hr.employee', compute='_compute_approval_related_employees',store=True)
    hod_id = fields.Many2one('hr.employee', compute='_compute_approval_related_employees',store=True)
    alternative_hod_id = fields.Many2one('hr.employee', compute='_compute_approval_related_employees',store=True)
    hr_manager_id = fields.Many2one('hr.employee', compute='_compute_approval_related_employees',store=True)
    alternative_hr_manager_id = fields.Many2one('hr.employee', compute='_compute_approval_related_employees',store=True)
    third_approver_id = fields.Many2one(
        'hr.employee', string='Third Approval', readonly=True, copy=False,
        help='This area is automatically filled by the user who validate the time off with second level (If time off type need third validation)')
    can_validate = fields.Boolean(compute='_compute_can_validate')

    @api.depends('state', 'validation_type')
    def _compute_can_validate(self):
        for holiday in self:
            holiday.can_validate = False
            if holiday.validation_type in ('both', 'manager_hod') and holiday.state in ('validate1',):
                holiday.can_validate = True
            if holiday.validation_type in ('manger_hod_hr',) and holiday.state in ('validate2',):
                holiday.can_validate = True

    @api.depends('employee_id','employee_id.parent_id','employee_id.coach_id')
    def _compute_approval_related_employees(self):
        for rec in self:
            rec.alternative_manager_id = rec.employee_id.parent_id.get_handover_employee() if rec.employee_id.parent_id else None
            rec.hod_id = rec.employee_id.coach_id or None
            rec.alternative_hod_id = rec.employee_id.coach_id.get_handover_employee() if rec.employee_id.coach_id else None
            rec.hr_manager_id = rec.employee_id.hr_manager_id or None
            rec.alternative_hr_manager_id = rec.employee_id.hr_manager_id.get_handover_employee() if rec.employee_id.hr_manager_id else None

    def get_next_state(self):
        self.ensure_one()
        next_state_dict = {
            'no_validation': {
                'confirm': 'validate'
            },
            'hr': {
                'confirm': 'validate',
            },
            'manager': {
                'confirm': 'validate',
            },
            'both': {
                'confirm': 'validate1',
                'validate1': 'validate'

            },
            'manager_hod': {
                'confirm': 'validate1',
                'validate1': 'validate',
            },
            'manger_hod_hr': {
                'confirm': 'validate1',
                'validate1': 'validate2',
                'validate2': 'validate',
            },

        }
        return next_state_dict.get(self.validation_type, {}).get(self.state, None)

    def _manager_hod_approval_check(self, state):
        self.ensure_one()
        current_user = self.env.user
        current_employee = self.env.user.employee_id
        is_hr_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        if not self.validation_type or self.validation_type != 'manager_hod':
            return None
        if not state:
            raise UserError(f'something went wrong !! ')
        if self.state == state:
            return None
        next_state = self.get_next_state()

        if self.state == 'refuse' and state == 'confirm' and not is_hr_manager:
            raise UserError('You Are not allowed to do this operation')
        if state not in (next_state, 'refuse', 'cancel'):
            raise UserError('You Are not allowed to do this operation')

        if state == 'validate1' and self.employee_id.parent_id.id != current_employee.id and current_user.id != self.employee_id.leave_manager_id.id and current_employee.id != self.alternative_manager_id.id:
            raise UserError('You Are not allowed to do this operation')
        if state == 'validate' and current_employee.id != self.hod_id.id and current_employee.id != self.alternative_hod_id.id:
            raise UserError('You Are not allowed to do this operation')
        return None

    def _manger_hod_hr_approval_check(self, state):
        self.ensure_one()
        current_user = self.env.user
        current_employee = self.env.user.employee_id
        is_hr_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        if not self.validation_type or self.validation_type != 'manger_hod_hr':
            return None
        if not state:
            raise UserError(f'something went wrong !! ')
        if self.state == state:
            raise UserError(f'something went wrong !! ')
        next_state = self.get_next_state()
        if self.state == 'refuse' and state == 'confirm' and not is_hr_manager:
            raise UserError('You Are not allowed to do this operation')
        if state not in (next_state, 'refuse'):
            raise UserError('You Are not allowed to do this operation')
        if state == 'validate1' and current_user.id != self.employee_id.leave_manager_id.id and current_employee.id != self.alternative_manager_id.id:
            raise UserError('You Are not allowed to do this operation')
        elif state == 'validate2' and current_employee.id != self.hod_id.id and current_employee.id != self.alternative_hod_id.id:
            raise UserError('You Are not allowed to do this operation')
        elif state == 'validate' and current_employee.id != self.hr_manager_id.id and current_employee.id != self.alternative_hr_manager_id.id:
            raise UserError('You Are not allowed to do this operation')

        return None

    # inherited base method for our logics

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return None
        prevoius = self.filtered(lambda hol: hol.validation_type not in ('manager_hod', 'manger_hod_hr'))
        res = super(HrLeave, prevoius)._check_approval_update(state)

        # is_hr_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_hr_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        for holiday in self:
            val_type = holiday.validation_type
            if not val_type or val_type not in ('manager_hod', 'manger_hod_hr'):
                continue
            if val_type == 'manager_hod' and not is_hr_manager:
                holiday._manager_hod_approval_check(state)
            if val_type == 'manger_hod_hr' and not is_hr_manager:
                holiday._manger_hod_hr_approval_check(state)

        return res

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_reset(self):
        for holiday in self:
            try:
                holiday._check_approval_update('confirm')
            except (AccessError, UserError):
                holiday.can_reset = False
            else:
                holiday.can_reset = True

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):

        for holiday in self:
            if holiday.validation_type not in ('manager_hod', 'manger_hod_hr'):
                continue
            next_state = holiday.get_next_state()
            if not next_state:
                holiday.can_approve = False
                continue
            try:
                holiday._check_approval_update(next_state)
            except (AccessError, UserError):
                holiday.can_approve = False
            else:
                holiday.can_approve = True
        prevoius = self.filtered(lambda hol: hol.validation_type not in ('manager_hod', 'manger_hod_hr'))
        res = super(HrLeave, prevoius)._compute_can_approve()

    def action_approve(self, check_state=True):
        prevoius = self.filtered(lambda hol: hol.validation_type not in ('manager_hod', 'manger_hod_hr'))
        res = super(HrLeave, prevoius).action_validate(check_state)
        new_holidays = self - prevoius
        current_employee = self.env.user.employee_id
        for holiday in new_holidays:
            next_state = holiday.get_next_state()
            holiday._check_approval_update(next_state)
            approval_field = holiday._get_approval_field_based_on_next_stage(next_state)
            holiday.write({'state': next_state, approval_field: current_employee.id})
        if not self.env.context.get('leave_fast_create'):
            new_holidays.activity_update()
        return True and res

        # # if validation_type == 'both': this method is the first approval approval
        # # if validation_type != 'both': this method calls action_validate() below
        #
        # # Do not check the state in case we are redirected from the dashboard
        # if check_state and any(holiday.state != 'confirm' for holiday in self):
        #     raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))
        #
        # current_employee = self.env.user.employee_id
        # self.filtered(lambda hol: hol.validation_type == 'both').write(
        #     {'state': 'validate1', 'first_approver_id': current_employee.id})
        #
        # self.filtered(lambda hol: hol.validation_type != 'both').action_validate(check_state)
        # if not self.env.context.get('leave_fast_create'):
        #     self.activity_update()
        # return True
        #

    def _get_approval_field_based_on_next_stage(self, next_stage):
        self.ensure_one()
        field_dict = {
            'manger_hod_hr': {'validate1': 'first_approver_id', 'validate2': 'second_approver_id',
                              'validate': 'third_approver_id'},
            'manger_hod': {'validate1': 'first_approver_id', 'validate2': 'second_approver_id',
                           'validate': 'second_approver_id'}

        }
        return field_dict.get(self.validation_type, {}).get(next_stage, 'first_approver_id')

    def action_validate(self, check_state=True):
        #  we have two trpe of approval first one are previous and want to work as expected
        prevoius = self.filtered(lambda hol: hol.validation_type not in ('manager_hod', 'manger_hod_hr'))
        res = super(HrLeave, prevoius).action_validate(check_state)
        new_holidays = self - prevoius
        new_leaves = new_holidays._get_leaves_on_public_holiday()
        current_employee = self.env.user.employee_id
        if new_leaves:
            raise ValidationError(
                _('The following employees are not supposed to work during that period:\n %s') % ','.join(
                    new_leaves.mapped('employee_id.name')))
        for holiday in new_holidays:
            next_state = holiday.get_next_state()
            holiday._check_approval_update(next_state)
            approval_field = holiday._get_approval_field_based_on_next_stage(next_state)
            holiday.write({'state': next_state, approval_field: current_employee.id})

        new_holidays._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            new_holidays.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        return res

        # current_employee = self.env.user.employee_id
        # leaves = self._get_leaves_on_public_holiday()
        # if leaves:
        #     raise ValidationError(
        #         _('The following employees are not supposed to work during that period:\n %s') % ','.join(
        #             leaves.mapped('employee_id.name')))
        # if check_state and any(
        #         holiday.state not in ['confirm', 'validate1'] and holiday.validation_type != 'no_validation' for
        #         holiday in self):
        #     raise UserError(_('Time off request must be confirmed in order to approve it.'))
        #
        # self.write({'state': 'validate'})
        #
        # leaves_second_approver = self.env['hr.leave']
        # leaves_first_approver = self.env['hr.leave']
        #
        # for leave in self:
        #     if leave.validation_type == 'both':
        #         leaves_second_approver += leave
        #     else:
        #         leaves_first_approver += leave
        #
        # leaves_second_approver.write({'second_approver_id': current_employee.id})
        # leaves_first_approver.write({'first_approver_id': current_employee.id})
        #
        # self._validate_leave_request()
        # if not self.env.context.get('leave_fast_create'):
        #     self.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        # return True

    def action_refuse(self):
        current_employee = self.env.user.employee_id
        prevoius = self.filtered(lambda hol: hol.validation_type not in ('manager_hod', 'manger_hod_hr'))
        res = super(HrLeave, prevoius).action_refuse()
        new_holidays = self - prevoius
        if any(holiday.state not in ['confirm', 'validate', 'validate1', 'validate2'] for holiday in new_holidays):
            raise UserError(_('Time off request must be confirmed or validated in order to refuse it.'))

        new_holidays._notify_manager()
        validated_holidays = new_holidays.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        validated2_holidays = new_holidays.filtered(lambda hol: hol.state == 'validate2')
        validated2_holidays.write({'state': 'refuse', 'second_approver_id': current_employee.id})
        (new_holidays - validated_holidays - validated2_holidays).write(
            {'state': 'refuse', 'third_approver_id': current_employee.id})
        # Delete the meeting
        new_holidays.mapped('meeting_id').write({'active': False})
        # Post a second message, more verbose than the tracking message
        for holiday in new_holidays:
            if holiday.employee_id.user_id:
                holiday.message_post(
                    body=_('Your %(leave_type)s planned on %(date)s has been refused',
                           leave_type=holiday.holiday_status_id.display_name, date=holiday.date_from),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)

        new_holidays.activity_update()
        return True and res

    is_broken_leave = fields.Boolean(related='holiday_status_id.is_broken_leave')

    @api.constrains('is_broken_leave')
    def broken_leave_validation_check(self):
        for holiday in self:
            if not holiday.is_broken_leave:
                continue
            if holiday.is_broken_leave and holiday.request_date_from != holiday.request_date_to:
                raise ValidationError('Broken leave must be in same day interval')
            broken_leave_count = self.search_count(
                [('employee_id', '=', holiday.employee_id.id), ('company_id', '=', holiday.company_id.id),
                 ('state', 'not in', ['refuse', 'cancel']),
                 ('request_date_from', '=', holiday.request_date_from)('holiday_status_id.is_broken_leave', '=', True)])
            if broken_leave_count > 1:
                raise ValidationError('In One day you can apply only one broken leave')

        # for holiday in self:
        #     try:
        #         if holiday.state == 'confirm' and holiday.validation_type == 'both':
        #             holiday._check_approval_update('validate1')
        #         else:
        #             holiday._check_approval_update('validate')
        #     except (AccessError, UserError):
        #         holiday.can_approve = False
        #     else:
        #         holiday.can_approve = True

    # @api.depends_context('uid')
    # @api.depends('state', 'employee_id')
    # def _compute_can_cancel(self):
    #     now = fields.Datetime.now().date()
    #     for leave in self:
    #         leave.can_cancel = leave.id and leave.employee_id.user_id == self.env.user and leave.state in ['validate',
    #                                                                                                        'validate1'] and leave.date_from and leave.date_from.date() >= now
