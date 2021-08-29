from odoo import models, fields, api, exceptions, _

class AreaDataClass(models.Model):
    _name = 'area.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name= fields.Many2one('area.record',string='Area')
    # center = fields.Char(string='Center')
    # governorate=fields.Many2one('res.country.state',string='Governorate')
    # country = fields.Many2one('res.country', string='Country')
    workshop_number=fields.Integer(string='Workshops Number',compute='workshop_table_compute_change')
    merchants_number=fields.Integer(string='Merchants Number',compute='merchants_table_compute_change')
    workshop_table=fields.One2many('workshop.table','workshop_inverse',compute='workshop_table_compute_change',store=True)
    merchants_table=fields.One2many('merchants.table','merchants_inverse',compute='merchants_table_compute_change',store=True)

    @api.multi
    @api.depends('name')
    def workshop_table_compute_change(self):
        l=[]
        asd = self.env['workshop.info'].search([('area', '=', self.name.id)])
        for rec in self:
            self.workshop_table.unlink()
            if asd:
                for m in asd:
                  l.append({
                              "name": m.name,
                              "phone": m.phone,
                          })
            rec.workshop_table=l
        self.workshop_number=(len(self.workshop_table))

    @api.multi
    @api.depends('name')
    def merchants_table_compute_change(self):
        l = []
        asd = self.env['merchants.data'].search([('area', '=', self.name.id)])
        for rec in self:
            self.merchants_table.unlink()
            if asd:
                for m in asd:
                    l.append({
                        "name": m.name,
                        "phone": m.phone,
                    })
            rec.merchants_table = l
        self.merchants_number = (len(self.merchants_table))




class AreaRecordClass(models.Model):
    _name = 'area.record'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name= fields.Char(string='Area',track_visibility='onchange')
    center = fields.Char(string='Center',track_visibility='onchange')
    governorate=fields.Many2one('res.country.state',string='Governorate',track_visibility='onchange')
    country = fields.Many2one('res.country', string='Country',track_visibility='onchange')





class WorkshopTableClass(models.Model):
    _name = 'workshop.table'

    name= fields.Char('Name',store=True,track_visibility='onchange')
    phone = fields.Char('Phone',store=True,track_visibility='onchange')

    workshop_inverse=fields.Many2one('area.data',track_visibility='onchange')



class MerchantsTableClass(models.Model):
    _name = 'merchants.table'

    name= fields.Many2one('res.partner',string='Name',store=True,track_visibility='onchange')
    phone = fields.Char('Phone',store=True)

    merchants_inverse=fields.Many2one('area.data',track_visibility='onchange')