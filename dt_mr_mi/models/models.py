from odoo import api, fields, models

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'


    internal_picking_type = fields.Selection([('out','Out'),('int_mi','Maintenance Issue'),('mi','Issue'),('in','IN'),('int','Internal')])

    @api.onchange('internal_picking_type')
    def set_code_base_on_type(self):
        if not self.internal_picking_type:
            return
        picking_code_dict = {
            'out': 'outgoing',
            'int_mi': 'internal',
            'mi': 'outgoing',
            'in': 'incoming',
            'int': 'internal',
        }
        self.code = picking_code_dict.get(self.internal_picking_type)


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    responsible_id = fields.Many2one('res.users')

    def _get_location_base_on_responsible(self):
        self.ensure_one()
        return self.env['stock.location'].sudo().search([('company_id','=',self.company_id.id),('owner_id','=',self.responsible_id)],limit=1)

    @api.depends('picking_type_id', 'partner_id','responsible_id')
    def _compute_location_id(self):
        res = super(InheritStockPicking,self)._compute_location_id()
        for picking in self:
            if not picking.responsible_id:
                continue
            location = picking._get_location_base_on_responsible()
            if not location:
                continue
            picking.location_dest_id = location.id
        return res







