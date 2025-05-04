from odoo import fields, models, api


class LocationStockQuantity(models.TransientModel):
    _name = 'location.stock.quantity'
    _description = 'Location Stock Quantity'
    _rec_name = 'location_id'

    location_id = fields.Many2one('stock.location')
    config_id = fields.Many2one('Location.user.configuration')
    message = fields.Html()
    line_ids = fields.One2many('location.stock.quantity.line', 'lsq_id',
                               compute='_compute_stock_quantity_location_wise', store=True)

    @api.depends('location_id')
    def _compute_stock_quantity_location_wise(self):
        for rec in self:
            groups = self.env['stock.quant']._read_group(
                [('location_id.usage', 'in', ('internal', 'transit')),
                 ('location_id', 'in', rec.location_id.ids)],
                ['product_id'], ['quantity:sum'])
            groups = dict(groups)
            datas = [(5, 0, 0)]
            for group, quantity in groups.items():
                datas.append(
                    (0, 0,
                     {
                         'product_id': group,
                         'location_id': rec.location_id.id,
                         'quantity': quantity
                     }
                     )
                )
            rec.line_ids = datas
    def btn_set_done(self):
        self.btn_assigned(no_popup=True)


class LocationStockQuantityLine(models.TransientModel):
    _name = 'location.stock.quantity.line'
    _description = 'Location Stock Quantity Line'
    _rec_name = 'location_id'

    product_id = fields.Many2one('product.product')
    location_id = fields.Many2one('stock.location')
    lsq_id = fields.Many2one('location.stock.quantity')
    quantity = fields.Float()
