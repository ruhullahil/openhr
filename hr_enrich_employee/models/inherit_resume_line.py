from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'hr.resume.line'


    date_start = fields.Date(required=False)
    display_type = fields.Selection(selection_add=[('education', 'Education')])
    passing = fields.Char()
    expire_on = fields.Date()
