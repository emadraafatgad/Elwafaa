from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountInvoiceClass(models.Model):
    _inherit="account.invoice"

    total_accessories = fields.Float(string='Total Accessories',track_visibility='onchange',compute='action_compute_total_accessories')
    total_service = fields.Float(string='Total Service',track_visibility='onchange',compute='action_compute_total_accessories')
    total_steel = fields.Float(string='Total Steel',track_visibility='onchange',compute='action_compute_total_accessories')
    total_accessories_qty = fields.Float(string='Total Accessories Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    total_service_qty = fields.Float(string='Total Service Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    total_steel_qty = fields.Float(string='Total Steel Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    mm = fields.Selection([('taxed_cash','Taxed Cash'),('Untaxed_cash','Untaxed Cash'),('taxed_accrual','Taxed Accrual'),('untaxed_accrual','Untaxed Accrual')],string='Work Method',default='taxed_cash',related='partner_id.work_method',track_visibility='onchange')

    car = fields.Many2one('car.data', string='Car', track_visibility='onchange',domain="[('customer','=',partner_id)]",required=True)
    plate_number = fields.Char(string='Plate Number', track_visibility='onchange',related='car.plate_number')
    chassis_number = fields.Char(string='Chassis Number',track_visibility='onchange',related='car.chassis_number')
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True,domain="[('car_type','=',car)]",required=True)
    driver_name = fields.Char(string='Driver Name')
    supervisor_name = fields.Char('اسم المشرف', track_visibility='onchange')
    technician_name = fields.Char('اسم الفني ', track_visibility='onchange')
    invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
                                       oldname='invoice_line',
                                       states={'draft,wait': [('readonly', False)]}, copy=True)
    tax_line_ids = fields.One2many('account.invoice.tax', 'invoice_id', string='Tax Lines', oldname='tax_line',
                                  store=True, states={'draft,wait': [('readonly', False)]}, copy=True)

    total_other_tax = fields.Float(string='Total other Taxes', track_visibility='onchange',compute='total_other_taxes')
    # total_after_tax = fields.Float(string='Total after Taxes', track_visibility='onchange',compute='total_other_taxes')

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: inv.state not in ('draft','wait')):
            raise UserError(_("Invoice must be in draft or waiting state in order to validate it."))
        if to_open_invoices.filtered(
                lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(
                _("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(
                _('No account was found to create the invoice, be sure you have installed a chart of account.'))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

    @api.multi
    @api.depends('tax_line_ids')
    def total_other_taxes(self):
     for line in self:
      for rec in line.tax_line_ids:
           line.total_other_tax =line.total_other_tax +rec.amount_total


    state = fields.Selection([
        ('draft', 'Draft'),
        ('wait', 'Waiting'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'In Payment' status is used when payments have been registered for the entirety of the invoice in a journal configured to post entries at bank reconciliation only, and some of them haven't been reconciled with a bank statement line yet.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

    @api.multi
    @api.depends('invoice_line_ids')
    def action_compute_total_accessories(self):
      for rec in self:
        for line in rec.invoice_line_ids:
          if line.product_id. accessories_ok == True:
            rec.total_accessories += line.price_subtotal
            rec.total_accessories_qty += line.quantity
          elif line.product_id.service_ok == True:
            rec.total_service += line.price_subtotal
            rec.total_service_qty += line.quantity
          elif line.product_id.steel_ok == True:
              rec.total_steel += line.price_subtotal
              rec.total_steel_qty += line.quantity



    # @api.multi
    # def action_accept(self):
    #     self.state_workflow = 'accept'


class AccountInvoiceTaxaClass(models.Model):
    _inherit="account.invoice.tax"

    amount_total = fields.Monetary(string="Amount Total", store=True,compute='_compute_amount_total')
    name = fields.Char(string='Tax Description', required=True,store=True)



# class ProductProudctWafaClass(models.Model):
#     _inherit="product.product"
#
#     accessories_ok = fields.Boolean(string='Accessories')
#     service_ok = fields.Boolean(string='Service')
#     steel_ok = fields.Boolean(string='Steel')




class ProducttemplateWafaClass(models.Model):
    _inherit="product.template"

    accessories_ok = fields.Boolean(string='Accessories',track_visibility='onchange')
    service_ok = fields.Boolean(string='Service',track_visibility='onchange')
    steel_ok = fields.Boolean(string='Steel',track_visibility='onchange')
    car_model = fields.Many2one('model.car',string='Car Model',store=True,copy=True)
    car_type = fields.Many2one('car.type', string='Car',track_visibility='onchange',related='car_model.car_type')


class ProductProductWafaClass(models.Model):
    _inherit="product.product"

    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True)
    car_type = fields.Many2one('car.type', string='Car', track_visibility='onchange', related='car_model.car_type')


class AccountInvoiceLineInheritWafa(models.Model):
    _inherit = 'account.invoice.line'

    product_id = fields.Many2one('product.product', string='Product',ondelete='restrict', index=True,domain="[('car_model','=',car_model)]")
    method_pay = fields.Selection([('taxed_cash','Taxed Cash'),('Untaxed_cash','Untaxed Cash'),('taxed_accrual','Taxed Accrual'),('untaxed_accrual','Untaxed Accrual')],string='Work Method',default='taxed_cash',related='invoice_id.mm',track_visibility='onchange')
    price_unit = fields.Float(string='Unit Price', required=True, compute='_onchange_uom_id')
    car_type = fields.Many2one('car.data', string='Car', compute='cal_type_car', store=True)
    car_model = fields.Many2one('model.car', string='Car Model', store=True, copy=True,compute='cal_type_car')


    @api.multi
    @api.depends('product_id', 'invoice_id')
    def cal_type_car(self):
        for rec in self:
            rec.car_type = rec.invoice_id.car
            rec.car_model = rec.invoice_id.car_model
    @api.multi
    @api.onchange('uom_id', 'product_id','car_model','car_type')
    def _onchange_uom_id(self):
        for rec in self:
            asd = rec.env['company.price_bridge'].search(
                [('customerr', '=', rec.partner_id.id), ('product', '=', rec.product_id.id),('car_model', '=', rec.car_model.id), ('car_type', '=', rec.car_type.id)])
            if asd:
              for line in asd:
                rec.price_unit = line.total
        # warning = {}
        result = {}
        # if not self.uom_id:
        #     self.price_unit = 0.0

        # if self.product_id and self.uom_id:
        #     self._set_taxes()
        #     self.price_unit = self.product_id.uom_id._compute_price(self.price_unit, self.uom_id)

        if rec.product_id.uom_id.category_id.id != rec.uom_id.category_id.id:
            warning = {
                'title': _('Warning!'),
                'message': _(
                    'The selected unit of measure has to be in the same category as the product unit of measure.'),
            }
            rec.uom_id = rec.product_id.uom_id.id
            if warning:
                result['warning'] = warning
        return result

    # @api.multi
    # @api.depends('product_id')
    # def price_unit_calc(self):
    #     for rec in self:
    #         asd = rec.env['company.price_bridge'].search(
    #             [('customerr', '=', rec.partner_id.id), ('product', '=', rec.product_id.id)])
    #         if asd:
    #             rec.price_unit = asd.total



class SaleAdvancePaymentInvInheritWafa(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = order.fiscal_position_id.map_account(
                self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id).id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        del context
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
        else:
            tax_ids = taxes.ids

        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'account_analytic_id': order.analytic_account_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'company_id': order.company_id.id,
            'comment': order.note,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)

        invoice.state = 'wait'
        return invoice