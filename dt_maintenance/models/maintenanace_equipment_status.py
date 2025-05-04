from odoo import fields, models, api


class MaintenanceEquipmentStatus(models.Model):
    _name = 'maintenance.equipment.state'
    _description = 'Maintenance Equipment Status'
    _order = 'sequence,id'

    name = fields.Char()
    description = fields.Text()
    sequence = fields.Integer()
    template_id = fields.Many2one('mail.template')
    is_running = fields.Boolean('Running')
    is_scraped = fields.Boolean('Scraped')
    is_maintenance = fields.Boolean('Maintenance')
