from odoo import fields, models, api


class AlterSequenceModel(models.Model):
    _name = 'hr.alter.leave.sequence'
    _description = 'AlterSequenceModel'
    _rec_name = 'leave_type'
    _order = 'sequence , id'

    leave_type = fields.Many2one('hr.leave.type')
    sequence = fields.Integer()
    applicability = fields.Selection([
        ('appy_full_or_nothing','If full period applicability then only apply.'),
        ('appy_apply_only_current_if_applicable','If not satisfied the full leave duration then appy that satisfied.'),
        ('apply_full_if_possible_or_current','If possible apply full in same leave type or apply previous as it is the other with current.'),
    ],defailt='apply_full_if_possible_or_current')
    parent_leave_type = fields.Many2one('hr.leave.type')




