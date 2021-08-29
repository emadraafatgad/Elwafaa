from time import strftime

from odoo import models, fields, api, exceptions, _
import datetime

class PricelistInfoClass(models.Model):
    _name = 'pricelist.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'company'

    company = fields.Char(string='Company Name',store=True,copy=True,track_visibility='onchange')
    state = fields.Selection([
        ('draft', "Draft"),
        ('request', "Request Sent"),
        ('approve', "Approved"),('received', "Car Received"), ], default='draft',track_visibility='onchange')

    sending_date =fields.Date(string='Sending Date',readonly=True,track_visibility='onchange')
    approve_date = fields.Date(string='Approve Date',track_visibility='onchange')
    end_date = fields.Date(string='Final Date',readonly=True,track_visibility='onchange')
    sales_person = fields.Many2one('res.users',string='SalesPerson',track_visibility='onchange', default=lambda self: self.env.user)
    pricelist = fields.One2many('price.offer','inverse_price_offer',string='Price List',track_visibility='onchange')
    mail = fields.Char('Mail',related='sales_person.login')
    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_receive(self):
        self.state = 'received'



    @api.multi
    def action_request(self):
        self.state = 'request'
        self.sending_date = fields.date.today()

    @api.multi
    def action_approve(self):
        self.state = 'approve'
        # self.approve_date = fields.date.today()
        planned = (datetime.datetime.strptime(str(self.approve_date), '%Y-%m-%d') + datetime.timedelta(
            days=14)).strftime('%Y-%m-%d')
        self.end_date =planned


    def check_for_incomplete_customer_leads(self):
        res = self.env['pricelist.info'].search([('end_date', '<', fields.date.today())])
        if res:
            for rec in res:
                if rec.state != 'received':

                    email_template = self.env.ref('company_sales_system.lead_dates_email')
                    # template = self.env['mail.template'].browse(email_template)
                    email_template.send_mail(rec.id, force_send=True)



                # if email_template:
                #     email_template.send_mail(rec.employee_id.work_email, force_send=True)
                # mail_template = rec.env['mail.template'].browse(template_id)
                # mail_template.write({'email_to': rec.hhh})
                #
                # # this will trigger the mail
                # if mail_template:
                #     mail_template.send_mail(self.id, force_send=True, raise_exception=True)


class PriceListBridgeOffer(models.Model):
    _name = 'price.offer'

    product=fields.Many2one('product.product',required=True)
    price = fields.Float(string='Price')
    price_percentage = fields.Float(string='Percentage')
    sign = fields.Char(string='%',default='%',readonly=True)
    total=fields.Float(string='Total',compute='_compute_final_amount')


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


    inverse_price_offer=fields.Many2one('pricelist.info')