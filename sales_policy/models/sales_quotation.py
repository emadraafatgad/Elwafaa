import dp as dp

from odoo import models, fields, api, exceptions, _

class SalesQuotationLineInherit(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('product_id', 'order_id')
    def cal_customer_relation(self):
        for rec in self:
            rec.customer = rec.order_id.partner_id
    customer=fields.Many2one('res.partner',string='Customer',compute='cal_customer_relation',copy=True,store=True)
    car_type = fields.Many2one('car.data', string='Car',domain="[('customer','=',customer)]", store=True)
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True, domain="[('car_type','=',car_type)]")

    price_unit = fields.Float('Unit Price', required=True,readonly=True, compute='product_uom_change')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = self.get_sale_order_line_multiline_description_sale(product)

        vals.update(name=name)

        self._compute_tax_id()

        # if self.order_id.pricelist_id and self.order_id.partner_id:
        #     vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
        #         self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        # self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

    @api.multi
    @api.depends('product_id','customer','car_model','car_type')
    def product_uom_change(self):
      for rec in self:
        asd = rec.env['company.price_bridge'].search([('customerr', '=', rec.customer.id),('product', '=', rec.product_id.id),('car_model', '=', rec.car_model.id), ('car_type', '=', rec.car_type.id)])
        if asd:
          rec.price_unit=asd.total
        # else:
        #
        #     if not self.product_uom or not self.product_id:
        #         self.price_unit = 0.0
        #         return
        #     if self.order_id.pricelist_id and self.order_id.partner_id:
        #         product = self.product_id.with_context(
        #             lang=self.order_id.partner_id.lang,
        #             partner=self.order_id.partner_id,
        #             quantity=self.product_uom_qty,
        #             date=self.order_id.date_order,
        #             pricelist=self.order_id.pricelist_id.id,
        #             uom=self.product_uom.id,
        #             fiscal_position=self.env.context.get('fiscal_position')
        #         )
        #         self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
        #                                                                                   product.taxes_id, self.tax_id,
        #                                                                                   self.company_id)
        #     #


class SalesQuotationInherit(models.Model):
    _inherit = 'sale.order'


    cars = fields.Many2many('car.data',string='Cars',domain="[('customer','=',partner_id)]")
    total_am_due = fields.Float( string='Previous Amount Due',default=0,compute='_amount_due_credit_limit_validation')
    total_credit = fields.Float(string='Previous Amount Due', default=0,compute='_amount_due_credit_limit_validation')

    @api.multi
    @api.depends('amount_total','partner_id')
    def _amount_due_credit_limit_validation(self):
     for line in self:
        asd = line.env['account.invoice'].search([('partner_id', '=', line.partner_id.id)])
        if asd:
            for rec in asd:
                print('hello'+str(rec.residual))
                line.total_am_due += rec.residual
                line.total_credit =line.total_am_due + line.amount_total

        if line.total_credit > line.partner_id.credit_limit:
                raise exceptions.ValidationError('You will exceed your credit limit of amount due!')




# class AccountInvoiceLineInheritKKLL(models.Model):
#     _inherit = 'account.invoice.line'

