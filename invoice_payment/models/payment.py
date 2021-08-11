from odoo import models, fields, api, exceptions, _

class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    receiver_name = fields.Char(string=' Receiver Name')
    national_id = fields.Char(string='National ID')
    collection_representative =fields.Char(string='Collection Representative')
    amount_for = fields.Char(string='Amount Reason')

    # realty = fields.Char(string='Block Number')
    main_street = fields.Char(string='Main Street',related='partner_id.street')
    sub_street = fields.Char(string='Sub Street',related='partner_id.street2')
    city = fields.Char(string='City',related='partner_id.city')
    governorate = fields.Many2one('res.country.state', string='Governorate',related='partner_id.state_id')
    country_name = fields.Many2one('res.country', string='Country',related='partner_id.country_id')
    phone=fields.Char(string='Phone',related='partner_id.phone')


