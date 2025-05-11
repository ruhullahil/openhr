from odoo import fields, models, api


class InheritMaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    responsible_location = fields.Many2one('stock.location',compute='_compute_responsible_location',store=True,readonly=False)
    spare_parts_use_ids = fields.One2many('spare.parts.used.line','m_request_id')

    def _get_location_base_on_responsible(self):
        self.ensure_one()
        return self.env['stock.location'].sudo().search(
            [('company_id', '=', self.company_id.id), ('owner_id', '=', self.user_id.id)], limit=1)

    @api.depends('user_id')
    def _compute_responsible_location(self):
        for req in self:
            req.responsible_location = req._get_location_base_on_responsible() or None

    def reflect_in_stock_used(self):
        spare_parts_ids = self.mapped('spare_parts_use_ids')
        for sare_part in spare_parts_ids:
            sare_part.make_and_done_move()
        return




