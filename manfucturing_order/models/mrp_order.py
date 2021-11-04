from odoo import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools import datetime


class MrpOrderClass(models.Model):
    _name = 'mrp.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product'

    customer = fields.Many2one('res.partner', string='Customer', track_visibility='onchange', required=True)
    product = fields.Many2one('product.product', string='Product',track_visibility='onchange',required=True)
    quantity = fields.Float(string='Quantity To Produce', track_visibility='onchange',required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange',related='product.uom_id')
    routing = fields.Many2one('manfucturing.steps',string='Routing',track_visibility='onchange',copy=True,store=True,required=True)
    bill_of_materials = fields.Many2one('temp.bom',string='Bill of Material',required=True,track_visibility='onchange' ,domain="[('product', '=', product)]",)
    date_start = fields.Date(string='Start Date',track_visibility='onchange',required=True,default=fields.Date.today())
    date_end = fields.Date(string='End Date',track_visibility='onchange',required=True,default=fields.Date.today())
    source = fields.Char(string='Source Origin',track_visibility='onchange')
    responsible_user = fields.Many2one('res.users', string='Responsible User', track_visibility='onchange',default=lambda self: self.env.user)
    transfer_lines =fields.One2many('mrp.order_bridge','mrp_order_inv',store=True)
    man_step_lines = fields.One2many('mrp.order_bridge_steps', 'mrp_order_man_step_inv',readonly=False,compute='create_routing_template_records',store=True,copy=True)
    seq =fields.Char('Sequence',readonly=True)
    source_location =fields.Many2one('stock.location',string='Source Location',related='routing.raw_materials_location')
    dest_location = fields.Many2one('stock.location', string='Destination Location')
    operation_type = fields.Many2one('stock.picking.type', string='Operation Type')

    state = fields.Selection([
        ('draft', "Draft"),
        ('start', "In Progress"),
        ('done', "Done"),
    ], default='draft')

    @api.multi
    def action_draft(self):
        self.state='draft'

    @api.multi
    def action_confirm(self):
        asd = self.env['mrp.request'].search([('mrb_order_id', '=', self.id)])
        if asd:
            asd.state ='in_progress'
        self.state = 'start'

    @api.multi
    def action_finish(self):
        pick = self.env['stock.picking'].create({
            'partner_id': self.customer.id,
            'picking_type_id': self.operation_type.id,
            'location_id': self.source_location.id,
            'location_dest_id': self.dest_location.id,
            'origin': self.source,
            'manf_id': self.id,

        })
        for l in pick:
                    l.write({
                        'move_ids_without_package': [(0, 0, {
                            'name': str(self.product.name),
                            'product_id': self.product.id,
                            'product_uom_qty': self.quantity,
                            'product_uom': self.product_uom.id,
                            'location_id': self.source_location.id,
                            'location_dest_id': self.dest_location.id,

                        })]
                    })
        asd = self.env['mrp.request'].search([('mrb_order_id', '=', self.id)])
        if asd:
            asd.state = 'lock'
        self.state = 'done'

    @api.model
    def create(self, vals):
        vals['seq'] = self.env['ir.sequence'].next_by_code('mrp_order_sequence')
        return super(MrpOrderClass, self).create(vals)

    @api.one
    @api.depends('routing')
    def create_routing_template_records(self):
        if self.routing:
            l = []
            asd = self.env['manfucturing.steps'].search([('name', '=', self.routing.name)])
            if asd:
                for rec in asd.steps_lines:
                    l.append({
                             'operation': rec.operation.id,
                             'work_center': rec.work_center.id,
                             'date_start': fields.Datetime.now(),
                             'date_end': fields.Datetime.now(),
                              })
                # if not self.date_start or not self.date_end:
                #     raise ValidationError('Please ')
                self.man_step_lines = l

    # @api.one
    # @api.depends('bill_of_materials')
    # def create_bill_of_materials_records(self):
    #     if self.bill_of_materials:
    #         l = []
    #         asd = self.env['temp.bom'].search([('name', '=', self.bill_of_materials.name)])
    #         if asd:
    #             for rec in asd.lines:
    #                 l.append({
    #                     'product': rec.product.id,
    #                     'to_consume': rec.quantity * self.quantity,
    #                     'operation': rec.operation.id,
    #
    #                 })
    #             self.transfer_lines = l


class MrpOrderBridgeClass(models.Model):
    _name = 'mrp.order_bridge'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', track_visibility='onchange',required=True)
    # quantity = fields.Float(string='Quantity To Produce', track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange',related='product.uom_id',readonly=True)
    to_consume = fields.Float(string='To Consume', track_visibility='onchange',copy=True,store=True)
    to_reserve = fields.Float(string='To Reserve', track_visibility='onchange',compute='compute_to_reserve_from_to_consume')
    consumed = fields.Float(string='Consumed', track_visibility='onchange')
    operation = fields.Many2one('mrp.operation',string='Operation')
    mrp_order_inv = fields.Many2one('mrp.order')
    source_location = fields.Many2one('stock.location', string='Source Location')
    dest_location = fields.Many2one('stock.location', string='Destination Location')
    operation_type = fields.Many2one('stock.picking.type', string='Operation Type')

    @api.multi
    @api.depends('to_consume')
    def compute_to_reserve_from_to_consume(self):
        for rec in self:
            rec.to_reserve =rec.to_consume


class MrpOrderBridgeStepsClass(models.Model):
    _name = 'mrp.order_bridge_steps'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'operation'

    # @api.model
    @api.onchange('operation')
    def _domain_operation(self):
        list = []
        for line in self.mrp_order_man_step_inv.routing.steps_lines:
            print(line.operation)
            list.append(line.operation.name)
        # domain = [
        #     ('operation', 'in', list)
        # ]
        return {'domain': {'operation': [('name', 'in', list)]}}

    operation = fields.Many2one('mrp.operation', string='Operation')
    work_center = fields.Many2one('work.center', string='Work Center')
    date_start = fields.Datetime(string='Start Date',default=fields.Datetime.now(),copy=True,store=True)
    date_end = fields.Datetime(string='End Date',default=fields.Datetime.now(),copy=True,store=True)
    expected = fields.Float(string='Expected Duration', track_visibility='onchange')
    real_duration = fields.Char(string='Real Duration', track_visibility='onchange')
    routing = fields.Many2one('manfucturing.steps',string='Routing',related='mrp_order_man_step_inv.routing')
    lead_time_unit = fields.Char(string='Time Unit',default="Days:Hours:Minutes:Seconds",track_visibility='onchange',store=True,copy=True,readonly=True)
    mrp_order_man_step_inv = fields.Many2one('mrp.order')


    @api.multi
    def action_start(self):
        self.mrp_order_man_step_inv.action_confirm()
        self.date_start =fields.Datetime.now()
        if self.mrp_order_man_step_inv.transfer_lines :
            for line in self.mrp_order_man_step_inv.transfer_lines:
                if line.operation == self.operation:
                     line.source_location = self.mrp_order_man_step_inv.source_location
                     line.dest_location = self.mrp_order_man_step_inv.dest_location
                     line.operation_type = self.mrp_order_man_step_inv.operation_type
            pick = self.env['stock.picking'].create({
                'partner_id': self.mrp_order_man_step_inv.customer.id,
                'picking_type_id': self.mrp_order_man_step_inv.operation_type.id,
                'location_id': self.mrp_order_man_step_inv.source_location.id,
                'location_dest_id': self.mrp_order_man_step_inv.dest_location.id,
                'origin': self.mrp_order_man_step_inv.source,
                'manf_id': self.id,

            })
            for line in self.mrp_order_man_step_inv.transfer_lines:
                if line.operation == self.operation:
                    for l in pick:
                        l.write({
                            'move_ids_without_package': [(0, 0, {
                                'name': str(line.operation.name),
                                'product_id': line.product.id,
                                'product_uom_qty': line.to_consume,
                                'product_uom': line.product_uom.id,
                                'location_id': self.mrp_order_man_step_inv.source_location.id,
                                'location_dest_id': self.mrp_order_man_step_inv.dest_location.id,

                            })]
                        })


            # pick.state = 'waiting'
            # pick.action_done()
            # pick.button_validate()

    @api.multi
    def action_finish(self):
        self.date_end = fields.Datetime.now()
        if self.date_start and self.date_end:
            start_dt = fields.Datetime.from_string(self.date_start)
            finish_dt = fields.Datetime.from_string(self.date_end)
            difference = relativedelta(finish_dt, start_dt)
            days = difference.days
            hours = difference.hours
            minutes = difference.minutes
            sec = difference.seconds
            time =str(days) +':'+str(hours) +':'+str(minutes)+':'+str(sec)
            self.real_duration = time

        picking = self.env['stock.picking'].search([('manf_id', '=', self.id)])
        if picking:
            for rec in picking:
                rec.action_confirm()
                rec.action_assign()
            print('hhhhhhhhh')
            self.action_val()



    @api.multi
    def action_val(self):
        picking = self.env['stock.picking'].search([('manf_id', '=', self.id),('state', '=','assigned')])
        if picking:
            for rec in picking:
                rec.button_validate()
                print('hi')
    # @api.multi
    # @api.depends('date_start','date_end')
    # def difference_date_cal(self):
    #  for rec in self:
    #
    #     fmt = '%Y-%m-%d'
    #     start_date = rec.date_start
    #     end_date = rec.date_end
    #     d1 = datetime.strptime(str(start_date), fmt)
    #     d2 = datetime.strptime(str(end_date), fmt)
    #     if d2 >= d1:
    #       rec.real_duration = (d2 - d1).days
    #     else:
    #      raise ValidationError(_('end date should be superior than start date'))

    # @api.one
    # @api.depends('date_start', 'date_end')
    # def _total_minutes(self):
    #     if self.date_start and self.date_end:
    #         start_dt = fields.Datetime.from_string(self.date_start)
    #         finish_dt = fields.Datetime.from_string(self.date_end)
    #         difference = relativedelta(finish_dt, start_dt)
    #         days = difference.days
    #         hours = difference.hours
    #         minutes = difference.minutes
    #         seconds = difference.seconds
    #         if self.lead_time_unit =='seconds':
    #             self.real_duration = seconds
    #         elif self.lead_time_unit == 'minutes':
    #             self.real_duration = minutes
    #         elif self.lead_time_unit == 'hours':
    #             self.real_duration = hours
    #         else:
    #             self.real_duration = days



class StockPickingClassManf(models.Model):
    _inherit = 'stock.picking'

    manf_id = fields.Integer()
