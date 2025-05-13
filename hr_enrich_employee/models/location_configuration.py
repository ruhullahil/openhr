from odoo import fields, models, api


class LocationConfiguration(models.Model):
    _name = 'location.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Location Configuration'

    name = fields.Char()
    company_id = fields.Many2one('res.company',default= lambda self : self.env.company,tracking=True)
    parent_location_type_id = fields.Many2one('location.type.configuration',compute='_compute_parent_location_type_id',store=True,tracking=True)
    location_type_id = fields.Many2one('location.type.configuration',tracking=True)
    parent_id = fields.Many2one('location.configuration',domain="[('company_id','=',company_id),('location_type_id','=?',parent_location_type_id)]",tracking=True)
    child_location_type_id = fields.Many2one('location.type.configuration', compute='_compute_child_location_type_id',
                                              store=True,tracking=True)
    child_ids = fields.One2many('location.configuration','parent_id')
    child_count = fields.Integer(compute='_compute_child_count')


    @api.depends('location_type_id')
    def _compute_parent_location_type_id(self):
        for l_config in self:
            l_config.parent_location_type_id = None
            if l_config.location_type_id:
                l_config.parent_location_type_id = l_config.location_type_id.get_previous_type() or None

    @api.depends('location_type_id')
    def _compute_child_location_type_id(self):
        for l_config in self:
            l_config.child_location_type_id = None
            if l_config.location_type_id:
                l_config.child_location_type_id = l_config.location_type_id.get_next_type() or None

    @api.depends('child_ids')
    def _compute_child_count(self):
        for rec in self:

            rec.child_count = len(rec.child_ids) or 0

