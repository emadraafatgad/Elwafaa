from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError


class CarsFixClass(models.Model):
    _name = 'car.fix'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'customer'


    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('reserve', "Reserved"),
        ('request', "Request Parts"),
        ('finish', "Fixing Finished"),
        ('invoice', "Invoiced"),

    ], default='draft',track_visibility='onchange')

    @api.multi
    def action_draft(self):
        self.state = 'request'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_finish(self):
        self.state = 'finish'


    customer = fields.Many2one('res.partner', string='Customer/Company',track_visibility='onchange',required=True)
    car = fields.Many2one('car.data', string='Car Information', domain="[('customer','=',customer)]",track_visibility='onchange')
    plate_number = fields.Char(string='Plate Number',track_visibility='onchange',required=True,readonly=False)
    chassis_number = fields.Char(string='Chassis Number',track_visibility='onchange',required=True,readonly=False)
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True,required=True,readonly=False)
    driver_name = fields.Char(string='Driver Name',readonly=False)
    fuel_tank = fields.Selection(
        [('zero', '0'), ('quarter', '1/4'), ('one_th', '1/3'), ('th_fo', '3/4'), ('one', '1')], string='Fuel Tank',readonly=False
       )
    entry_counter = fields.Char(string='Entry Counter per KM')
    exit_counter = fields.Char(string='Exit Counter per KM')

    sliders = fields.Boolean(string='سوست',track_visibility='onchange')
    traps = fields.Boolean(string='عفشة',track_visibility='onchange')
    danagel = fields.Boolean(string='دناجل',track_visibility='onchange')
    entery_date = fields.Date(string='Entry date',track_visibility='onchange')
    fix_date = fields.Date(string='Fix date',track_visibility='onchange')
    delivery_date = fields.Date(string='Delivery date',track_visibility='onchange')
    for_companies = fields.Char('خاص بالشركات',track_visibility='onchange')
    authority = fields.Char('Authority',track_visibility='onchange')
    supervisor_name = fields.Char('اسم المشرف',track_visibility='onchange',required=True)
    technician_name = fields.Char('اسم الفني ',track_visibility='onchange',required=True)
    worker_name = fields.Many2many('worker.name', string='العمال',track_visibility='onchange')
    customer_complain = fields.Text(string='شكوي العميل ',track_visibility='onchange')
    car_issue=fields.Many2one('car.issue',string='Car Issue')

    service = fields.One2many('worker.service', 'service_inv', string='Service',track_visibility='onchange',store=True)
    parts = fields.One2many('car.part', 'car_parts_inv', string='Car Parts',track_visibility='onchange',store=True)
    operation_type = fields.Many2one('stock.picking.type', string='Operation Type',track_visibility='onchange')
    location_id = fields.Many2one('stock.location', string='Source Location	',track_visibility='onchange',related='operation_type.default_location_src_id')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location',track_visibility='onchange',related='operation_type.default_location_dest_id')

    counter = fields.Integer(default=1,store=True,copy=True)
    @api.multi
    @api.constrains('parts','service')
    def _check_price_unit(self):
        for rec in self.parts:
            if rec.price_unit <= 0:
                raise ValidationError(
                    _('some product for this company/customer has no price list please create price list for them to continue'))
        for line in self.service:
            if line.price_unit <= 0:
                raise ValidationError(
                    _('some product for this company/customer has no price list please create price list for them to continue'))

    @api.multi
    def create_invoice_with_fix_data(self):
        inv = self.env['account.invoice'].create({
            'partner_id': self.customer.id,
            'car': self.car.id,
            'plate_number': self.plate_number,
            'chassis_number': self.chassis_number,
            'car_model': self.car_model.id,
            'driver_name': self.driver_name,
            'supervisor_name': self.supervisor_name,
            'technician_name': self.technician_name,

        })
        for line in self.parts:
            for l in inv:
                l.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': line.product.id,
                        'quantity': line.quantity,
                        'name': str(line.product.name),
                        'price_unit': line.price_unit,
                        'account_id': line.account_id.id,
                        # 'car_type': line.car_type.id,
                        'car_model': line.car_model.id,

                    })]
                })
        for line in self.service:
            for l in inv:
                l.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': line.product.id,
                        'quantity': line.no_of_hours,
                        'name': str(line.product.name),
                        'price_unit': line.price_unit,
                        'account_id': line.account_id.id,

                    })]
                })
        self.state = 'invoice'
        inv.state = 'wait'

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
        self.counter = self.counter+1
        if len(self.parts) ==1:
            if self.parts.quantity_done >0:
                raise ValidationError(
                    _('this quantities has requested before.'))

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
            'technician_name': self.technician_name,
            'plate_number': self.plate_number,
            'car_id': self.id,
            'counter': self.counter,

        })
        for line in self.parts:
          if line.quantity_done <=0:
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
        # self.counter=extra_count +1
        self.state = 'confirmed'
        employee.state='waiting'
        employee.action_done()

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
    @api.depends('stock.state', 'customer', 'supervisor_name', 'parts','plate_number','technician_name')
    def action_reserve(self):
        for line in self:
            asd = self.env['stock.picking'].search(
                [('partner_id', '=', line.customer.id), ('supervisor_name', '=', line.supervisor_name),('technician_name', '=', line.technician_name),('plate_number', '=', line.plate_number),('car_id', '=', line.id),('counter', '=', line.counter)])
            if asd:
                for rec in asd:
                    if rec.state == 'assigned':
                        for m in rec.move_ids_without_package:
                            for record in line.parts:
                                 if m.product_id.id == record.product.id and m.product_uom_qty == record.quantity :
                                     if m.reserved_availability >0:
                                         record.quantity_done = m.reserved_availability
                                         record.done = m.quantity_done
                                         record.state = m.state
                                     else:
                                         raise ValidationError(
                                             _('some quantities not reserved yet please check your stock to complete process.'))


                    elif rec.state == 'done':
                        for m in rec.move_ids_without_package:
                            for record in line.parts:
                                 if m.product_id.id == record.product.id and m.product_uom_qty == record.quantity :
                                     if m.quantity_done > 0:
                                         record.done = m.quantity_done
                                         record.state = m.state
                                         self.state = 'reserve'
                                     else:
                                         raise ValidationError(
                                             _('some quantities not done yet please check your stock to complete process.'))
                    else:
                        raise ValidationError(
                            _('some quantities not reserved yet please check your stock to complete process.'))


class CarsPartsClass(models.Model):
    _name = 'car.part'
    _rec_name = 'product'


    # def _default_accou(self):
    #     journal_id = self._context.get('journal_id') or self._context.get('default_journal_id')
    #     if journal_id:
    #         journal = self.env['account.journal'].browse(journal_id)
    #         if self._context.get('type') in ('out_invoice', 'in_refund'):
    #             return journal.default_credit_account_id.id
    #         return journal.default_debit_account_id.id

    account_id = fields.Many2one('account.account', string='Account',readonly=False,
                                 compute='compute_def_account',
                                 help="The income or expense account related to the selected product.")

    @api.multi
    @api.depends('product')
    def compute_def_account(self):
        for line in self:
            if line.product.property_account_income_id:
                line.account_id = line.product.property_account_income_id
            elif line.product.categ_id.property_account_income_categ_id:
                line.account_id = line.product.categ_id.property_account_income_categ_id
            elif line.product.categ_id.parent_id.property_account_income_categ_id:
                line.account_id = line.product.categ_id.parent_id.property_account_income_categ_id
            elif line.product.categ_id.parent_id.parent_id.property_account_income_categ_id:
                line.account_id = line.product.categ_id.parent_id.parent_id.property_account_income_categ_id


    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    product = fields.Many2one('product.product', string='Product',track_visibility='onchange',)
    car_type = fields.Many2one('car.data', string='Car',compute='cal_car_type_parts_inv_car',store=True)
    car_model = fields.Many2one('model.car', string='Car Model', store=True,compute='cal_car_type_parts_inv_car')
    quantity = fields.Float(string='Quantity',track_visibility='onchange')
    quantity_done = fields.Float(string='Available Quantity',store=True,readonly=True,track_visibility='onchange')
    done = fields.Float(string='Done Quantity',store=True, readonly=True, track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure',track_visibility='onchange',related='product.uom_id')
    customer = fields.Many2one('res.partner', string='Customer/Company',related='car_parts_inv.customer')
    supervisor_name = fields.Char('اسم المشرف',related='car_parts_inv.supervisor_name',track_visibility='onchange')
    stock = fields.Many2one('stock.picking')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status',readonly=True, store=True, track_visibility='onchange')


    car_parts_inv = fields.Many2one('car.fix')

    @api.multi
    @api.onchange('product','car_parts_inv')
    def cal_car_type_parts_inv_car(self):
        for rec in self:
           # rec.car_type = rec.car_parts_inv.car
           rec.car_model = rec.car_parts_inv.car_model

    price_unit = fields.Float('Price', compute='check_product_company_priclist')

    @api.multi
    @api.depends('product', 'customer','car_model')
    def check_product_company_priclist(self):
        for rec in self:
            asd = rec.env['company.price_bridge'].search(
                [('customerr', '=', rec.customer.id), ('product', '=', rec.product.id),('car_model', '=', rec.car_model.id)])
            if asd:
                rec.price_unit = asd.total

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
    technician_name = fields.Char('اسم المتخصص ',track_visibility='onchange')
    plate_number = fields.Char(string='Plate Number',track_visibility='onchange')
    car_id = fields.Many2one('car.fix', track_visibility='onchange')
    counter = fields.Integer(default=1,store=True,copy=True)



    @api.multi
    @api.constrains('move_ids_without_package')
    def _check_quantity_done(self):
        for record in self.move_ids_without_package:
            if record.product_uom_qty < record.quantity_done:
                raise Warning("You can't transfer more than the Initial Demand!")
                # raise ValidationError(
                #     _('some product for this company/customer has no price list please create price list for them to continue'))


class CarProblemClass(models.Model):
    _name = 'car.issue'

    name = fields.Char('Issue',track_visibility='onchange')


class WorkerServiceClass(models.Model):
    _name = 'worker.service'
    _rec_name = 'product'

    product = fields.Many2one('product.product',string='Service',domain=[('service_ok','=',True)])
    worker = fields.Char('Worker')
    no_of_hours = fields.Float('Number Of Hours')

    service_inv = fields.Many2one('car.fix')
    account_id = fields.Many2one('account.account', string='Account', readonly=False,
                                 compute='compute_def_account',
                                 help="The income or expense account related to the selected product.")
    customer = fields.Many2one('res.partner',related='service_inv.customer')
    price_unit = fields.Float('Price/Hour',compute='check_product_company_priclist')

    @api.multi
    @api.depends('product', 'customer')
    def check_product_company_priclist(self):
        for rec in self:
            asd = rec.env['company.price_bridge'].search(
                [('customerr', '=', rec.customer.id), ('product', '=', rec.product.id)])
            if asd:
                rec.price_unit = asd.total
            # else:
            #  raise TypeError(_('this customer/company has no price list please create price list to continue.'))

    @api.multi
    @api.depends('product')
    def compute_def_account(self):
        for line in self:
            if line.product.property_account_income_id:
                line.account_id = line.product.property_account_income_id
            elif line.product.categ_id.property_account_income_categ_id:
                line.account_id = line.product.categ_id.property_account_income_categ_id
            elif line.product.categ_id.parent_id.property_account_income_categ_id:
                line.account_id = line.product.categ_id.parent_id.property_account_income_categ_id
            elif line.product.categ_id.parent_id.parent_id.property_account_income_categ_id:
                line.account_id = line.product.categ_id.parent_id.parent_id.property_account_income_categ_id

