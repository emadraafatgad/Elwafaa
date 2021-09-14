from odoo import models, fields, api, exceptions, _

class MrpRequestClass(models.Model):
    _name = 'mrp.request'
    _rec_name = 'customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    customer=fields.Many2one('res.partner',string='Customer',track_visibility='onchange')
    product=fields.Many2one('product.product',string='Product',track_visibility='onchange')
    attachment = fields.Binary('Attachments', attachment=True,track_visibility='onchange')
    quantity = fields.Float(string='Quantity', track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange')
    delivery_date=fields.Date(string='Delivery Date',default=fields.Date.today(),store=True,copy=True,track_visibility='onchange')
    source = fields.Char(string='Source Origin', track_visibility='onchange')
    bom_template = fields.Many2one('temp.bom',string='Bill of Material')


    mrp_request_table=fields.One2many('mrp.request_bridge','bridge_inverse_mrp',track_visibility='onchange',store=True,copy=True)

    # @api.one
    # @api.depends('pricelist_temp')
    # def create_price_template_records(self):
    #   if self.pricelist_temp:
    #       l=[]
    #       asd = self.env['temp.price_list'].search([('name', '=', self.pricelist_temp.name)])
    #       if asd:
    #           for rec in asd.temp_price:
    #               l.append({'product':rec.product.id,
    #                         'price': rec.price,
    #                         'price_percentage': rec.price_percentage,
    #                         'sign':rec.sign,
    #                         'total':rec.total,
    #                         'car_type': rec.car_type,
    #                         'car_model': rec.car_model,
    #
    #               })
    #           self.pricelist_table = l
    #       # for line in self.emp_comparison:
    #       #   for l in asd:
    #       #       l.write({
    #       #           'emp_comparison': [(0, 0, {
    #       #               'required_program': line.required_program.id,
    #       #               'emp_name': line.emp_name.id,
    #       #               'emp_code': line.emp_no,
    #       #               'ommat': line.ommat,
    #       #           })]
    #       #       })
    # @api.one
    # @api.depends('no_of_days')
    # def _compute_date_amount(self):
    #     for line in self:
    #         if line.no_of_days ==0:
    #             line.date2 =line.date
    #         else:
    #             planned = (datetime.datetime.strptime(str(line.date),'%Y-%m-%d') + datetime.timedelta(days=line.no_of_days)).strftime('%Y-%m-%d')
    #             line.date2 = planned
    #             line.date= line.date2
    #             # break
    #             # @api.multi
    #             # def _compute_days(self):
    #             #     d1=datetime.strptime(str(self.check_date),'%Y-%m-%d')
    #             #     self.will_collection= d1 + timedelta(days=10)


    # state = fields.Selection([
    #     ('draft', "Draft"),
    #     ('confirmed', "Confirmed"),
    #     ('update', "Updated"),
    #
    # ], default='draft')

    # @api.multi
    # def action_draft(self):
    #     self.state = 'draft'
    #
    # @api.multi
    # def action_confirm(self):
    #     self.state = 'confirmed'
    #
    # @api.multi
    # def action_update(self):
    #     self.state = 'update'



class MrpRequestBridgeBridge(models.Model):
    _name = 'mrp.request_bridge'
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product',track_visibility='onchange')
    quantity = fields.Float(string='Quantity', track_visibility='onchange')
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange')
    total_quantity = fields.Float(string='Total Quantity', track_visibility='onchange',compute='compute_total_quantity_all')
    inverse_quantity = fields.Float(string='Inverse Quantity',related='bridge_inverse_mrp.quantity')

    bridge_inverse_mrp = fields.Many2one('mrp.request')


    @api.multi
    @api.depends('inverse_quantity', 'quantity')
    def compute_total_quantity_all(self):
        for rec in self:
            rec.total_quantity = rec.inverse_quantity * rec.quantity

