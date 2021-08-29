from odoo import models, fields, api, exceptions, _

class AccountInvoiceClass(models.Model):
    _inherit="account.invoice"

    total_accessories = fields.Float(string='Total Accessories',track_visibility='onchange',compute='action_compute_total_accessories')
    total_service = fields.Float(string='Total Service',track_visibility='onchange',compute='action_compute_total_accessories')
    total_steel = fields.Float(string='Total Steel',track_visibility='onchange',compute='action_compute_total_accessories')
    total_accessories_qty = fields.Float(string='Total Accessories Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    total_service_qty = fields.Float(string='Total Service Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    total_steel_qty = fields.Float(string='Total Steel Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    mm = fields.Selection([('taxed_cash','Taxed Cash'),('Untaxed_cash','Untaxed Cash'),('taxed_accrual','Taxed Accrual'),('untaxed_accrual','Untaxed Accrual')],string='Work Method',default='taxed_cash',related='partner_id.work_method',track_visibility='onchange')



    @api.multi
    @api.depends('invoice_line_ids')
    def action_compute_total_accessories(self):
        for line in self.invoice_line_ids:
          if line.product_id. accessories_ok == True:
            self.total_accessories += line.price_subtotal
            self.total_accessories_qty += line.quantity
          elif line.product_id.service_ok == True:
            self.total_service += line.price_subtotal
            self.total_service_qty += line.quantity
          elif line.product_id.steel_ok == True:
              self.total_steel += line.price_subtotal
              self.total_steel_qty += line.quantity

    # @api.multi
    # def action_accept(self):
    #     self.state_workflow = 'accept'

# class ProductProudctWafaClass(models.Model):
#     _inherit="product.product"
#
#     accessories_ok = fields.Boolean(string='Accessories')
#     service_ok = fields.Boolean(string='Service')
#     steel_ok = fields.Boolean(string='Steel')




class ProducttemplateWafaClass(models.Model):
    _inherit="product.template"

    accessories_ok = fields.Boolean(string='Accessories')
    service_ok = fields.Boolean(string='Service')
    steel_ok = fields.Boolean(string='Steel')
