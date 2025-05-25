from odoo import fields, models, api, Command


class InheritHrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    rounding_type = fields.Selection([('floor','Floor'),('ceil','Ceiling')],delault='ceil')
    max_consecutive_period = fields.Integer()
    department_id = fields.Many2one('hr.department')
    auto_alter_max_consecutive_exit = fields.Boolean(string='Automatic change Leave Application')
    alter_sequence = fields.One2many('hr.alter.leave.sequence','parent_leave_type')
    is_auto_merge = fields.Boolean(string='Auto Marge')




    # this fields are used for gender specific leave
    # for example paternity leave is only apply for male not female and female can avail maternity leave
    is_gender_specific_leave = fields.Boolean(default=False,string='Gender Related')
    apply_gender = fields.Selection([('male','Male'),('female','Female')])


    # this leave are only apply for spacific religion
    # for example pilgrimage leave
    is_religion_specific_leave = fields.Boolean(default=False,string='Religion Related')
    apply_religion = fields.Many2one('hr.religion')

   #  this fields for compensatory_leave
    is_compensatory_leave = fields.Boolean(string='Compensatory Leave')
    allowed_with_in_days = fields.Integer()
    restriction = fields.Selection([('must','Must Follow'),('warning','Warning')],default='warning')

#     leave for extera validity
    is_need_extera_validation = fields.Boolean()
    appy_in_fiscal_year = fields.Float()
    apply_in_life_time = fields.Float()

#     auto clear field
    is_check_auto_clear = fields.Boolean(compute='_compute_auto_clear_data',store=True)

    @api.depends('is_auto_merge','is_gender_specific_leave','is_religion_specific_leave','is_compensatory_leave')
    def _compute_auto_clear_data(self):
        for rec in self:
            rec.is_check_auto_clear  = not rec.is_check_auto_clear or False
            if not rec.is_auto_merge:
                rec.alter_sequence = [Command.clear()]
                rec.auto_alter_max_consecutive_exit = False
            if not rec.is_gender_specific_leave:
                rec.apply_gender = None
            if not rec.is_religion_specific_leave:
                rec.apply_religion = None
            if not rec.is_compensatory_leave:
                rec.allowed_with_in_days = 0









