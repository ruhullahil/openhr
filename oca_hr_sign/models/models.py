from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'


    sign_template_id = fields.Many2one('sign.oca.template',compute='_compute_sign_template',store=True,readonly=False)
    sign_request_count = fields.Integer(compute='_compute_request_count')


    @api.depends('partner_id')
    def _compute_request_count(self):
        for applicant in self:
            applicant.sign_request_count = applicant.partner_id.signer_count or 0

    @api.depends('job_id')
    def _compute_sign_template(self):
        for rec in self:
            if not rec.sign_template_id:
                rec.sign_template_id = rec.job_id.sign_template_id or None

    def send_oca_sign(self):
        self.ensure_one()
        if not self.sign_template_id:
            raise ValidationError('Sign template is not Added !!')

        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': _('Sign configuration'),
            'view_mode': 'form',
            'res_model': 'sign.oca.template.generate',
            'context': {'default_template_id': self.sign_template_id.id},
        }

    def navigate_sign_requests(self):
        sign_request_ids = self.partner_id.signer_ids.mapped('request_id')

        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Requests'),
            'view_mode': 'list,form',
            'res_model': 'sign.oca.request',
            'domain': [('id', 'in', sign_request_ids.ids)],
        }



    
    
class HRJob(models.Model):
    _inherit = 'hr.job'

    sign_template_id = fields.Many2one('sign.oca.template')


class OCASignTemplate(models.Model):
    _inherit = 'sign.oca.template'


    def send_template(self):
        self.ensure_one()
        action = self.env.ref('sign_oca.sign_oca_template_generate_act_window')
        action['context'] = {'default_template_id': self.id}
        return action




    

    


