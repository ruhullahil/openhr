from odoo import fields, models, api


class HrDistrict(models.Model):
    _name = 'res.country.district'
    _description = 'District'

    name = fields.Char()
    state_id = fields.Many2one('res.country.state')
