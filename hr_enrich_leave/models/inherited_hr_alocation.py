from odoo import fields, models, api


class HrAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    config_line_id = fields.Many2one('hr.default.leave.configuration')






