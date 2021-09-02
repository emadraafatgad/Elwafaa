from odoo import models, fields, api, exceptions, _

class TargetTeamClass(models.Model):
    _name = 'team.target'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name =fields.Many2one('res.users',string='User')
    team = fields.Many2one('crm.team',string='Team',related='name.sale_team_id')
    target =fields.Float(string='Target')
    # sale_team_id = fields.Many2one(
    #     'crm.team', 'User Sales Channel',
    #     related='team_user_ids.team_id', readonly=False,
    #     store=True)
