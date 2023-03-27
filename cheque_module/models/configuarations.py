from odoo import api, fields, models


class ChequeConfiguration(models.Model):
    _name = "cheque.configuration"
    _description = "Cheque Configuration"
    _rec_name = 'bank_name'

    bank_name = fields.Char(string='Bank Name', required=True)
    active = fields.Boolean(string='Active', default=True)