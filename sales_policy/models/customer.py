from odoo import models, fields, api, exceptions, _

class ResPartnerModify(models.Model):
    _inherit = 'res.partner'

    categories = fields.Selection([('company','Companies'),('individuals','Individuals'),('workshops','Workshops')],string='Categories',required=True,default='company',track_visibility='onchange')
    company_activity=fields.Many2one('company.activity',string='Company Activity')
    company_category = fields.Selection([('a','A'),('b','B'),('c','C'),('d','D'),('competitive','Competitive')],string='Company Category',track_visibility='onchange')
    movement_responsible_name =fields.Char('Movement Responsible Name',track_visibility='onchange')
    movement_responsible_phone = fields.Char('Movement Responsible Phone',track_visibility='onchange')
    accounting_manager_name = fields.Char('Accounting Manager Name',track_visibility='onchange')
    accounting_manager_phone = fields.Char('Accounting Manager Phone',track_visibility='onchange')
    purchase_responsible_name = fields.Char('Purchase Responsible Name',track_visibility='onchange')
    purchase_responsible_phone = fields.Char('Purchase Responsible Phone',track_visibility='onchange')
    owner_name = fields.Char('Owner Name',track_visibility='onchange')
    owner_phone = fields.Char('Owner Phone',track_visibility='onchange')
    cars_no = fields.Char('Number of Cars',track_visibility='onchange')
    car_type = fields.Many2many('car.type',string='Car Type',track_visibility='onchange')
    salesperson = fields.Char('Salesperson',track_visibility='onchange')
    dealing_way = fields.Selection([('work_order','Work Order'),('phone_call','Phone call'),('mail','E-mail')],string='Dealing Way',track_visibility='onchange')
    payment_method = fields.Many2one('payement.method',string='Payment Method')
    work_method = fields.Selection([('taxed_cash','Taxed Cash'),('Untaxed_cash','Untaxed Cash'),('taxed_accrual','Taxed Accrual'),('untaxed_accrual','Untaxed Accrual')],string='Work Method',default='taxed_cash',track_visibility='onchange')
    attachment = fields.Binary('Attachments', attachment=True,track_visibility='onchange')
    # attachment = fields.Many2many("ir.attachment",string='Upload Your Files',width='100%',length='100%',required=True)

    Competitor_companies= fields.Many2one('competitive.company',string='Competitor Companies',track_visibility='onchange')

    previous_deal = fields.Char('Previous Deal',track_visibility='onchange')

    area=fields.Many2one('area.data',string='Area',track_visibility='onchange')
    used_paper_type=fields.Char('Used Paper Type',track_visibility='onchange')
    best_price_for_customer=fields.Float('Best Price For Customer',track_visibility='onchange')
    average_customer_consumption = fields.Char('Average Customer Consumption',track_visibility='onchange')
    cars= fields.One2many('car.data','customer',string='Cars',track_visibility='onchange')
    fix_cars = fields.One2many('car.fix', 'customer', string='Fixing Cars',track_visibility='onchange')

    credit_limit = fields.Float(string='حد الائتمان')
    customer_evaluation = fields.Selection([('bad','Bad'),('good','Good'),('very_good','Very Good')],string='Customer Evaluation',default='good',track_visibility='onchange')



class CompanyActivityClass(models.Model):
    _name = 'company.activity'

    name=fields.Char(string='Activity')


class PayementMethodClass(models.Model):
    _name = 'payement.method'
    _rec_name = 'payment_method'

    # payment_method = fields.Selection([('cash','Cash'),('weekly','Weekly'),('monthly','Monthly'),('45days','45 Days')],string='Payment Method')
    payment_method = fields.Char(string='Payment Method')
    no_of_days= fields.Integer('Number of days')

    @api.multi
    @api.constrains('no_of_days')
    def _no_of_days_validation(self):
        for line in self:
            if (line.no_of_days) < 0.0:
                raise exceptions.ValidationError('Number of days should be equal or greater than zero!')

class CompitiorCompaniesClass(models.Model):
    _name = 'competitive.company'

    name= fields.Char('Name')
