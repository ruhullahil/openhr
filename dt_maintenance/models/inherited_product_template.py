from odoo import fields, models, api
from odoo.exceptions import ValidationError


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    is_maintenance_product = fields.Boolean('Maintenance')
    is_maintenance_parts = fields.Boolean('Maintenance Parts')
    equipment_category_id = fields.Many2one('maintenance.equipment.category')

    @api.constrains('is_maintenance_product')
    def _check_maintenance_product_constrains(self):
        for product in self:
            if not product.is_maintenance_product:
                continue
            if product.type != 'consu' or not product.is_storable or product.tracking != 'serial' or product.sale_ok:
                raise ValidationError('Product configuration is not correct !! please check product configuration .')


    @api.onchange('is_maintenance_product')
    def onchange_set_config_for_maintenance(self):
        if not self.is_maintenance_product:
            return
        # self.is_maintenance_parts = False
        self.type = 'consu'
        self.is_storable = True
        self.tracking = 'serial'
        self.sale_ok = False

    # @api.onchange('is_maintenance_parts')
    # def onchange_set_config_for_maintenance_part(self):
    #     if not self.is_maintenance_parts:
    #         return
    #     self.is_maintenance_product = False

