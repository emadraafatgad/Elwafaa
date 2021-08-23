# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadLostInherit(models.TransientModel):
    _inherit = 'crm.lead.lost'


    @api.multi
    def action_lost_reason_apply(self):
        leads = self.env['pipeline.data'].browse(self.env.context.get('active_ids'))
        leads.write({'lost_reason': self.lost_reason_id.id})
        return leads.action_set_lost()
