from email.policy import default

from odoo import fields, models, api,_
from odoo.exceptions import ValidationError


class CompensatoryDay(models.Model):
    _name = 'hr.compensatory.day'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Compensatory Day'
    _rec_name = 'date'

    name = fields.Char()
    company_id = fields.Many2one('res.company',default=lambda self : self.env.company.id)
    is_admin = fields.Boolean(compute='_compute_is_admin')
    employee_id = fields.Many2one('hr.employee',tracking=True,default= lambda self : self.env.user.employee_id.id)
    date = fields.Date(tracking=True)
    from_time = fields.Float(tracking=True)
    to_time = fields.Float(tracking=True)
    duration = fields.Float(tracking=True,store=True,compute='_compute_duration')
    type = fields.Selection([('manual','Manual')],default='manual')
    state = fields.Selection([('draft','Draft'),('approval','Approval'),('approved','Approved'),('rejected','Rejected'),('cancel','Cancel')],default='draft',tracking=True)
    is_adjusted = fields.Boolean(default=False)

    @api.depends('company_id')
    def _compute_is_admin(self):
        for rec in self:
            rec.is_admin = self.env.user.has_group("hr.group_hr_user")


    @api.depends('from_time','to_time')
    def _compute_duration(self):
        for rec in self:
            rec.duration = rec.to_time - rec.from_time

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.compensatory.seq') or _("New")
        return super().create(vals_list)

    def btn_submit(self):
        for rec in self:
            if rec.state not in ('draft'):
                continue
            rec.state = 'approval'

    def btn_approve(self):
        for rec in self:
            if rec.state not in ('approval'):
                continue
            rec.state = 'approved'

    def btn_reject(self):
        for rec in self:
            if rec.state not in ('approval'):
                continue
            rec.state = 'rejected'

    def btn_cancel(self):
        for rec in self:
            if rec.state not in ('draft'):
                continue
            rec.state = 'cancel'

    @api.constrains('from_time','to_time')
    def check_time_related_validation(self):
        for rec in self:
            if rec.from_time and rec.from_time > 24.0:
                raise ValidationError('Date field can not be greater then 24')
            if rec.to_time and rec.to_time > 24.0:
                raise ValidationError('Date field can not be greater then 24')
            if rec.from_time and rec.to_time and rec.from_time > rec.to_time:
                raise ValidationError('start time can not greater then end time')


