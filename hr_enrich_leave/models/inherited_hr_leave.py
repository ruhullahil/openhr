from datetime import datetime, time
from math import ceil

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import pytz


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    max_consecutive_period = fields.Integer(related='holiday_status_id.max_consecutive_period',store=True)
    info_message = fields.Html(compute='_compute_info_message')
    fiscal_year = fields.Many2one('account.fiscal.year',compute='_compute_fiscal_year',store=True)

    # support document mandatory fields and functions

    is_document_required = fields.Boolean(related='holiday_status_id.is_document_required')

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


    @api.constrains('is_compensatory_leave','compensatory_id','state')
    def check_compensatory_related_validation(self):
        for rec in self:
            today = fields.Date.context_today(self)
            if not rec.is_compensatory_leave:
                continue
            if rec.leave_type_request_unit == 'hour':
                raise ValidationError('Compensatory leave unit would be days !! please contact with Admin')
            if rec.number_of_days > 1.0001 :
                raise ValidationError('Compensatory day must be 1 day')
            if rec.compensatory_id and rec.compensatory_allowed_with_in_days > 0.0001:
                compensatory_date =  rec.compensatory_id.date
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
        # check previous day leave
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



#     -------------------------------------------------------------------------------------------------------------------------------------
#                           Extra validation
# -----------------------------------------------------------------------------------------------------------------------------------------

    is_need_extra_validation = fields.Boolean(related='holiday_status_id.is_need_extra_validation')

    def _check_max_apply_in_year(self):
        self.ensure_one()
        max_apply_year = self.holiday_status_id.max_apply_in_year  or 0.0
        if not (max_apply_year > 0.001):
            return
        current_date = fields.Date.context_today(self)
        start_date = current_date.replace(day=1,month=1)
        end_date = current_date.replace(day=31,month=12)
        domain = [('company_id','=',self.company_id.id),('employee_id','=',self.employee_id.id),('state','not in',('cancel','refuse'))]
        date_related_domain = [('date_to','>=',start_date),('date_to','<=',end_date)]
        domain += date_related_domain
        appy_count = self.sudo().search_count(domain)
        if appy_count > max_apply_year:
            raise ValidationError(f'You can not appy {self.holiday_status_id.display_name} !! Your limit is over for this year.')

    def _check_max_in_life_time(self):
        self.ensure_one()
        max_life_time = self.holiday_status_id.max_apply_in_life_time or 0.0
        if not (max_life_time > 0.001):
            return
        domain = [('company_id', '=', self.company_id.id), ('employee_id', '=', self.employee_id.id),
                  ('state', 'not in', ('cancel', 'refuse'))]
        appy_count = self.sudo().search_count(domain)
        if appy_count > max_life_time:
            raise ValidationError(
                f'You can not appy {self.holiday_status_id.display_name} !! Your limit is over for this leave type.')






    def check_extra_validation(self):
        for rec in self:
            if not rec.is_need_extra_validation:
                continue
            # yearly validation check
            rec._check_max_apply_in_year()
            # life time max check
            rec._check_max_in_life_time()






