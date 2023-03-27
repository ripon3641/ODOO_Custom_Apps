from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import timedelta

class LoanInstallment(models.Model):
    _name = "loan.installment"
    _descriptions = "Loan Installment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "installment_no"

    installment_no = fields.Char(string='Serial No', required=True,
                               readonly=True, default=lambda self: _('New'))
    loan_ref_no = fields.Many2one(comodel_name='loan.management', string="Loan Reference No", tracking=True)
    installment_date = fields.Date(string="Installment Date", required=True)
    installment_amount = fields.Integer(related='loan_ref_no.monthly_installment', string="Installment Amount")
    state = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
        ], string='Status', default='unpaid', invisible='1', tracking=True)
    base_value = fields.Integer(related='loan_ref_no.base_value_installment', store=True)
    interest_value = fields.Integer(related='loan_ref_no.interest_value_installment', store=True)
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'bank')]", required=True)
    loan_account = fields.Many2one(related='loan_ref_no.loan_account', string='Loan Account')
    expense_account = fields.Many2one(related='loan_ref_no.expense_account', string='Expense Account', required=True)
    journal_entry_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False,)
    is_readonly = fields.Boolean(string='Is Readonly?', compute='_compute_is_readonly', store=True)

    @api.model
    def create(self, vals):
        if vals.get('installment_no', _('New')) == _('New'):
            vals['installment_no'] = self.env['ir.sequence'].next_by_code(
                'loan.installment') or _('New')
        res = super(LoanInstallment, self).create(vals)
        return res

    def button_reset_to_draft(self):
        self.write({
            'state': "unpaid"
        })

    def button_cancel(self):
        self.write({
            'state': "cancel"
        })

    @api.model
    def _check_not_paid(self):
        for record in self:
            if record.state in 'paid':
                return False
        return True

    def unlink(self):
        if not self._check_not_paid():
            raise UserError(_('You cannot delete a record that is already Paid'))
        return super(LoanInstallment, self).unlink()

    def generate_journal_entry(self):
        move = self.env['account.move'].create({
            'journal_id': self.journal_id.id,
            'ref': 'Payment of %s' % self.installment_no,
            'date': self.installment_date,
            'line_ids': [
                (0, 0, {
                    'name': 'Loan Payment',
                    'account_id': self.loan_account.id,
                    'debit': self.base_value,
                }),
                (0, 0, {
                    'name': 'Loan Interest',
                    'account_id': self.expense_account.id,
                    'debit': self.interest_value,
                }),
                (0, 0, {
                    'name': '',
                    'account_id': self.journal_id.default_account_id.id,
                    'credit': self.base_value + self.interest_value,
                }),
            ]
        })
        move.post()
        self.journal_entry_id = move.id

    def button_paid(self):
        self.generate_journal_entry()
        self.write({
            'state': 'paid'
        })

    @api.depends('state')
    def _compute_is_readonly(self):
        for record in self:
            if record.state in 'paid':
                record.is_readonly = True
            else:
                record.is_readonly = False
