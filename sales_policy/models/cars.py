from odoo import models, fields, api, exceptions, _

class CarsDataClass(models.Model):
    _name = 'car.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'car_type'

    car_type = fields.Many2one('car.type', string='Car Type',store=True,copy=True,track_visibility='onchange')
    plate_number = fields.Char(string='Plate Number',track_visibility='onchange')
    chassis_number = fields.Char('Chassis Number',track_visibility='onchange')
    car_model = fields.Many2one('model.car',string='Car Model',domain="[('car_type','=',car_type)]",store=True,copy=True)
    driver_name = fields.Char('Driver Name',track_visibility='onchange')
    customer=fields.Many2one('res.partner',string='Customer',track_visibility='onchange')
    fuel_tank = fields.Selection([('zero','0'),('quarter','1/4'),('one_th','1/3'),('th_fo','3/4'),('one','1')],string='Fuel Tank',track_visibility='onchange')
    # sliders = fields.Boolean(string='Sliders')
    # traps = fields.Boolean(string='Traps')
    # danagel = fields.Boolean(string='Danagel')
    # entery_date = fields.Date(string='Entry date')
    # fix_date = fields.Date(string='Fix date')
    # delivery_date = fields.Date(string='Delivery date')
    entry_counter = fields.Char(string='Entry Counter per KM',track_visibility='onchange')
    exit_counter = fields.Char(string='Exit Counter per KM',track_visibility='onchange')
    # for_companies=fields.Char('For Companies')
    # authority = fields.Char('Authority')
    #
    # supervisor_name = fields.Char('Supervisor')
    # technician_name = fields.Char('Technician ')
    # worker_name = fields.Many2many('worker.name',string='Worker')
    # customer_complain =fields.Text(string='Customer Complaint')




    # sale_quotation=fields.Many2one('sale.order',string='Sale')




class CarType(models.Model):
    _name = 'car.type'


    name=fields.Char(string='Car Type')
    _sql_constraints = [
        ('name_uniq', 'unique (name)', """Only one value can be defined for each given usage!"""),
    ]


class CarModel(models.Model):
    _name = 'model.car'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Car Model',track_visibility='onchange')
    car_type = fields.Many2one('car.type', string='Car Type',track_visibility='onchange')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', """Only one value can be defined for each given usage!"""),
    ]


class WorkersGroup(models.Model):
    _name = 'worker.name'

    name=fields.Char(string='Name',track_visibility='onchange')
