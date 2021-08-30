from odoo import models, fields, api, exceptions, _

class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    receiver_name = fields.Char(string=' Receiver Name',track_visibility='onchange')
    national_id = fields.Char(string='National ID',track_visibility='onchange')
    collection_representative =fields.Char(string='Collection Representative',track_visibility='onchange')
    amount_for = fields.Char(string='Amount Reason',track_visibility='onchange')

    # realty = fields.Char(string='Block Number')
    main_street = fields.Char(string='Main Street',related='partner_id.street',track_visibility='onchange')
    sub_street = fields.Char(string='Sub Street',related='partner_id.street2',track_visibility='onchange')
    city = fields.Char(string='City',related='partner_id.city',track_visibility='onchange')
    governorate = fields.Many2one('res.country.state', string='Governorate',related='partner_id.state_id')
    country_name = fields.Many2one('res.country', string='Country',related='partner_id.country_id')
    phone=fields.Char(string='Phone',related='partner_id.phone')


