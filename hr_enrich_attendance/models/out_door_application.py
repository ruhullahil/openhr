from odoo import fields, models, api


class OutdoorApplication(models.Model):
    _name = 'ProjectName.TableName'
    _description = 'Description'

    name = fields.Char()
