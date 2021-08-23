from odoo import models, fields, api, exceptions, _

class ResPartnerModify(models.Model):
    _inherit = 'res.partner'

    categories = fields.Selection([('company','Companies'),('individuals','Individuals'),('workshops','Workshops')],string='Categories',required=True,default='company')
    company_activity=fields.Many2one('company.activity',string='Company Activity')
    company_category = fields.Selection([('a','A'),('b','B'),('c','C'),('d','D'),('competitive','Competitive')],string='Company Category')
    movement_responsible_name =fields.Char('Movement Responsible Name')
    movement_responsible_phone = fields.Char('Movement Responsible Phone')
    accounting_manager_name = fields.Char('Accounting Manager Name')
    accounting_manager_phone = fields.Char('Accounting Manager Phone')
    purchase_responsible_name = fields.Char('Purchase Responsible Name')
    purchase_responsible_phone = fields.Char('Purchase Responsible Phone')
    owner_name = fields.Char('Owner Name')
    owner_phone = fields.Char('Owner Phone')
    cars_no = fields.Char('Number of Cars')
    car_type = fields.Many2one('car.type',string='Car Type')
    salesperson = fields.Char('Salesperson')
    dealing_way = fields.Selection([('work_order','Work Order'),('phone_call','Phone call'),('mail','E-mail')],string='Dealing Way')
    payment_method = fields.Many2one('payement.method',string='Payment Method')
    work_method = fields.Selection([('tax_invoice','Tax Invoice'),('statement','Statement'),('cash','Cash'),('later','Later')],string='Work Method')
    Competitor_companies= fields.Many2one('competitive.company',string='Competitor Companies')

    previous_deal = fields.Char('Previous Deal')

    area=fields.Many2one('area.data',string='Area')
    used_paper_type=fields.Char('Used Paper Type')
    best_price_for_customer=fields.Float('Best Price For Customer')
    average_customer_consumption = fields.Char('Average Customer Consumption')
    cars= fields.One2many('car.data','customer',string='Cars')


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