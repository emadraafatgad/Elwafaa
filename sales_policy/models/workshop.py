from odoo import models, fields, api, exceptions, _


class WorkshopsDataClass(models.Model):
    _name = 'workshop.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name= fields.Char(string='Name')
    phone = fields.Char(string='Phone')
    area=fields.Many2one('area.record',string='Area')
    # center=fields.Char(string='Center')
    # governorate=fields.Many2one('res.country.state',string='Governorate')
    # country=fields.Many2one('res.country',string='Country')



class MerchantsDataClass(models.Model):
    _name = 'merchants.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('res.partner',string='Name',domain="[('categories','=','workshops')]")
    phone = fields.Char(string='Phone')
    area=fields.Many2one('area.record',string='Area')
    # center = fields.Char(string='Center')
    # governorate = fields.Many2one('res.country.state', string='Governorate')
    # country = fields.Many2one('res.country', string='Country')







