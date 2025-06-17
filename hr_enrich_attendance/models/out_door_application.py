from odoo import fields, models, api


class OutdoorApplication(models.Model):
    _name = 'hr.attendance.outdoor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Outdoor Attendance'

    name = fields.Char()
    company_id = fields.Many2one('res.company',default=lambda self : self.env.company.id,tracking=True)
    default_employee_ids = fields.Many2many('hr.employee',compute='_compute_default_employee_ids')
    employee_id = fields.Many2one('hr.employee',domain="[('id','in',default_employee_ids)]",tracking=True)
    outdoor_date = fields.Date(tracking=True)
    from_time = fields.Float()
    to_time = fields.Float()


    # def _get_access_able_employee(self,employee):
    #     need_to_check_employees = employee.ids
    #     already_travers_employee_set = set()
    #
    #     while need_to_check_employees:
    #         active_employee_id = need_to_check_employees.pop()
    #         if active_employee_id not in already_travers_employee_set:
    #             already_travers_employee_set.add(active_employee_id)
    #             active_employee = self.env['']






    @api.depends('company_id')
    def _compute_default_employee_ids(self):
        for outdoor in self:
            current_employee = self.env.user.employee_id
            is_hr_manager = self.env.user.has_group('hr_attendance.group_hr_attendance_officer')
            domain = []
            if outdoor and outdoor.company_id:
                domain += [('company_id','=',outdoor.company_id.id)]
            if not is_hr_manager and current_employee:
                domain +=['|',('id','child_of',current_employee.id),('id','=',current_employee.id)]
            outdoor.default_employee_ids = self.env['hr.employee'].sudo().search(domain).ids
