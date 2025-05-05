from odoo import fields, models, api


class MaterialRequisition(models.Model):
    _name = 'material.requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Material Requisition'

    name = fields.Char()
    date = fields.Date(tracking=True)
    require_date = fields.Date(tracking=True)
    issue_date = fields.Date(tracking=True)
    responsible_id = fields.Many2one('res.users',tracking=True)
    company_id = fields.Many2one('res.company')
    reason = fields.Html()



class MaterialRequisitionLine(models.Model):
    _name = 'material.requisition.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Material Requisition Line'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product')
    description = fields.Char()
    uom_category_id = fields.Many2one('uom.category',related='product_id.uom_id.category_id',store=True)
    uom_id = fields.Many2one('uom.uom',compute='_compute_uom_id',store=True,readonly=False,domain="[('category_id','=',uom_category_id)]")
    quantity = fields.Float(digits='Product Unit of Measure')
    requisition_id = fields.Many2one('material.requisition')


