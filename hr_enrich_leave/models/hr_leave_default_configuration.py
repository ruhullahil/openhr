from odoo import fields, models, api,_
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


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
    amount_python_compute = fields.Text(
        string="Python Code",
        default="""# Available variables:
    #-------------------------------
    # employee: hr.employee object
    # line: hr.default.leave.configuration.line object
    # Example:
    #-------------------------------
    # result = line.allocation_duration * (1/12 * line.remain_month)""",  # noqa: E501
    )
    application_condition = fields.Selection([('date', 'Date Range'), ('value', 'Value Range')],
                                             help='This field use for applicability for date range ignore the year year will be ignored in calculation')





    def _execute_python_code(self,local_dict):

        try:
            safe_eval(self.amount_python_compute, local_dict,mode="exec")
            return local_dict.get('result',0)
        except:
            raise UserError(
                _(f'{self.amount_python_compute} not executable !!'))
        # cxt = {
        #     'object': self,
        #     'env': self.env,
        #
        #     'date': date,
        #     'datetime': datetime,
        #     'timedelta': timedelta,
        #     'time': time,
        # }
        # code = definition.compute_code.strip()
        # safe_eval(code, cxt, mode="exec", nocopy=True)


    def condition_allocation_execute(self,local_dict):
        self.ensure_one()
        if self.condition_type != 'condition':
            return 0
        # TODO: have to add conditionatcondition_allocation_executeional method
        return 0

    def _get_allocation_amount(self,local_dict):
        self.ensure_one()
        employee = local_dict['employee']
        line = local_dict['line']
        if not self.condition_for or self.condition_for != 'allocation':
            return 0
        if self.condition_type == 'formula':
            if 'result' not in local_dict:
                local_dict['result'] = 0
            return self._execute_python_code(local_dict)
        return self.condition_allocation_execute(local_dict)




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
    state = fields.Selection([('draft', 'Draft'),('waiting','Waiting'), ('running', 'Running'), ('expire', 'Expire')],default='draft')
    configuration_lines = fields.One2many('hr.default.leave.configuration.line','configuration_id')


    def change_stage(self):
        pass

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'default.leave.con.seq') or _("New")
        return super().create(vals_list)


    def configurate_expiration_check(self):
        current_date = fields.Date.context_today(self)
        if self.state == 'expire' and not self.end_date:
            self.end_date = current_date
        elif self.state == 'running' and self.end_date and self.end_date < current_date:
            self.state = 'expire'
        return self.state == 'running'






    def condition_wise_auto_allocation(self,employees=None):
        configurations = self.sudo().search([])
        for configuration in configurations:
            if not configuration.configurate_expiration_check():
                continue
            configuration.configuration_lines.auto_allocation(employees)





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
    renew_day = fields.Integer(help='count hole year as 365 day and day is year of that day')
    remain_month = fields.Integer(compute='_compute_remain_month')

    def _get_end_date(self):
        self.ensure_one()
        current_yer_last_date = fields.Date.context_today(self).replace(month=12, day=31)
        return self.fiscal_year_id.date_to or current_yer_last_date

    @api.depends('renew_base','fiscal_year_id','renew_day','renew_day')
    def _compute_remain_month(self):
        date = fields.Date.context_today(self)
        for line in self:
            end_day = line._get_end_date()
            duration = relativedelta(end_day,date)
            months = duration.months
            days = duration.days
            months += 1 if days > 15 else 0
            line.remain_month = 1 if date > end_day else months

    # carry over related fields
    is_able_carry_over = fields.Boolean()
    carry_over_type = fields.Selection([('conditional', 'Conditional'), ('fixed', 'Fixed')])
    max_carry_over = fields.Float(compute='_compute_max_carry_over', store=True, readonly=False)
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
    allocation_condition_id = fields.Many2one('leave.condition',domain="[('condition_for','=','allocation')]")
    allocation_duration = fields.Float()
    allocation_ids = fields.One2many('hr.leave.allocation','config_line_id')
    # last allocation related info
    # last_allocation_id = fields.Many2one('hr.leave.allocation',compute='_compute_last_allocation_info',store=True)
    # last_allocation_start_date = fields.Date(compute='_compute_last_allocation_info',store=True)
    # last_allocation_end_date = fields.Date(compute='_compute_last_allocation_info',store=True)
    # last_allocation_corn_date = fields.Date()
    #
    # @api.depends('allocation_ids','allocation_ids.state','allocation_ids.')
    # def _compute_last_allocation_info(self):
    #     for configuration in self:
    #         configuration.


    def _get_allocation_amount(self,local_dict):
        line = local_dict['line']
        if line.allocation_type == 'fixed':
            return line.allocation_duration
        elif line.allocation_type == 'conditional':
            return line.allocation_condition_id.get_conditional_allocation(local_dict)

        return 0


#     -----------------------------------------------------------------------------------------------------------------------------------------------
#                                    Business Method
# ---------------------------------------------------------------------------------------------------------------------------------------------------

    def _get_applicable_employees(self):
        self.ensure_one()
        # add leave type related domain
        pre_domain = self.leave_type_id.get_applicability_employee_domain()
        if self.company_id:
            pre_domain += [('company_id','in',self.company_id.ids)]
        if self.department_id:
            pre_domain.append(('department_id','in',self.department_id.ids))
        employees = self.env['hr.employee'].sudo().search(pre_domain)
        return employees




    def auto_allocation(self,employees=None):
        for line in self:
            if not employees:
                employees = self._get_applicable_employees()
            for employee in employees:
                pass

