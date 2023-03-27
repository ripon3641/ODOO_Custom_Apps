from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import datetime


class LoanManagement(models.Model):
    _name = "loan.management"
    _description = "Loan Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference_no'

    reference_no = fields.Char(string='Serial No', required=True,
                               readonly=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    loan_reference = fields.Text(string='Reference')
    loan_type = fields.Many2one('loantype.config', string='Loan Type', required=True, tracking=True)
    bank_name = fields.Many2one('bank.configuration', string='Bank Name', required=True, tracking=True)
    apply_date = fields.Date(string='Apply Date', required=True, tracking=True)
    apply_amount = fields.Integer(string='Apply Amount', tracking=True)
    loan_approve_date = fields.Date(string='Approve Date', tracking=True)
    interest_rate = fields.Float(string='Interest Rate', default='9', tracking=True, required=True)
    monthly_installment = fields.Integer(compute='_compute_monthly_installment', string='Installment Amount',
                                         store=True)
    loan_approve_amount = fields.Integer(string='Approve Amount', required=True, tracking=True)
    loan_tenure = fields.Float(string='Tenure (Year)', tracking=True, default='1', required=True)
    interest_amount = fields.Integer(compute='_compute_interest_amount', string='Interest Amount', store=True)
    total_amount = fields.Integer(compute='_compute_total_amount', string='Total Amount', store=True)
    note = fields.Html(string='Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('approved', 'Approved'),
        ('disbursement', 'Disbursement'),
        ('cancel', 'Cancelled')], string='Status', default='draft', invisible='1', tracking=True)
    remaining_amount = fields.Integer(compute='_compute_remaining_amount', string='Remaining Amount', store=True)
    number_of_installment = fields.Integer(compute='_compute_number_of_installment', string='Installment', store=True)
    first_installment_date = fields.Date(string='First Installment Date', required=True)
    next_payment_date = fields.Date(string='Next payment Date')
    loan_account = fields.Many2one('account.account', string='Loan Account', )
    disbursement_amount = fields.Float(compute='_compute_disbursement_amount', string='Disbursed Amount', )
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'bank')]")
    disbursement_date = fields.Date(string='Disbursed Date')
    journal_entry_id = fields.Many2one('account.move', string='Disbursed Journal', readonly=True, copy=False)
    base_value_installment = fields.Integer(compute='_compute_base_value_installment', string='Base Value', store=True)
    interest_value_installment = fields.Integer(compute='_compute_interest_value_installment', string='Interest Value',
                                                store=True)
    view_installments_button = fields.Boolean(string='Installments', readonly=True, on_click='action_view_installments')
    installment_ids = fields.One2many('loan.installment', 'loan_ref_no', string='Installments')
    total_installments = fields.Integer(compute='_compute_total_installments')
    settled_amount = fields.Integer(string='Settled Amount', compute='_compute_settled_amount', store=True)
    is_readonly = fields.Boolean(string='Is Readonly?', compute='_compute_is_readonly', store=True)
    expense_account = fields.Many2one('account.account', string='Expense Account', required=True)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'loan.management') or _('New')
        res = super(LoanManagement, self).create(vals)
        return res

    def button_submit(self):
        self.write({
            'state': 'submit'
        })

    def button_reset_to_draft(self):
        self.write({
            'state': "draft"
        })

    def button_cancel(self):
        self.write({
            'state': "cancel"
        })

    @api.depends('number_of_installment', 'interest_rate', 'loan_approve_amount')
    def _compute_monthly_installment(self):
        for record in self:
            r = (record.interest_rate / 100) / 12
            n = record.number_of_installment
            monthly_installment = (record.loan_approve_amount * r * (1 + r) ** n) / ((1 + r) ** n - 1)
            record.monthly_installment = (monthly_installment)

    @api.depends('loan_approve_amount', 'number_of_installment', 'interest_rate', 'monthly_installment')
    def _compute_interest_amount(self):
        for record in self:
            record.interest_amount = (record.number_of_installment * record.monthly_installment) - record.loan_approve_amount

    @api.depends('loan_approve_amount', 'interest_amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.loan_approve_amount + record.interest_amount

    @api.depends('total_amount', 'settled_amount')
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.total_amount - record.settled_amount

    @api.depends('loan_tenure')
    def _compute_number_of_installment(self):
        for record in self:
            record.number_of_installment = record.loan_tenure * 12

    @api.depends('loan_approve_amount', 'number_of_installment')
    def _compute_base_value_installment(self):
        for record in self:
            record.base_value_installment = record.loan_approve_amount / record.number_of_installment

    @api.depends('interest_amount', 'number_of_installment')
    def _compute_interest_value_installment(self):
        for record in self:
            record.interest_value_installment = record.interest_amount / record.number_of_installment

    def action_view_installment(self):
        return

    @api.depends('loan_approve_amount')
    def _compute_disbursement_amount(self):
        for record in self:
            record.disbursement_amount = record.loan_approve_amount

    def generate_journal_entry(self):
        move = self.env['account.move'].create({
            'journal_id': self.journal_id.id,
            'ref': 'Disbursement of %s' % self.reference_no,
            'date': self.disbursement_date,
            'line_ids': [
                (0, 0, {
                    'name': 'Loan Disbursement',
                    'account_id': self.loan_account.id,
                    'credit': self.disbursement_amount,
                }),
                (0, 0, {
                    'name': 'Bank Account',
                    'account_id': self.journal_id.default_account_id.id,
                    'debit': self.disbursement_amount,
                }),
            ]
        })
        move.post()
        self.journal_entry_id = move.id

    def button_disbursement(self):
        self.generate_journal_entry()
        self.write({
            'state': 'disbursement'
        })

    @api.model
    def _check_not_approved(self):
        for record in self:
            if record.state in ('approved', 'disbursement'):
                return False
        return True

    def unlink(self):
        if not self._check_not_approved():
            raise UserError(_('You cannot delete a record that is already Approved or Disbursed.'))
        return super(LoanManagement, self).unlink()

    @api.depends('state')
    def _compute_is_readonly(self):
        for record in self:
            if record.state in 'disbursement':
                record.is_readonly = True
            else:
                record.is_readonly = False

    @api.model
    def _get_installment_action(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installments',
            'res_model': 'loan.installment',
            'view_mode': 'tree,form',
            'domain': [('loan_ref_no', '=', self.id)],
            'context': {'create': True},
            'target': 'current',
        }

    def action_view_installments(self):
        return self._get_installment_action()

    # @api.model
    # def action_create_installment(self):
    #     installment_vals = {
    #         'loan_ref_no': self.env.context.get('default_loan_ref_no'),
    #         # other required field values
    #     }
    #     installment = self.env['installment'].create(installment_vals)
    #     return {
    #         'name': 'Installment',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'installment',
    #         'res_id': installment.id,
    #         'view_mode': 'form',
    #         'target': 'current',
    #     }

    @api.depends('installment_ids')
    def _compute_total_installments(self):
        for loan in self:
            loan.total_installments = len(loan.installment_ids)

    @api.depends('installment_ids')
    def _compute_settled_amount(self):
        for record in self:
            record.settled_amount = sum(record.installment_ids.mapped('installment_amount'))

    def generate_installments(self):
        Installment = self.env['loan.installment']
        installments = []
        # for i in range(1, int(self.number_of_installment) + 1):
        for i in range(self.number_of_installment):
            installment_date = self.first_installment_date + relativedelta(months=i)
            installment = Installment.new({
                'loan_ref_no': self.id,
                'installment_no': str(i + 1).zfill(3),
                'installment_date': installment_date,
                'loan_account': self.loan_account,
                'expense_account': self.expense_account,
                'base_value': self.base_value_installment,
                'interest_value': self.interest_value_installment,
                'installment_amount': self.monthly_installment,
            })
            installment._onchange_loan_ref_no()
            installments.append(installment._convert_to_write(installment._cache))
        Installment.create(installments)

    def button_approve(self):
        self.state = "approved"
        self.generate_installments()
        return True
