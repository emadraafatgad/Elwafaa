from odoo import models, fields, api, exceptions, _

class PipelineDataClass(models.Model):
    _name = 'pipeline.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'company'

    have_meetings =fields.Boolean(string='Have a meeting?',compute='_compute_meeting_or_not')
    company = fields.Char(string='Company Name',store=True,copy=True)
    active = fields.Boolean('Active', default=True, track_visibility=True)
    main_street = fields.Char(string='Main Street')
    sub_street = fields.Char(string='Sub Street')
    city = fields.Char(string='City')
    governorate = fields.Many2one('res.country.state', string='Governorate')
    country_name = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Phone')
    employee = fields.Many2one('res.users',string='Employee',track_visibility='onchange', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', "Draft"),
        ('accept', "Accepted"),
        ('reject', "Rejected"),

    ], default='draft')
    have_m = fields.Selection([
        ('yes', "Yes"),
        ('no', "No"),
    ], default='yes',compute='_compute_have_meetings_or_not', string='Have a meeting?')

    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')

    @api.multi
    def _compute_meeting_count(self):
        meeting_data = self.env['calendar.event'].read_group([('opportunity_id', 'in', self.ids)], ['opportunity_id'],
                                                             ['opportunity_id'])
        mapped_data = {m['opportunity_id'][0]: m['opportunity_id_count'] for m in meeting_data}
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)

    @api.multi
    @api.depends('meeting_count')
    def _compute_meeting_or_not(self):
        for line in self:
            if line.meeting_count > 0:
                line.have_meetings = True
            else:
                line.have_meetings = False

    @api.multi
    @api.depends('have_meetings')
    def _compute_have_meetings_or_not(self):
        for line in self:
            if line.have_meetings ==True:
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
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.company:
            partner_ids.append(self.company)
        action['context'] = {
            'default_opportunity_id': self.id ,
            'default_partner_id': self.company,
            # 'default_partner_ids': partner_ids,
            # 'default_team_id': self.team_id.id,
            'default_name': self.employee.id,
        }
        return action

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_accept(self):
        self.state = 'accept'
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
        # }

    @api.multi
    def action_reject(self):
        self.state = 'reject'

