from odoo import fields, models, api


class FrozenAllocationInfo(models.Model):
    _name = 'frozen.allocation.info'
    _description = 'Frozen Allocation Info'

    allocation_id = fields.Many2one('hr.leave.allocation',tracking=True)
    leave_type_id = fields.Many2one('hr.leave.type',compute='_compute_leave_type_id',store=True,readonly=False)
    employee_id = fields.Many2one('hr.employee',related='allocation_id.employee_id',tracking=True)
    start_date = fields.Date(related='allocation_id.date_from',tracking=True)
    end_date = fields.Date()
    frozen_leave = fields.Float(tracking=True)
    carry_able_leave = fields.Float(tracking=True)
    # previous carry related info
    previous_carry = fields.Float(tracking=True)
    previous_allocation_id = fields.Many2one('hr.leave.allocation',tracking=True)
    is_initial = fields.Boolean()

    @api.depends('allocation_id')
    def _compute_leave_type_id(self):
        for fai in self:
            fai.leave_type_id = fai.allocation_id.holiday_status_id.id


