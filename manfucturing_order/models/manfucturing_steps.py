from odoo import models, fields, api, exceptions, _

class ManfucturingStepsClass(models.Model):
    _name = 'manfucturing.steps'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Routing Name',track_visibility='onchange',required=True)
    raw_materials_location = fields.Many2one('stock.location',string='Raw Materials Location')

    steps_lines = fields.One2many('manfucturing.steps_bridge','steps_inv',string='Steps Lines')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique!'),
    ]


class ManfucturingStepsBridgeClass(models.Model):
    _name = 'manfucturing.steps_bridge'

    operation = fields.Many2one('mrp.operation',string='Operation')
    work_center = fields.Many2one('work.center',string='Work Center')

    steps_inv = fields.Many2one('manfucturing.steps')