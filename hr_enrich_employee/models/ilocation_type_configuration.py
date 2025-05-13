from odoo import fields, models, api


class LocationTypeConfiguration(models.Model):
    _name = 'location.type.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Location Type Configuration'
    _order = 'sequence , id'

    name = fields.Char()
    description = fields.Text()
    sequence = fields.Integer()
    company_id = fields.Many2one('res.company',default= lambda self: self.env.company)

    def get_previous_type(self):
        self.ensure_one()
        configurations = self.search([('company_id','=',self.company_id.id)])
        for index,config in enumerate(configurations):
            if index > 0 and config.id == self.id:
                return configurations[index-1]
        return self.env[self._name]


    def get_next_type(self):
        self.ensure_one()
        configurations = self.search([('company_id', '=', self.company_id.id)])
        for index, config in enumerate(configurations):
            if index < (len(configurations)-1) and config.id == self.id:
                return configurations[index + 1]
        return self.env[self._name]


