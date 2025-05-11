from odoo import fields, models, api


class HrJobRank(models.Model):
    _name = 'hr.job.rank'
    _description = 'HR Job Rank'

    name = fields.Char()
    description = fields.Text()
    sequence = fields.Integer()

