from odoo import models, fields, api, exceptions, _
import datetime
# from  datetime import  datetime,date,timedelta

class CompanyPriceList(models.Model):
    _name = 'company.price'
    _rec_name = 'customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    customer=fields.Many2one('res.partner',string='Customer',track_visibility='onchange')
    car = fields.Many2one('car.data', string='Car', domain="[('customer','=',customer)]",track_visibility='onchange',store=True, copy=True,)
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True)
    is_service = fields.Boolean('Is Service?')
    pricelist_temp=fields.Many2one('temp.price_list',string='Price List Template',track_visibility='onchange',domain="[('car_model','=',car_model)]")
    date=fields.Date(string='Date',default=fields.Date.today(),store=True,copy=True,track_visibility='onchange')
    date2=fields.Date(string='Date',store=True,copy=True,track_visibility='onchange',compute='_compute_date_amount')
    payment_term=fields.Many2one('payement.method',string='Payment Terms',track_visibility='onchange')
    no_of_days= fields.Integer('Number of days',related='payment_term.no_of_days')
    categories = fields.Selection([('companies','Companies'),('individuals','Individuals'),('workshops','Workshops')],string='Categories',track_visibility='onchange')
    pricelist_table=fields.One2many('company.price_bridge','bridge_inverse_price',track_visibility='onchange',store=True,copy=True)
    accessories_percentage= fields.Float(string='Accessories Percentage')
    steel_percentage= fields.Float(string='Steel Percentage')
    service_percentage= fields.Float(string='Service Percentage')
    company_category = fields.Selection([('a','A'),('b','B'),('c','C'),('d','D'),('competitive','Competitive')],string='Company Category',track_visibility='onchange',related='customer.company_category')

    @api.multi
    def action_filter(self):
        for rec in self.pricelist_table:
            asd = self.env['product.product'].search(
                [('name', '=', rec.product.name), ('car_model', '=', self.car_model.id)], limit=1)
            if asd:
                for m in asd:
                    #     if m.car_model ==self.car_model:
                    #         print(m.id)
                    rec.product = m.id
                    rec.car_model = self.car_model
            # if rec.car_model != self.car_model:
            #     rec.unlink()

    @api.one
    @api.depends('pricelist_temp')
    def create_price_template_records(self):
      if self.pricelist_temp:
          l=[]
          asd = self.env['temp.price_list'].search([('name', '=', self.pricelist_temp.name)])
          if asd:
              for rec in asd.temp_price:
                  l.append({'product':rec.product.id,
                            'price': rec.price,
                            # 'price_percentage': rec.price_percentage,
                            # 'sign':rec.sign,
                            'total':rec.total,
                            # 'car_type': rec.car_type,
                            'car_model': rec.car_model,

                  })
              self.pricelist_table = l
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
    @api.one
    @api.depends('no_of_days')
    def _compute_date_amount(self):
        for line in self:
            if line.no_of_days ==0:
                line.date2 =line.date
            else:
                planned = (datetime.datetime.strptime(str(line.date),'%Y-%m-%d') + datetime.timedelta(days=line.no_of_days)).strftime('%Y-%m-%d')
                line.date2 = planned
                line.date= line.date2
                # break
                # @api.multi
                # def _compute_days(self):
                #     d1=datetime.strptime(str(self.check_date),'%Y-%m-%d')
                #     self.will_collection= d1 + timedelta(days=10)


    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('update', "Updated"),

    ], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_update(self):
        self.state = 'update'



class CompanyPriceListBridge(models.Model):
    _name = 'company.price_bridge'

    product=fields.Many2one('product.product',required=True,track_visibility='onchange',domain="[('car_model','=',car_model)]")
    price = fields.Float(string='Price',track_visibility='onchange')
    price_percentage = fields.Float(string='Percentage',track_visibility='onchange')
    sign = fields.Char(string='%',default='%',readonly=True,track_visibility='onchange')
    total=fields.Float(string='Total',compute='_compute_final_amount',track_visibility='onchange')
    customerr=fields.Many2one('res.partner',string='Customer',related='bridge_inverse_price.customer')
    accessories_ok = fields.Boolean(string='Accessories',compute='_compute_booleans_tf')
    service_ok = fields.Boolean(string='Service',compute='_compute_booleans_tf')
    steel_ok = fields.Boolean(string='Steel',compute='_compute_booleans_tf')
    accessories_percentage = fields.Float(string='Accessories Percentage',related='bridge_inverse_price.accessories_percentage')
    steel_percentage = fields.Float(string='Steel Percentage',related='bridge_inverse_price.steel_percentage')
    service_percentage = fields.Float(string='Service Percentage',related='bridge_inverse_price.service_percentage')
    # car_type = fields.Many2one('car.data', string='Car', compute='cal_car_type_inv', store=True,copy=True)
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True,related='bridge_inverse_price.car_model')

    # @api.multi
    # @api.depends('product', 'bridge_inverse_price')
    # def cal_car_type_inv(self):
    #     for rec in self:
    #         # rec.car_type = rec.bridge_inverse_price.car
    #         rec.car_model = rec.bridge_inverse_price.car_model

    @api.one
    @api.depends('product')
    def _compute_booleans_tf(self):
        for rec in self:
            if rec.product.accessories_ok == True and rec.product.service_ok ==True and rec.product.steel_ok ==True:
                rec.accessories_ok = True
                rec.service_ok = True
                rec.steel_ok = True
            elif rec.product.accessories_ok == True and rec.product.steel_ok ==True :
                rec.accessories_ok = True
                rec.steel_ok = True
            elif rec.product.accessories_ok == True and rec.product.service_ok ==True :
                rec.accessories_ok = True
                rec.service_ok = True

            elif rec.product.steel_ok == True and rec.product.service_ok ==True :
                rec.steel_ok = True
                rec.service_ok = True
            elif rec.product.accessories_ok ==True:
                rec.accessories_ok = True
            elif rec.product.service_ok ==True:
                rec.service_ok = True
            elif rec.product.steel_ok ==True:
                rec.steel_ok = True
    @api.one
    @api.depends('price', 'price_percentage','service_ok','steel_ok','accessories_ok','accessories_percentage','steel_percentage','service_percentage')
    def _compute_final_amount(self):
        for rec in self:
            if rec.service_ok==True and rec.steel_ok==True and rec.accessories_ok==True:
                rec.total = rec.price + ((rec.accessories_percentage / 100) * rec.price) +((rec.steel_percentage / 100) * rec.price) +((rec.service_percentage / 100) * rec.price) + ((rec.price_percentage / 100) * rec.price)
            elif rec.service_ok == True and rec.steel_ok == True :
                rec.total = rec.price  + ((rec.steel_percentage / 100) * rec.price) + ((rec.service_percentage / 100) * rec.price) + ((rec.price_percentage / 100) * rec.price)
            elif rec.service_ok == True and rec.accessories_ok == True :
                rec.total = rec.price  + ((rec.accessories_percentage / 100) * rec.price) + ((rec.service_percentage / 100) * rec.price) + ((rec.price_percentage / 100) * rec.price)
            elif rec.steel_ok == True and rec.accessories_ok == True :
                rec.total = rec.price  + ((rec.accessories_percentage / 100) * rec.price) + ((rec.steel_percentage / 100) * rec.price) + ((rec.price_percentage / 100) * rec.price)
            elif rec.accessories_ok == True :
                rec.total = rec.price  + ((rec.accessories_percentage / 100) * rec.price) +((rec.price_percentage / 100) * rec.price)
            elif rec.steel_ok == True :
                rec.total = rec.price  + ((rec.steel_percentage / 100) * rec.price) +((rec.price_percentage / 100) * rec.price)
            elif rec.service_ok == True :
                rec.total = rec.price  + ((rec.service_percentage / 100) * rec.price) +((rec.price_percentage / 100) * rec.price)
            else:
             rec.total =rec.price+((rec.price_percentage/100)*rec.price)

    @api.multi
    @api.constrains('price')
    def _price_validation(self):
        for line in self:
            if (line.price) <  0.0:
                raise exceptions.ValidationError('price should be equal or greater than zero!')


    bridge_inverse_price=fields.Many2one('company.price')


class CompanyPriceListTemplate(models.Model):
    _name = 'temp.price_list'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Template',track_visibility='onchange',store=True,copy=True)
    # car = fields.Many2one('car.data', string='Car',track_visibility='onchange')
    is_service = fields.Boolean('Is Service?')
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True)
    company_category = fields.Selection([('a','A'),('b','B'),('c','C'),('d','D'),('competitive','Competitive')],string='Company Category',track_visibility='onchange')


    temp_price = fields.One2many('price_list.template_bridge','bridge_inverse_price_temp',string='Lines',store=True,copy=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique!'),
    ]

    @api.multi
    def action_filter(self):
        for rec in self.temp_price:
            asd = self.env['product.product'].search(
                [('name', '=', rec.product.name), ('car_model', '=', self.car_model.id)], limit=1)
            if asd:
                for m in asd:
                    #     if m.car_model ==self.car_model:
                    #         print(m.id)
                    rec.product = m.id
                    rec.car_model = self.car_model
            # if rec.car_model != self.car_model:
            #     rec.unlink()





class CompanyPriceListtTemplateBridge(models.Model):
    _name = 'price_list.template_bridge'
    _rec_name = 'product'

    product=fields.Many2one('product.product',required=True,track_visibility='onchange',store=True,copy=True, domain = "[('car_model','=',car_model)]")

    price = fields.Float(string='Price',track_visibility='onchange',store=True,copy=True)
    # price_percentage = fields.Float(string='Percentage',track_visibility='onchange',store=True,copy=True)
    # sign = fields.Char(string='%',default='%',readonly=True,track_visibility='onchange',store=True,copy=True)
    total=fields.Float(string='Total',compute='_compute_final_amount',track_visibility='onchange',store=True,copy=True)
    # customerr=fields.Many2one('res.partner',string='Customer',related='bridge_inverse_price.customer')

    car_type = fields.Many2one('car.data', string='Car', compute='cal_type_inv', store=True)
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True,related='bridge_inverse_price_temp.car_model')

    # @api.multi
    # @api.onchange('product', 'bridge_inverse_price_temp')
    # def cal_type_inv(self):
    #     for rec in self:
    #         # rec.car_type = rec.bridge_inverse_price_temp.car
    #         rec.car_model = rec.bridge_inverse_price_temp.car_model


    @api.one
    @api.depends('price')
    def _compute_final_amount(self):
        for rec in self:
            # rec.total =rec.price+((rec.price_percentage/100)*rec.price)
            rec.total = rec.price

    @api.multi
    @api.constrains('price')
    def _price_validation(self):
        for line in self:
            if (line.price) <  0.0:
                raise exceptions.ValidationError('price should be equal or greater than zero!')


    bridge_inverse_price_temp=fields.Many2one('temp.price_list')