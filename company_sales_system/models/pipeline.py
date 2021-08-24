from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.osv import expression


class PipelineDataClass(models.Model):
    _name = 'pipeline.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'company'

    lost_reason = fields.Many2one('crm.lost.reason', string='Lost Reason', index=True, track_visibility='onchange')
    have_meetings = fields.Boolean(string='Have a meeting?', compute='_compute_meeting_or_not', readonly=False)
    company = fields.Char(string='Company Name', store=True, copy=True, track_visibility='onchange')
    active = fields.Boolean('Active', default=True, track_visibility=True)
    main_street = fields.Char(string='Main Street', track_visibility='onchange')
    sub_street = fields.Char(string='Sub Street', track_visibility='onchange')
    city = fields.Char(string='City', track_visibility='onchange')
    governorate = fields.Many2one('res.country.state', string='Governorate', track_visibility='onchange')
    country_name = fields.Many2one('res.country', string='Country', track_visibility='onchange')
    phone = fields.Char(string='Phone', track_visibility='onchange')
    employee = fields.Many2one('res.users', string='SalesPerson', track_visibility='onchange',
                               default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', "Draft"),
        ('accept', "Accepted"),
        ('reject', "Rejected"),

    ], default='draft', track_visibility='onchange')
    have_m = fields.Selection([
        ('yes', "Yes"),
        ('no', "No"),
    ], string='Have a meeting?', default='no', compute='_compute_have_meetings_or_not')
    # , compute = '_compute_have_meetings_or_not'
    # , search = '_search_abandoned_cart'

    # def _search_abandoned_cart(self, operator, value):
    #     abandoned_delay = self.website_id and self.website_id.cart_abandoned_delay or 1.0
    #     abandoned_datetime = fields.Datetime.to_string(datetime.utcnow() - relativedelta(hours=abandoned_delay))
    #     abandoned_domain = expression.normalize_domain([
    #         ('date_order', '<=', abandoned_datetime),
    #         ('team_id.team_type', '=', 'website'),
    #         ('state', '=', 'draft'),
    #         ('partner_id', '!=', self.env.ref('base.public_partner').id),
    #         ('order_line', '!=', False)
    #     ])
    #     # is_abandoned domain possibilities
    #     if (operator not in expression.NEGATIVE_TERM_OPERATORS and value) or (
    #             operator in expression.NEGATIVE_TERM_OPERATORS and not value):
    #         return abandoned_domain
    #     return expression.distribute_not(['!'] + abandoned_domain)  # negative domain

    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')

    @api.multi
    def _compute_meeting_count(self):
        meeting_data = self.env['calendar.event'].read_group([('opportunity_id', 'in', self.ids)], ['opportunity_id'],
                                                             ['opportunity_id'])
        mapped_data = {m['opportunity_id'][0]: m['opportunity_id_count'] for m in meeting_data}
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)

    # @api.multi
    # @api.depends('meeting_count')
    # def _compute_meeting_or_not(self):
    #     for line in self:
    #         if line.meeting_count > 0:
    #             line.have_meetings = True
    #         else:
    #             line.have_meetings = False

    @api.multi
    @api.depends('meeting_count')
    def _compute_have_meetings_or_not(self):
        for line in self:
            if line.meeting_count > 0:
                line.have_m = 'yes'
            else:
                line.have_m = 'no'

    @api.multi
    def action_set_lost(self):
        """ Lost semantic: probability = 0, active = False """
        return self.write({'state': 'reject', 'active': False})

    @api.multi
    def action_schedule_meeting(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        action = self.env.ref('company_sales_system.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.company:
            partner_ids.append(self.company)
        # action['context'] = {'phone': self.phone,
        #              'employee_user': self.employee.id,
        #              'company': self.company, }
        action['context'] = {
            'default_opportunity_id': self.id,
            'default_partner_id': self.company,
            'default_name': self.employee.name,
            # 'default_partner_ids': partner_ids,
            # 'default_team_id': self.team_id.id,
            'default_phone': self.phone,
            'default_employee_user': self.employee.id,
            'default_company': self.company,
        }
        print(self.env.context.get('active_ids'))
        leads = self.env['calendar.event'].browse(self.env.context.get('active_ids'))
        print(leads)
        leads.write({'phone': self.phone,
                     'employee_user': self.employee.id,
                     'company': self.company, })

        return action

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_accept(self):
        self.state = 'accept'
        # leads = self.env['calendar.event'].browse(self.env.context.get('active_ids'))
        # leads.write({'phone': self.phone,
        #              'employee_user': self.employee.id,
        #              'company': self.company, })
        # context= {'phone': self.phone,
        #              'employee_user': self.employee.id,
        #              'company': self.company, }
        # return {
        #
        #     'name': ('Meeting Form'),
        #
        #     'view_type': 'form',
        #
        #     'view_mode': 'form',
        #
        #     'res_model': 'calendar.event',
        #
        #     'type': 'ir.actions.act_window',
        #
        #      'target': 'new',
        #
        #     'context':context,
        #
        # }

    @api.multi
    def action_reject(self):
        self.state = 'reject'
