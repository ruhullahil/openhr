# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class dt_mr_mi(models.Model):
#     _name = 'dt_mr_mi.dt_mr_mi'
#     _description = 'dt_mr_mi.dt_mr_mi'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

