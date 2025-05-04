from odoo import fields, models, api


class InheritMaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = ['maintenance.equipment','portal.mixin']



    product_id = fields.Many2one('product.product')
    product_tmpl_id = fields.Many2one('product.template',related='product_id.product_tmpl_id')
    equipment_state_id = fields.Many2one('maintenance.equipment.state',group_expand='_read_group_stage_ids',tracking=True)
    partner_id = fields.Many2one('res.partner',string='User',tracking=True)
    location_id = fields.Many2one('stock.location',related='partner_id.retailer_location',store=True,tracking=True)

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages.sudo()._search([], order=stages._order)
        return stages.browse(stage_ids)


    def _track_template(self, changes):
        res = super()._track_template(changes)
        project = self[0]
        if 'equipment_state_id' in changes and project.equipment_state_id.template_id:
            res['stage_id'] = (project.equipment_state_id.template_id, {
                'auto_delete_keep_log': False,
                'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light',
            })
        return res

