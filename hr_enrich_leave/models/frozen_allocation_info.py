from odoo import fields, models, api


class FrozenAllocationInfo(models.Model):
    _name = 'frozen.allocation.info'
    _description = 'Frozen Allocation Info'

    allocation_id = fields.Many2one('hr.leave.allocation')
    employee_id = fields.Many2one('hr.employee',related='allocation_id.employee_id')
    start_date = fields.Date()
    end_date = fields.Date()
    frozen_leave = fields.Float()
    carry_able_leave = fields.Float()
    # previous carry related info
    previous_carry = fields.Float()
    previous_allocation_id = fields.Many2one('hr.leave.allocation')

