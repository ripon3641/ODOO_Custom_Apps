from odoo import api, fields, models
from odoo.tools.translate import _


class PaymentCheque(models.Model):
    _name = 'payment.cheque'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payment Cheque'
    _rec_name = 'cheque_no'

    cheque_no = fields.Char(string='Serial No', required=True,
                            readonly=True, default=lambda self: _('New'))
    bank_name = fields.Many2one('account.journal', string='Bank Name', tracking=True, required=True, domain=[('type', '=', 'bank')])
    total_page = fields.Integer(string='Total Page', required=True)
    cheque_sl_no = fields.Integer(string="Cheque Serial No", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('activated', 'Activated'),
        ('deactivated', 'Deactivated'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', invisible='1', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('cheque_no', _('New')) == _('New'):
            vals['cheque_no'] = self.env['ir.sequence'].next_by_code(
                'payment.cheque') or _('New')
        res = super(PaymentCheque, self).create(vals)
        return res

    def button_activated(self):
        self.write({
            'state': "activated"
        })

    def button_deactivated(self):
        self.write({
            'state': "deactivated"
        })

    def button_cancel(self):
        self.write({
            'state': "cancel"
        })
