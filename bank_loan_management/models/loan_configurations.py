from odoo import api, fields, models


class LoanConfiguration(models.Model):
    _name = "bank.configuration"
    _description = "Bank Configuration"
    _rec_name = 'bank_name'

    bank_name = fields.Char(string='Bank Name', required=True)
    active = fields.Boolean(string='Active', default=True)
