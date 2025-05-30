from datetime import datetime, time
from math import ceil

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import pytz


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    max_consecutive_period = fields.Integer(related='holiday_status_id.max_consecutive_period',store=True)
    info_message = fields.Html(compute='_compute_info_message')
    fiscal_year = fields.Many2one('account.fiscal.year',compute='_compute_fiscal_year',store=True)

    @api.depends('employee_id', 'holiday_status_id', 'date_from', 'date_to')
    def _compute_fiscal_year(self):
        AccountFiscalYear = self.env["account.fiscal.year"]
        for leave in self:
            fiscalyear = AccountFiscalYear._get_fiscal_year(
                leave.company_id, leave.date_from, leave.date_to
            )
            leave.fiscal_year = fiscalyear or None




    @api.depends('employee_id','holiday_status_id','date_from','date_to')
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
            hours = ceil(duration.total_seconds()/3600)
            result[leave.id] = (days, hours)
        if not result:
            return super(HrLeave,self)._get_durations(check_leave_type,resource_calendar)
        return result

    def _get_consecutive_number_of_time(self):
        self.ensure_one()
        # print(f'date fom : {self.date_from}')
        # # time_zone = self.employee_id.tz
        # ut_time = pytz.timezone(pytz.UTC)
        contract_start = self.date_from.astimezone(pytz.UTC)
        # check privious day leave
        last_work_day = self.employee_id._get_previous_working_daya(contract_start)
        leave = self.employee_id.get_leave_id(last_work_day)
        if leave and leave.holiday_status_id.id == self.holiday_status_id.id and self.holiday_status_id.is_auto_merge:
            duration  = self.date_to - leave.date_from
            con_time = ceil(duration.total_seconds() / (24 * 3600)) if self.leave_type_request_unit != 'hour' else ceil(duration.total_seconds()/3600)
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





    def chek_durational_validation(self):
        self._get_consecutive_number_of_time()







    @api.constrains('max_consecutive_period','leave_type_request_unit','state')
    def _check_max_consecutive_period_validation(self):
        for rec in self:
            if rec.state in ('refuse','cancel'):
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

#             Add cretical validation



