from odoo import fields, models, api

MAX_NUMBER = 999999.9


class HrAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    config_id = fields.Many2one('hr.default.leave.configuration')
    config_line_id = fields.Many2one('hr.default.leave.configuration.line')
    is_carry_over_allocation = fields.Boolean(related='config_line_id.is_able_carry_over')

    def _get_previous_frozen_data(self):
        self.ensure_one()
        data = {}
        FrozenInfo = self.env['frozen.allocation.info']
        if not self.is_carry_over_allocation or not self.config_line_id or not self.config_line_id.is_auto_renew:
            return data
        frozen_infos = FrozenInfo.sudo().search(
            [('employee_id', '=', self.employee_id.id), ('leave_type_id', 'in', self.holiday_status_id.ids),
             ('employee_company_id', '=', self.employee_company_id.id), ('end_date', '<=', self.date_from)],
            order='id desc')
        total_frozen = 0
        max_carry_over = self.config_line_id.max_carry_over if self.config_line_id and self.config_line_id.max_carry_over > 0.0001 else MAX_NUMBER
        max_carry_over_year = self.config_line_id.max_carry_over_year if self.config_line_id and self.config_line_id.max_carry_over_year > 0.0001 else MAX_NUMBER
        is_able_use_carry_over = self.config_line_id.is_able_use_carry_over if self.config_line_id and self.config_line_id.is_able_use_carry_over else False
        max_carry_over_use = self.config_line_id.max_carry_over_use if is_able_use_carry_over else 0.0
        for frozen in frozen_infos:
            total_frozen += min(frozen.carry_able_leave, max_carry_over_year)
        data['frozen_count'] = min(max_carry_over, total_frozen)
        data['use_able_frozen'] = min(max_carry_over_use, total_frozen)

        return data

    def get_previous_allocation(self):
        self.ensure_one()
        domain = [('state', '=', 'validate'), ('date_to', '<=', self.date_from),
                  ('employee_id', '=', self.employee_id.id), ('holiday_status_id', '=', self.holiday_status_id.id)]
        last_allocation = self.sudo().search(domain, order=' date_to  desc', limit=1)
        return last_allocation
