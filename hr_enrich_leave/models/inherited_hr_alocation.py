from odoo import fields, models, api


class HrAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    config_id = fields.Many2one('hr.default.leave.configuration')
    config_line_id = fields.Many2one('hr.default.leave.configuration.line')
    is_carry_over_allocation = fields.Boolean(related='config_line_id.is_able_carry_over')

    def _get_previous_frozen(self):
        self.ensure_one()
        FrozenInfo = self.env['frozen.allocation.info']
        if not self.is_carry_over_allocation or not self.config_line_id or self.config_line_id.is_auto_renew:
            return FrozenInfo
        frozen_infos = FrozenInfo.sudo().search(
            [('employee_id', '=', self.employee_id.id), ('leave_type_id', 'in', self.holiday_status_id.ids),
             ('employee_company_id', '=', self.employee_company_id.id)],order='')
