from odoo import models, fields, api, exceptions, _

class CarsDataClass(models.Model):
    _name = 'car.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'car_type'

    car_type = fields.Many2one('car.type', string='Car Type',store=True,copy=True)
    plate_number = fields.Char(string='Plate Number')
    chassis_number = fields.Char('Chassis Number')
    car_model = fields.Many2one('model.car',string='Car Model',domain="[('car_type','=',car_type)]",store=True,copy=True)
    driver_name = fields.Char('Driver Name')
    customer=fields.Many2one('res.partner',string='Customer')



class CarType(models.Model):
    _name = 'car.type'


    name=fields.Char(string='Car Type')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', """Only one value can be defined for each given usage!"""),
    ]


class CarModel(models.Model):
    _name = 'model.car'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Car Model')
    car_type = fields.Many2one('car.type', string='Car Type')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', """Only one value can be defined for each given usage!"""),
    ]
