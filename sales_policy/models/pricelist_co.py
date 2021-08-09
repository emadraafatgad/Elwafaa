from odoo import models, fields, api, exceptions, _
import datetime
# from  datetime import  datetime,date,timedelta

class CompanyPriceList(models.Model):
    _name = 'company.price'
    _rec_name = 'customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    customer=fields.Many2one('res.partner',string='Customer')
    date=fields.Date(string='Date',default=fields.Date.today(),store=True,copy=True)
    date2=fields.Date(string='Date',store=True,copy=True,track_visibility='onchange',compute='_compute_date_amount')
    payment_term=fields.Many2one('payement.method',string='Payment Terms')
    no_of_days= fields.Integer('Number of days',related='payment_term.no_of_days')
    categories = fields.Selection([('companies','Companies'),('individuals','Individuals'),('workshops','Workshops')],string='Categories')
    pricelist_table=fields.One2many('company.price_bridge','bridge_inverse_price')

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

    product=fields.Many2one('product.product',required=True)
    price = fields.Float(string='Price')
    price_percentage = fields.Float(string='Percentage')
    sign = fields.Char(string='%',default='%',readonly=True)
    total=fields.Float(string='Total',compute='_compute_final_amount')
    customerr=fields.Many2one('res.partner',string='Customer',related='bridge_inverse_price.customer')


    @api.one
    @api.depends('price', 'price_percentage')
    def _compute_final_amount(self):
        for rec in self:
            rec.total =rec.price+((rec.price_percentage/100)*rec.price)

    @api.multi
    @api.constrains('price')
    def _price_validation(self):
        for line in self:
            if (line.price) <  0.0:
                raise exceptions.ValidationError('price should be equal or greater than zero!')


    bridge_inverse_price=fields.Many2one('company.price')
