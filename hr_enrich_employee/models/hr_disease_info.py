from odoo import fields, models, api


class HrDiseaseInfo(models.Model):
    _name = 'hr.disease.info'
    _description = 'HrDiseaseInfo'
    _rec_name = 'chronic_disease'

    chronic_disease = fields.Many2one('hr.chronic.disease')
    details = fields.Text()
    employee_id = fields.Many2one('hr.employee')
    start_date = fields.Date()

