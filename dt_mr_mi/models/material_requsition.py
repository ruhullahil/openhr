from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MaterialRequisition(models.Model):
    _name = 'material.requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Material Requisition'

    name = fields.Char()
    date = fields.Date(tracking=True)
    require_date = fields.Date(tracking=True)
    issue_date = fields.Date(tracking=True)
    responsible_id = fields.Many2one('res.users', tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    reason = fields.Html()
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='draft')
    requisition_line_ids = fields.One2many('material.requisition.line', 'requisition_id')

    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('material.requisition.seq') or _('New')
        return super(MaterialRequisition, self).create(values)

    def btn_approved(self):
        approval_dict = {
            'draft': 'submit',
            'submit': 'approved'
        }
        for mr in self:
            next_stage = approval_dict.get(mr.state, None)
            if not next_stage:
                raise ValidationError('Something went wrong!!')
            mr.state = next_stage

    def btn_rejected(self):
        for mr in self:
            if mr.state not in ('submit','draft'):
                raise ValidationError('Not possible do this operation')
            mr.state = 'rejected'


class MaterialRequisitionLine(models.Model):
    _name = 'material.requisition.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Material Requisition Line'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product')
    description = fields.Char()
    uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id', store=True)
    uom_id = fields.Many2one('uom.uom', compute='_compute_uom_id', store=True, readonly=False,
                             domain="[('category_id','=',uom_category_id)]")
    quantity = fields.Float(digits='Product Unit of Measure')
    requisition_id = fields.Many2one('material.requisition')
    parent_state = fields.Selection(related='requisition_id.state')
    available_qty = fields.Float(related='product_id.qty_available')

    @api.depends('product_id', 'uom_category_id')
    def _compute_uom_id(self):
        for line in self:
            if not line.uom_id:
                line.uom_id = line.product_id.uom_id

    @api.onchange('product_id')
    def adjust_line_info_according_to_product(self):
        if not self.product_id:
            return
        if self.product_id.uom_id.id != self.uom_id.id:
            self.uom_id = self.product_id.uom_id

    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_id.id,
            'active_model': 'product.product',
        }
        return action
