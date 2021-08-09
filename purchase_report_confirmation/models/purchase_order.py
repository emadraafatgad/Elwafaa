from odoo import models, fields, api, exceptions, _

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    printer_name = fields.Many2one('res.users', string='User Name',
                                                  default=lambda self: self.env.uid, readonly=True)
    financial_manager_confirmation = fields.Many2one('res.users', string='Approving Financial Manager', readonly=True)

    f_m_confirmation_date = fields.Datetime(readonly=True,string='Financial Manager Approval Date',
                                            default=lambda self: fields.Datetime.now())

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
                self.f_m_confirmation_date =fields.Datetime.now()
                qq =  self.env.user
                self.financial_manager_confirmation =qq
                print(self.financial_manager_confirmation)

            else:
                order.write({'state': 'to approve'})
                self.f_m_confirmation_date = fields.Datetime.now()
                qq =  self.env.user
                self.financial_manager_confirmation = qq
                print(self.financial_manager_confirmation)
        return True

    # customer=fields.Many2one('res.partner',string='Customer',related='order_id.partner_id')
    # price_unit = fields.Float('Unit Price', required=True,readonly=True, compute='product_uom_change')
    #
    # @api.multi
    # @api.onchange('product_id')
    # def product_id_change(self):
    #     if not self.product_id:
    #         return {'domain': {'product_uom': []}}
    #
    #     # remove the is_custom values that don't belong to this template
    #     for pacv in self.product_custom_attribute_value_ids:
    #         if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
    #             self.product_custom_attribute_value_ids -= pacv
    #
    #     # remove the no_variant attributes that don't belong to this template
    #     for ptav in self.product_no_variant_attribute_value_ids:
    #         if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
    #             self.product_no_variant_attribute_value_ids -= ptav
    #
    #     vals = {}
    #     domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
    #     if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
    #         vals['product_uom'] = self.product_id.uom_id
    #         vals['product_uom_qty'] = self.product_uom_qty or 1.0
    #
    #     product = self.product_id.with_context(
    #         lang=self.order_id.partner_id.lang,
    #         partner=self.order_id.partner_id,
    #         quantity=vals.get('product_uom_qty') or self.product_uom_qty,
    #         date=self.order_id.date_order,
    #         pricelist=self.order_id.pricelist_id.id,
    #         uom=self.product_uom.id
    #     )
    #
    #     result = {'domain': domain}
    #
    #     name = self.get_sale_order_line_multiline_description_sale(product)
    #
    #     vals.update(name=name)
    #
    #     self._compute_tax_id()
    #
    #     # if self.order_id.pricelist_id and self.order_id.partner_id:
    #     #     vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
    #     #         self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
    #     # self.update(vals)
    #
    #     title = False
    #     message = False
    #     warning = {}
    #     if product.sale_line_warn != 'no-message':
    #         title = _("Warning for %s") % product.name
    #         message = product.sale_line_warn_msg
    #         warning['title'] = title
    #         warning['message'] = message
    #         result = {'warning': warning}
    #         if product.sale_line_warn == 'block':
    #             self.product_id = False
    #
    #     return result
    #
    # @api.multi
    # @api.depends('product_id','customer')
    # def product_uom_change(self):
    #   for rec in self:
    #     asd = rec.env['company.price_bridge'].search([('customerr', '=', rec.customer.id),('product', '=', rec.product_id.id)])
    #     if asd:
    #       rec.price_unit=asd.total
    #     # else:
    #     #
    #     #     if not self.product_uom or not self.product_id:
    #     #         self.price_unit = 0.0
    #     #         return
    #     #     if self.order_id.pricelist_id and self.order_id.partner_id:
    #     #         product = self.product_id.with_context(
    #     #             lang=self.order_id.partner_id.lang,
    #     #             partner=self.order_id.partner_id,
    #     #             quantity=self.product_uom_qty,
    #     #             date=self.order_id.date_order,
    #     #             pricelist=self.order_id.pricelist_id.id,
    #     #             uom=self.product_uom.id,
    #     #             fiscal_position=self.env.context.get('fiscal_position')
    #     #         )
    #     #         self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
    #     #                                                                                   product.taxes_id, self.tax_id,
    #     #                                                                                   self.company_id)
    #     #     #
    #
