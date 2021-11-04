from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError


class MrpRequestClass(models.Model):
    _name = 'mrp.request'
    _rec_name = 'customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    customer = fields.Many2one('res.partner', string='Customer', track_visibility='onchange', required=True)
    product = fields.Many2one('product.product', string='Product', track_visibility='onchange', required=True)
    attachment = fields.Binary('Attachments', attachment=True, track_visibility='onchange')
    quantity = fields.Float(string='Quantity', track_visibility='onchange', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', readonly=True, track_visibility='onchange',
                                  related='product.uom_id')
    delivery_date = fields.Date(string='Delivery Date', default=fields.Date.today(), store=True, copy=True,
                                track_visibility='onchange')
    source = fields.Char(string='Source Origin', track_visibility='onchange')
    bom_template = fields.Many2one('temp.bom', string='Bill of Material', domain="[('product', '=', product)]",
                                   required=True)
    seq = fields.Char('Sequence')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('in_progress', "In Progress"),
        ('lock', "Locked"),
        ('cancel', "Cancelled"),
    ], default='draft')

    mrp_request_table = fields.One2many('mrp.request_bridge', 'bridge_inverse_mrp', track_visibility='onchange',
                                        store=True, copy=True, compute='create_bom_template_records')

    @api.model
    def create(self, vals):
        vals['seq'] = self.env['ir.sequence'].next_by_code('mrp_request_sequence')
        return super(MrpRequestClass, self).create(vals)

    @api.multi
    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity < 1:
                raise ValidationError(
                    _('quantity can not be less than 1'))
            # for line in self.mrp_request_table:
            #     if 0.0 >=  line.quantity:
            #         raise ValidationError(_('quantity can not be less than 1'))

    @api.one
    @api.depends('bom_template')
    def create_bom_template_records(self):
        if self.bom_template:
            l = []
            asd = self.env['temp.bom'].search([('name', '=', self.bom_template.name)])
            if asd:
                for rec in asd.lines:
                    l.append({
                        'product': rec.product.id,
                        'quantity': rec.quantity,
                        'operation': rec.operation.id,

                    })
                self.mrp_request_table = l

    mrb_order_id = fields.Many2one('mrp.order', string='Manufacturing Order',
                                   readonly=True, index=True, ondelete='restrict', copy=False,
                                   help="Link to the automatically generated Manufacturing Order.")

    @api.multi
    def action_confirm(self):
        order = self.env['mrp.order'].create({
            'customer': self.customer.id,
            'product': self.product.id,
            'quantity': self.quantity,
            'bill_of_materials': self.bom_template.id,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today(),
            'routing': self.bom_template.routing.id,
            'source': self.source,
        })
        for line in self.mrp_request_table:
            for l in order:
                l.write({
                    'transfer_lines': [(0, 0, {
                        'product': line.product.id,
                        'to_consume': line.total_quantity,
                        'operation': line.operation.id,
                        # 'date_start': fields.Datetime.now(),
                        # 'date_end': fields.Datetime.now(),

                    })]
                })
        vals = {
            'mrb_order_id': order.id,

        }
        self.write(vals)
        self.state = 'confirmed'

    @api.multi
    def action_lock(self):
        self.state = 'lock'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'


class MrpRequestBridgeBridge(models.Model):
    _name = 'mrp.request_bridge'
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', track_visibility='onchange', required=True)
    quantity = fields.Float(string='Quantity', track_visibility='onchange', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of measure', track_visibility='onchange',
                                  related='product.uom_id', readonly=True)
    total_quantity = fields.Float(string='Total Quantity', track_visibility='onchange',
                                  compute='compute_total_quantity_all')
    operation = fields.Many2one('mrp.operation', string='Operation')
    inverse_quantity = fields.Float(string='Inverse Quantity', related='bridge_inverse_mrp.quantity')

    bridge_inverse_mrp = fields.Many2one('mrp.request')

    @api.multi
    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity < 1:
                raise ValidationError(
                    _('quantity can not be less than 1'))

    @api.multi
    @api.depends('inverse_quantity', 'quantity')
    def compute_total_quantity_all(self):
        for rec in self:
            rec.total_quantity = rec.inverse_quantity * rec.quantity
