from odoo import fields, models, api,_


class SparePartsUsedLine(models.Model):
    _name = 'spare.parts.used.line'
    _description = 'Description'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product')
    uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id', store=True)
    uom_id = fields.Many2one('uom.uom', compute='_compute_uom_id', store=True, readonly=False,
                             domain="[('category_id','=',uom_category_id)]")
    quantity = fields.Float(digits='Product Unit of Measure')
    location_id = fields.Many2one('stock.location')
    location_dest_id = fields.Many2one('stock.location')
    move_ids = fields.One2many('stock.move','spare_line_id')
    m_request_id = fields.Many2one('maintenance.request')
    company_id = fields.Many2one(related='m_request_id.company_id')
    lot_id = fields.Many2one('stock.lot')

    def _get_inventory_move_values(self):
        """ Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param package_id: `stock.quant.package`
        :param package_dest_id: `stock.quant.package`
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
        self.ensure_one()

        return {
            'name': f'spare parts move for {self.m_request_id.display_name}',
            'product_id': self.product_id.id,
            'spare_line_id':self.id,
            'product_uom': self.uom_id.id,
            'product_uom_qty': self.quantity,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'restrict_partner_id':  self.m_request_id.user_id.partner_id.id,
            'is_inventory': False,
            'picked': True,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.uom_id.id,
                'quantity': self.quantity,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': self.lot_id.id,
                'package_id': False,
                'result_package_id': False,
                'owner_id': self.m_request_id.user_id.partner_id.id,
            })]
        }
    def make_and_done_move(self):
        self.ensure_one()
        move_data = self._get_inventory_move_values()
        moves = self.env['stock.move'].create(move_data)
        moves._action_done()




