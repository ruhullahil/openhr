from odoo import fields, models, api,_
from odoo.exceptions import ValidationError


class LocationUserConfiguration(models.Model):
    _name = 'location.user.configuration'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Location User Configuration'

    name = fields.Char()
    user_id = fields.Many2one('res.users',tracking=True,required=True)
    assign_location = fields.Many2one('stock.location',tracking=True,required=True)
    state = fields.Selection([('draft','Draft'),('assigned','Assigned'),('removed','Removed'),('cancel','Cancel')],default='draft',tracking=True)

    @api.constrains('user_id','state')
    def _check_constrains(self):
        for rec in self:
            already_assigned = self.sudo().search_count([('id','not in', rec.ids),('state','in',['draft','assigned']),('user_id','=',rec.user_id.id)])
            if already_assigned > 0:
                raise ValidationError('You are not allowed to do this operation !!')





    def btn_assigned(self,no_popup = False):
        self.ensure_one()
        if not no_popup and not self.assign_location.is_empty:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Products'),
                'res_model': 'location.stock.quantity',
                'target': 'new',
                'context': {
                'default_config_id': self.id,
                'default_location_id': self.assign_location.id,
                'default_message': """<p class="text-danger">Your Assign Location is not empty !! Are you sure to assign this location.. </p>"""
            },
            }
        self.assign_location.set_owner_id(self.assign_location)
        self.state = 'assigned'

    def btn_remove(self):
        self.ensure_one()
        if  not self.assign_location.is_empty:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Products'),
                'res_model': 'location.stock.quantity',
                'target': 'new',
                'context': {
                    'default_config_id': self.id,
                    'default_location_id': self.assign_location.id,
                    'default_message': """<p class="text-danger">Your Remove  Location is not empty !! Are you sure to Remove user from this location.. </p>"""
                },
            }
        self.assign_location.remove_owner_id()
        self.state = 'removed'






