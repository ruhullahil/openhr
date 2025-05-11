from odoo import fields, models, api


class HrJobFacilityConfig(models.Model):
    _name = 'hr.job.facility.config'
    _description = 'Hr Job Facility Config'

    name = fields.Char()
    description = fields.Text()
