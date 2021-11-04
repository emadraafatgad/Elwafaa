from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class BillofMaterialTemplate(models.Model):
    _name = 'temp.bom'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Template Name',track_visibility='onchange',store=True,copy=True,required=True)
    product=fields.Many2one('product.product',string='Product',track_visibility='onchange',store=True,copy=True,required=True)
    lead_time = fields.Float(string='Lead Time')
    routing = fields.Many2one('manfucturing.steps',string='Routing',track_visibility='onchange',copy=True,store=True,required=True)
    lead_time_unit = fields.Selection([
        ('hours', "Hours"),
        ('days', "Days"),
        ('weeks', "Weeks"),
        ('months', "Months"),
    ], track_visibility='onchange')
    description=fields.Text(string='Description',track_visibility='onchange')
    lines = fields.One2many('temp.bom_bridge','bom_inverse',string='Lines',store=True,copy=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name,car_model)', 'Name must be unique!'),
    ]

    @api.multi
    @api.constrains('lines')
    def _check_quantity_lines(self):
        for line in self.lines:
            if line.quantity < 1:
                raise ValidationError(_('quantity can not be less than 1'))




class BillofMaterialTemplateBridge(models.Model):
    _name = 'temp.bom_bridge'
    _rec_name = 'product'

    product=fields.Many2one('product.product',track_visibility='onchange',store=True,copy=True,required=True)
    quantity = fields.Float(string='Quantity', track_visibility='onchange',required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange',related='product.uom_id',readonly=True)
    operation=fields.Many2one('mrp.operation',string='Operation', track_visibility='onchange',store=True,copy=True)

    bom_inverse=fields.Many2one('temp.bom')