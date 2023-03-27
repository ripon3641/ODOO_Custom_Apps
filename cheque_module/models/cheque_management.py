from odoo import api, fields, models
from odoo.tools.translate import _
import datetime


class ChequeManagement(models.Model):
    _name = 'cheque.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cheque Management'
    _rec_name = 'reference_no'

    reference_no = fields.Char(string='Serial No', required=True,
                               readonly=True, default=lambda self: _('New'))
    receive_date = fields.Date(string='Received Date', required=True, tracking=True, default=fields.Date.today)
    party_name = fields.Many2one('res.partner', string='Party Name', required=True, tracking=True,)
    cheque_no = fields.Char(string='Cheque No', required=True, tracking=True)
    cheque_date = fields.Date(string='Cheque Date', required=True)
    cheque_status = fields.Char(string='Cheque Status')
    bank_name = fields.Many2one('cheque.configuration', string='Bank Name', required=True, tracking=True)
    branch_name = fields.Char(string='Branch Name', required=True, tracking=True)
    cheque_type = fields.Selection([
        ('regular', 'Regular'),
        ('bank_guaranty', 'Bank Guaranty'),
        ('security', 'Security'),
    ], string='Cheque Type', default='regular', tracking=True)
    expire_date = fields.Date(string='Expire Date', compute='_compute_expire_date', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    amount = fields.Float(string='Amount', required=True, default='0', tracking=True)
    money_receipt_no = fields.Char(string='Money Receipt No', required=True, tracking=True)
    responsible_name = fields.Char(string='Responsible Name', required=True, tracking=True)
    zone = fields.Selection([
        ('zone1', 'Zone-1'),
        ('zone2', 'Zone-2'),
        ('zone3', 'Zone-3'),
        ('zone4', 'Zone-4'),
        ('zone5', 'Zone-5'),
        ('zone6', 'Zone-6'),
        ('zone7', 'Zone-7'),
        ('zone8', 'Zone-8'),
        ('zone9', 'Zone-9'),
        ('zone10', 'Zone-10'),
        ('corporate', 'Corporate'),
        ('dealerretailer', 'Dealer & Retailer')
    ], string='Zone', required=True, tracking=True)
    name = fields.Char(string='name', tracking=True)
    designation = fields.Char(string='Designation', tracking=True)
    Phone_no = fields.Char(string='Phone No', tracking=True)
    state = fields.Selection([
        ('ready', 'Ready'),
        ('clearing', 'Clearing'),
        ('honoured', 'Honoured'),
        ('dishonour1', 'Dishonour-1'),
        ('dishonour2', 'Dishonour-2'),
        ('dishonour3', 'Dishonour-3'),
        ('return', 'Return'),
        ('cancel', 'Cancelled')], string='Status', default='ready', invisible='1', tracking=True)
    deposit_bank = fields.Many2one('account.journal', string='Deposit Bank Name', tracking=True, required=True, domain=[('type', 'in', ['bank', 'cash'])])
    deposit_date = fields.Date(string='Deposit Date', tracking=True, required=True,
                               states={'ready': [('required', False)]})
    deposit_branch = fields.Char(string='Deposit Branch', tracking=True, required=True,
                                 states={'ready': [('required', False)]})
    journal_entry_id = fields.Many2one('account.move', string='Disbursed Journal', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'cheque.management') or _('New')
        res = super(ChequeManagement, self).create(vals)
        return res

    @api.depends('cheque_date')
    def _compute_expire_date(self):
        for rec in self:
            if rec.cheque_date:
                rec.expire_date = rec.cheque_date + datetime.timedelta(days=180)

    def button_clearing(self):
        self.write({
            'state': "clearing"
        })

    def button_honoured(self):
        self.write({
            'state': "honoured"
        })

    def button_dishonour1(self):
        self.write({
            'state': "dishonour1"
        })

    def button_dishonour2(self):
        self.write({
            'state': "dishonour2"
        })

    def button_dishonour3(self):
        self.write({
            'state': "dishonour3"
        })

    def button_return(self):
        self.write({
            'state': "return"
        })

    def button_reset_to_draft(self):
        self.write({
            'state': "ready"
        })

    def button_cancel(self):
        self.write({
            'state': "cancel"
        })

    def create_journal_entry(self):
        for record in self:
            if record.button_honoured:
                # create a debit entry for the deposit bank
                debit_vals = {
                    'account_id': record.deposit_bank.account_id.id,
                    'debit': record.amount,
                }
                # create a credit entry for the party name
                credit_vals = {
                    'account_id': record.party_name.property_account_receivable_id.id,
                    'credit': record.amount,
                }
                # create the journal entry
                vals = {
                    'journal_id': record.deposit_bank.id,
                    'date': fields.Date.deposit_date,
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
                }
                self.env['account.move'].create(vals)
