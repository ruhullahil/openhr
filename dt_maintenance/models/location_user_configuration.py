from odoo import fields, models, api
from odoo.exceptions import ValidationError


class LocationUserConfiguration(models.Model):
    _name = 'Location.user.configuration'
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



    def btn_assigned(self):
        pass





