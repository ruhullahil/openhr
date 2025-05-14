from odoo import fields, models, api


class HrJobRank(models.Model):
    _name = 'hr.job.rank'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Job Rank'
    _order = 'sequence, id'

    name = fields.Char(tracking=True)
    description = fields.Text()
    sequence = fields.Integer(tracking=True)
    company_id = fields.Many2one('res.company',default= lambda self:self.env.company,tracking=True)

