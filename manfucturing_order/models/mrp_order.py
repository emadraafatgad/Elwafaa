from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from odoo.tools import datetime


class MrpOrderClass(models.Model):
    _name = 'mrp.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product',track_visibility='onchange')
    quantity = fields.Float(string='Quantity To Produce', track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange')
    routing = fields.Many2one('manfucturing.steps',string='Routing',track_visibility='onchange',copy=True,store=True)
    bill_of_materials = fields.Many2one('temp.bom',string='Bill of Material',track_visibility='onchange')
    date_start = fields.Date(string='Start Date',track_visibility='onchange')
    date_end = fields.Date(string='End Date',track_visibility='onchange')
    source = fields.Char(string='Source Origin',track_visibility='onchange')
    responsible_user = fields.Many2one('res.users', string='Responsible User', track_visibility='onchange',default=lambda self: self.env.user)

    transfer_lines =fields.One2many('mrp.order_bridge','mrp_order_inv')
    man_step_lines = fields.One2many('mrp.order_bridge_steps', 'mrp_order_man_step_inv',readonly=False,compute='create_routing_template_records',store=True,copy=True)

    @api.one
    @api.depends('routing')
    def create_routing_template_records(self):
        if self.routing:
            l = []
            asd = self.env['manfucturing.steps'].search([('name', '=', self.routing.name)])
            if asd:
                for rec in asd.steps_lines:
                    l.append({'operation': rec.operation.id,
                              'work_center': rec.work_center.id,
                              'date_start': fields.Date.today(),
                              'date_end': fields.Date.today(),
                              })
                self.man_step_lines = l
            # for line in self.emp_comparison:
            #   for l in asd:
            #       l.write({
            #           'emp_comparison': [(0, 0, {
            #               'required_program': line.required_program.id,
            #               'emp_name': line.emp_name.id,
            #               'emp_code': line.emp_no,
            #               'ommat': line.ommat,
            #           })]
            #       })


class MrpOrderBridgeClass(models.Model):
    _name = 'mrp.order_bridge'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', track_visibility='onchange')
    # quantity = fields.Float(string='Quantity To Produce', track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange')
    to_consume = fields.Float(string='To Consume', track_visibility='onchange')
    to_reserve = fields.Float(string='To Reserve', track_visibility='onchange')
    consumed = fields.Float(string='Consumed', track_visibility='onchange')
    operation = fields.Many2one('mrp.operation',string='Operation')
    mrp_order_inv = fields.Many2one('mrp.order')


class MrpOrderBridgeStepsClass(models.Model):
    _name = 'mrp.order_bridge_steps'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'operation'

    operation = fields.Many2one('mrp.operation', string='Operation')
    work_center = fields.Many2one('work.center', string='Work Center')
    date_start = fields.Date(string='Start Date',default=fields.Date.today())
    date_end = fields.Date(string='End Date',default=fields.Date.today())
    expected = fields.Float(string='Expected', track_visibility='onchange')
    real_duration = fields.Float(string='Real Duration', track_visibility='onchange',compute='difference_date_cal')

    mrp_order_man_step_inv = fields.Many2one('mrp.order')

    @api.multi
    @api.depends('date_start','date_end')
    def difference_date_cal(self):
     for rec in self:

        fmt = '%Y-%m-%d'
        start_date = rec.date_start
        end_date = rec.date_end
        d1 = datetime.strptime(str(start_date), fmt)
        d2 = datetime.strptime(str(end_date), fmt)
        if d2 >= d1:
          rec.real_duration = (d2 - d1).days
        else:
         raise ValidationError(_('end date should be superior than start date'))