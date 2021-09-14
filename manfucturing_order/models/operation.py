from odoo import models, fields, api, exceptions, _

class MrpOperationClass(models.Model):
    _name = 'mrp.operation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Name',track_visibility='onchange')


class WorkCenterClass(models.Model):
    _name = 'work.center'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Name',track_visibility='onchange')