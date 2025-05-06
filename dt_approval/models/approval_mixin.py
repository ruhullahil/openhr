from odoo import fields, models, api


class ModelName(models.AbstractModel):
    _name = 'approval.mixin'
    _description = 'Description'

    state = fields.Selection(
        [('draft', 'draft'), ('approval', 'Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')])



