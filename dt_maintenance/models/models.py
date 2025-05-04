from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritStockLocation(models.Model):
    _inherit = 'stock.location'

    usage = fields.Selection(selection_add=[('equipment', 'Equipment')],ondelete={'equipment': 'cascade'})
    owner_id = fields.Many2one('res.users',tracking=True)

    @api.constrains('usage')
    def _equipment_location_constrain_check(self):
        for location in self:
            if location.usage == 'equipment' and location.location_id and location.location_id.usage != 'equipment':
                raise ValidationError('Equipment location parent need to be equipment location as well !!')

    def set_owner_id(self,owner):
        self.ensure_one()
        self.owner_id = owner.id

    def remove_owner_id(self):
        self.ensure_one()
        self.owner_id = None



class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    is_retailer = fields.Boolean('Retailer')
    retailer_location = fields.Many2one('stock.location',domain="[('child_ids','=',False),('usage','=','equipment')]")








