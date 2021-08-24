from odoo import models, fields, api, exceptions, _

class CalendarEventClass(models.Model):
    _inherit="calendar.event"

    state_workflow = fields.Selection([
        ('draft', "Draft"),
        ('accept', "Accepted"),
        ('reject', "Rejected"),

    ], default='draft', track_visibility='onchange')
    phone = fields.Char(string='Phone', track_visibility='onchange')
    employee_user = fields.Many2one('res.users', string='SalesPerson', track_visibility='onchange',default=lambda self: self.env.user)

    company = fields.Char(string='Company Name',store=True,copy=True,track_visibility='onchange')
    priclist = fields.Many2one('pricelist.info',string='Price List')
    lost_reason = fields.Many2one('crm.lost.reason', string='Lost Reason', index=True, track_visibility='onchange')

    @api.multi
    def action_reject(self):
        self.state_workflow = 'reject'

    @api.multi
    def action_accept(self):
        self.state_workflow = 'accept'

