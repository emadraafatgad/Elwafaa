from odoo import models, fields, api, exceptions, _


class CarsFixClass(models.Model):
    _name = 'car.fix'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'customer'

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('reserve', "Reserved"),
        ('invoice', "Invoiced"),

    ], default='draft',track_visibility='onchange')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'


    customer = fields.Many2one('res.partner', string='Customer/Company',track_visibility='onchange')
    car = fields.Many2one('car.data', string='Car', domain="[('customer','=',customer)]",track_visibility='onchange')
    plate_number = fields.Char(string='Plate Number', related='car.plate_number',track_visibility='onchange')
    chassis_number = fields.Char(string='Chassis Number', related='car.chassis_number',track_visibility='onchange')
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True, related='car.car_model')
    driver_name = fields.Char(string='Driver Name', related='car.driver_name')
    fuel_tank = fields.Selection(
        [('zero', '0'), ('quarter', '1/4'), ('one_th', '1/3'), ('th_fo', '3/4'), ('one', '1')], string='Fuel Tank',
        related='car.fuel_tank')
    entry_counter = fields.Char(string='Entry Counter per KM', related='car.entry_counter')
    exit_counter = fields.Char(string='Exit Counter per KM', related='car.exit_counter')

    sliders = fields.Boolean(string='سوست',track_visibility='onchange')
    traps = fields.Boolean(string='عفشة',track_visibility='onchange')
    danagel = fields.Boolean(string='دناجل',track_visibility='onchange')
    entery_date = fields.Date(string='Entry date',track_visibility='onchange')
    fix_date = fields.Date(string='Fix date',track_visibility='onchange')
    delivery_date = fields.Date(string='Delivery date',track_visibility='onchange')
    for_companies = fields.Char('خاص بالشركات',track_visibility='onchange')
    authority = fields.Char('Authority',track_visibility='onchange')
    supervisor_name = fields.Char('اسم المشرف',track_visibility='onchange')
    technician_name = fields.Char('اسم الفني ',track_visibility='onchange')
    worker_name = fields.Many2many('worker.name', string='العمال',track_visibility='onchange')
    customer_complain = fields.Text(string='شكوي العميل ',track_visibility='onchange')

    parts = fields.One2many('car.part', 'car_parts_inv', string='Car Parts',track_visibility='onchange')
    operation_type = fields.Many2one('stock.picking.type', string='Operation Type',track_visibility='onchange')
    location_id = fields.Many2one('stock.location', string='Source Location	',track_visibility='onchange')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location',track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account',help="The income or expense account related to the selected product.",track_visibility='onchange')

    @api.multi
    def create_invoice_with_fix_data(self):
        inv = self.env['account.invoice'].create({
            'partner_id': self.customer.id,
        })
        for line in self.parts:
            for l in inv:
                l.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': line.product.id,
                        'quantity': line.quantity,
                        'name': str(line.product.name),
                        'price_unit': line.product.lst_price,
                        'account_id': self.account_id.id,

                    })]
                })
        self.state = 'invoice'

        # for line in self.emp_comparison:
        #     for record in self.env['hr.employee'].search([('name', '=', line.emp_name.name)]):
        #         if line.condition == True:
        #             record.write({
        #                 'emp_record_comparison': [(0, 0, {
        #                     'training_name': line.required_program.id,
        #                     'training_hours': line.training_hours,
        #                     'date_to': line.date_to,
        #                     'date_from': line.date_from,
        #                     'trainer_org': line.course_type,
        #                     'ommat': line.ommat,
        #                     'place': line.center.id,
        #                     'course_cost': line.course_cost,
        #                     'year_emp_screen': line.year_here,
        #                 })]
        #             })

    @api.multi
    def create_delivery_records_in_the_stock(self):
        # stok_pick = self.env['stock.picking']
        # vals = {
        #
        #     'partner_id': self.customer.id,
        #     'picking_type_id': self.operation_type.id,
        #     'location_id': self.location_id.id,
        #     'location_dest_id': self.location_dest_id.id,
        #
        # }
        # stok_pick.create(vals)
        employee = self.env['stock.picking'].create({
            'partner_id': self.customer.id,
            'picking_type_id': self.operation_type.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'supervisor_name': self.supervisor_name,

        })
        for line in self.parts:
            # asd = self.env['stock.picking'].search([('partner_id', '=', self.customer.id)])
            for l in employee:
                l.write({
                    'move_ids_without_package': [(0, 0, {
                        'name': 'OP00',
                        'product_id': line.product.id,
                        'product_uom_qty': line.quantity,
                        'product_uom': line.product_uom.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,


                    })]
                })
        self.state = 'confirmed'

        # for line in self.emp_comparison:
        #     for record in self.env['hr.employee'].search([('name', '=', line.emp_name.name)]):
        #         if line.condition == True:
        #             record.write({
        #                 'emp_record_comparison': [(0, 0, {
        #                     'training_name': line.required_program.id,
        #                     'training_hours': line.training_hours,
        #                     'date_to': line.date_to,
        #                     'date_from': line.date_from,
        #                     'trainer_org': line.course_type,
        #                     'ommat': line.ommat,
        #                     'place': line.center.id,
        #                     'course_cost': line.course_cost,
        #                     'year_emp_screen': line.year_here,
        #                 })]
        #             })

    # sale_quotation=fields.Many2one('sale.order',string='Sale')

    @api.multi
    @api.depends('stock.state', 'customer', 'supervisor_name', 'parts')
    def action_reserve(self):
        for line in self:
            asd = self.env['stock.picking'].search(
                [('partner_id', '=', line.customer.id), ('supervisor_name', '=', line.supervisor_name)])
            if asd:
                print(asd)
                for rec in asd:
                    if rec.state == 'done':
                        for m in rec.move_ids_without_package:
                            for record in line.parts:
                                 if m.product_id.id == record.product.id :
                                     print('hello dear')
                                     record.quantity_done = m.quantity_done
                                     if record.quantity_done >0:
                                       self.state = 'reserve'


class CarsPartsClass(models.Model):
    _name = 'car.part'
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product',track_visibility='onchange')
    quantity = fields.Float(string='Quantity',track_visibility='onchange')
    quantity_done = fields.Float(string='Reserved Quantity',readonly=True,track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure',track_visibility='onchange')
    customer = fields.Many2one('res.partner', string='Customer/Company',related='car_parts_inv.customer')
    supervisor_name = fields.Char('اسم المشرف',related='car_parts_inv.supervisor_name',track_visibility='onchange')
    stock = fields.Many2one('stock.picking')


    car_parts_inv = fields.Many2one('car.fix')

    # @api.multi
    # @api.depends('stock.state','customer','supervisor_name','product','quantity')
    # def action_reserve(self):
    #     for line in self:
    #        asd =self.env['stock.picking'].search([('partner_id', '=', line.customer.id),('supervisor_name', '=', line.supervisor_name)])
    #        if asd:
    #            print('hello')
    #            for rec in asd:
    #                if rec.state=='done':
    #                    for m in rec.move_ids_without_package:
    #                        if m.product_id.id == line.product.id and m.product_uom_qty == line.quantity:
    #                            line.quantity_done = m.quantity_done





class StockPickingClass(models.Model):
    _inherit = 'stock.picking'

    supervisor_name = fields.Char('اسم المشرف',track_visibility='onchange')
