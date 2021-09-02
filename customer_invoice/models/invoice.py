from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class AccountInvoiceClass(models.Model):
    _inherit="account.invoice"

    total_accessories = fields.Float(string='Total Accessories',track_visibility='onchange',compute='action_compute_total_accessories')
    total_service = fields.Float(string='Total Service',track_visibility='onchange',compute='action_compute_total_accessories')
    total_steel = fields.Float(string='Total Steel',track_visibility='onchange',compute='action_compute_total_accessories')
    total_accessories_qty = fields.Float(string='Total Accessories Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    total_service_qty = fields.Float(string='Total Service Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    total_steel_qty = fields.Float(string='Total Steel Quantities', track_visibility='onchange',compute='action_compute_total_accessories')
    mm = fields.Selection([('taxed_cash','Taxed Cash'),('Untaxed_cash','Untaxed Cash'),('taxed_accrual','Taxed Accrual'),('untaxed_accrual','Untaxed Accrual')],string='Work Method',default='taxed_cash',related='partner_id.work_method',track_visibility='onchange')

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





class AccountInvoiceLineInheritWafa(models.Model):
    _inherit = 'account.invoice.line'

    method_pay = fields.Selection([('taxed_cash','Taxed Cash'),('Untaxed_cash','Untaxed Cash'),('taxed_accrual','Taxed Accrual'),('untaxed_accrual','Untaxed Accrual')],string='Work Method',default='taxed_cash',related='invoice_id.mm',track_visibility='onchange')




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