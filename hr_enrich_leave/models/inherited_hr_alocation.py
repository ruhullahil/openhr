from odoo import fields, models, api


class HrAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    config_id = fields.Many2one('hr.default.leave.configuration')
    config_line_id = fields.Many2one('hr.default.leave.configuration.line')
    is_carry_over_allocation = fields.Boolean(related='config_line_id.is_able_carry_over')






