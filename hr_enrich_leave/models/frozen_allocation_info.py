from datetime import date, timedelta

from odoo import fields, models, api
from odoo.tools.safe_eval import datetime, time


class FrozenAllocationInfo(models.Model):
    _name = 'frozen.allocation.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Frozen Allocation Info'

    allocation_id = fields.Many2one('hr.leave.allocation',tracking=True)
    leave_type_id = fields.Many2one('hr.leave.type',compute='_compute_leave_type_id',store=True,readonly=False,tracking=True)
    employee_id = fields.Many2one('hr.employee',compute='_compute_employee_id',tracking=True,tore=True,readonly=False)
    start_date = fields.Date(compute='_compute_start_end_date',tracking=True,store=True,readonly=False)
    employee_company_id = fields.Many2one(related='employee_id.company_id', readonly=True, store=True)
    end_date = fields.Date(compute='_compute_start_end_date',required=True,tracking=True,store=True,readonly=False)
    frozen_leave = fields.Float(tracking=True,required=1)
    carry_able_leave = fields.Float(tracking=True)
    # previous carry related info
    # previous_carry = fields.Float(tracking=True)
    # previous_allocation_id = fields.Many2one('hr.leave.allocation',tracking=True)
    # is_initial = fields.Boolean()

    # def _generate_local_dict(self, employee):
    #     self.ensure_one()
    #     local_dict = {
    #         'env': self.env,
    #         'line': self,
    #         'employee': employee,
    #         'date': date,
    #         'datetime': datetime,
    #         'timedelta': timedelta,
    #         'time': time,
    #
    #     }
    #     return local_dict

    # @api.depends('employee_id','allocation_id','leave_type_id')
    # def _compute_carry_able_leave(self):
    #     for rec in self:
    #         rec.carry_able_leave = rec.frozen_leave
    #         if rec.allocation_id and rec.allocation_id.config_line_id and not rec.allocation_id.config_line_id.is_able_carry_over:
    #             rec.carry_able_leave = 0
    #         if rec.allocation_id and rec.allocation_id.config_line_id and rec.allocation_id.config_line_id.is_able_carry_over:




    @api.depends('allocation_id')
    def _compute_leave_type_id(self):
        for fai in self:
            fai.leave_type_id = fai.allocation_id.holiday_status_id.id

    @api.depends('allocation_id')
    def _compute_start_end_date(self):
        for fai in self:
            fai.start_date = fai.allocation_id.date_from
            fai.end_date = fai.allocation_id.date_to

    @api.depends('allocation_id')
    def _compute_employee_id(self):
        for fai in self:
            fai.start_date = fai.allocation_id.employee_id




