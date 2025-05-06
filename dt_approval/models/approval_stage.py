from odoo import fields, models, api


class ApprovalStages(models.Model):
    _name = 'approval.stages'
    _description = 'Approval Stages'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model')
    model_name = fields.Char(related='model_id.model',store=True)
    description = fields.Html()

class ApprovalStageLine(models.Model):
    _name = 'approval.stages.line'
    _description = 'Approval Stage Line'

    name = fields.Char()
    sequence = fields.Integer()
    approval_stage_id = fields.Many2one('approval.stages')
    model_id = fields.Many2one('ir.model')
    model_name = fields.Char(related='model_id.model', store=True)
    allowed_groups = fields.Many2many('res.groups')
    default_user_ids = fields.Many2many('res.users',compute='_compute_allowed_users')
    user_ids = fields.Many2many('res.users',domain="[('id','in',default_user_ids)]")
    is_readonly = fields.Boolean()
    is_done = fields.Boolean()
    is_cancel = fields.Boolean()



