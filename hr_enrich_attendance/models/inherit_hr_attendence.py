
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, exceptions, _



class HrAttendance(models.Model):
    _inherit = 'hr.attendance'


    attendance_status = fields.Char(compute='_compute_attendance_status')
    leave_ids = fields.Many2many('hr.leave')








    def _cron_absence_detection(self):
        """
        Objective is to create technical attendances on absence days to have negative overtime created for that day
        """
        yesterday = datetime.today().replace(hour=0, minute=0, second=0) - relativedelta(days=1)
        companies = self.env['res.company'].search([('absence_management', '=', True)])
        if not companies:
            return

        checked_in_employees = self.env['hr.attendance.overtime'].search([('date', '=', yesterday),
                                                                          ('adjustment', '=', False)]).employee_id

        technical_attendances_vals = []
        absent_employees = self.env['hr.employee'].search([('id', 'not in', checked_in_employees.ids),
                                                           ('company_id', 'in', companies.ids)])
        for emp in absent_employees:
            local_day_start = pytz.utc.localize(yesterday).astimezone(pytz.timezone(emp._get_tz()))
            technical_attendances_vals.append({
                'check_in': local_day_start.strftime('%Y-%m-%d %H:%M:%S'),
                'check_out': (local_day_start + relativedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'in_mode': 'technical',
                'out_mode': 'technical',
                'employee_id': emp.id
            })

        technical_attendances = self.env['hr.attendance'].create(technical_attendances_vals)
        # to_unlink = technical_attendances.filtered(lambda a: a.overtime_hours == 0)

        body = _('This attendance was automatically created to cover an unjustified absence on that day.')
        for technical_attendance in technical_attendances:
            technical_attendance.message_post(body=body)

        # to_unlink.unlink()



