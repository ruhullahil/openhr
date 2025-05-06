# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class dt_approval(models.Model):
#     _name = 'dt_approval.dt_approval'
#     _description = 'dt_approval.dt_approval'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

