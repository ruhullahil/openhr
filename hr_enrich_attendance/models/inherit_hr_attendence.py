from odoo import fields, models, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'


    attendance_status = fields.Char(compute='_compute_attendance_status')
    leave_ids = fields.Many2many('hr.leave')



