from odoo import models, fields, api, exceptions, _

class BillofMaterialTemplate(models.Model):
    _name = 'temp.bom'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Template Name',track_visibility='onchange',store=True,copy=True)
    lead_time = fields.Float(string='Lead Time')
    lead_time_unit = fields.Selection([
        ('hours', "Hours"),
        ('days', "Days"),
        ('weeks', "Weeks"),
        ('months', "Months"),
    ], track_visibility='onchange')


    lines = fields.One2many('temp.bom_bridge','bom_inverse',string='Lines',store=True,copy=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name,car_model)', 'Name,Car Model must be unique!'),
    ]

class BillofMaterialTemplateBridge(models.Model):
    _name = 'temp.bom_bridge'
    _rec_name = 'product'

    product=fields.Many2one('product.product',track_visibility='onchange',store=True,copy=True)
    quantity = fields.Float(string='Quantity', track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange')
    operation=fields.Many2one('mrp.operation',string='Operation', track_visibility='onchange',store=True,copy=True)

    bom_inverse=fields.Many2one('temp.bom')