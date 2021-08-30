from odoo import models, fields, api, exceptions, _

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    purchase_order_no = fields.Many2one('purchase.order',string='Purchase request Number',track_visibility='onchange')
    vendor_bill_no = fields.Many2one('account.invoice',string='Vendor Bill Number',track_visibility='onchange')







