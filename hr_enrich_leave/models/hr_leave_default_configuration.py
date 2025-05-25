from odoo import fields, models, api,_



# ---------------------------------------------------------------------------------------------------
#                                                   Condition related models
#
#   use case
#
# -----------------------------------------------------------------------------------------------------

class AllocationCondition(models.Model):
    _name = 'leave.condition'
    _description = 'Leave Condition'

    name = fields.Char()
    condition_for = fields.Selection([('allocation', 'Allocation'), ('carry_over', 'Carry Over')])
    condition_type = fields.Selection([('formula', 'Formula'), ('condition', 'Condition')])
    formula = fields.Char()
    application_condition = fields.Selection([('date', 'Date Range'), ('value', 'Value Range')],
                                             help='This field use for applicability for date range ignore the year year will be ignored in calculation')


class LeaveConditionLine(models.Model):
    _name = 'leave.condition.line'
    _description = 'LeaveConditionLine'
    _rec_name = 'condition_id'

    condition_id = fields.Many2one('leave.condition')
    from_date = fields.Date()
    to_date = fields.Date()
    from_range = fields.Integer()
    to_range = fields.Integer()
    quantity = fields.Float()

# ----------------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------------------------------------
#                                               configuration models
# ------------------------------------------------------------------------------------------------------------------------




class HrDefaultConfiguration(models.Model):
    _name = 'hr.default.leave.configuration'
    _description = 'HrDefaultConfiguration'
    _rec_name = 'name'

    company_id = fields.Many2one('res.company',default= lambda self: self.env.company.id)
    department_id = fields.Many2one('hr.department')
    name = fields.Char()
    start_from = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([('draft', 'Draft'),('waiting','Waiting'), ('running', 'Running'), ('expire', 'Expire')],deafult='draft')
    allocation_lines = fields.One2many('hr.default.leave.configuration.line','configuration_id')


    def change_stage(self):
        pass

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'default.leave.con.seq') or _("New")
        return super().create(vals_list)


class HrDefaultConfigLine(models.Model):
    _name = 'hr.default.leave.configuration.line'
    _description = 'HrDefaultConfigLine'
    _rec_name = 'configuration_id'

    configuration_id = fields.Many2one('hr.default.leave.configuration')
    company_id = fields.Many2one('res.company', related='configuration_id.company_id',store=True)
    department_id = fields.Many2one('hr.department', related='configuration_id.department_id',store=True)
    leave_type_id = fields.Many2one('hr.leave.type',domain="[('allocation_validation_type','=','no_validation')]")

    # renew related fields
    is_auto_renew = fields.Boolean()
    renew_cycle = fields.Selection(
        [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')])
    renew_base = fields.Selection([('fixed', 'Fixed'), ('join_date', 'Join Date'),('fiscal','Fiscal Year')])
    # fiscal year field is visible for fiscal selection and if we select it , renew base on fiscal year
    #
    fiscal_year_id = fields.Many2one('account.fiscal.year')
    renew_day = fields.Integer()

    # carry over related fields
    is_able_carry_over = fields.Boolean()
    carry_over_type = fields.Selection([('conditional', 'Conditional'), ('fixed', 'Fixed')])
    max_carry_over = fields.Float(compute='_compute_max_carry_over', store=True, readonly=False)
    # Todo : Have to add conditional carry over model
    carry_over_condition_id = fields.Many2one('leave.condition',domain="[('condition_for','=','carry_over')]")
    is_able_use_carry_over = fields.Boolean()
    max_carry_over_use = fields.Float()

    @api.depends('carry_over_type')
    def _compute_max_carry_over(self):
        for rec in self:
            if rec.carry_over_type == 'fixed':
                rec.max_carry_over = 0
            else:
                rec.max_carry_over = 0

    # Allocation related fields
    allocation_type = fields.Selection([('fixed', 'Fixed'), ('conditional', 'Conditional')])
    # TODO :Have to add allocation condition_id
    allocation_condition_id = fields.Many2one('leave.condition',domain="[('condition_for','=','allocation')]")
    allocation_duration = fields.Float()
    allocation_ids = fields.One2many('hr.leave.allocation','config_line_id')
    # last allocation related info
    last_allocation_id = fields.Many2one('hr.leave.allocation',compute='_compute_last_allocation_id')
    last_allocation_date = fields.Date()
    # TODO : need to add allocation cycle releted info
