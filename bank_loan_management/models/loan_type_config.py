from odoo import api, fields, models


class LoantypeConfig(models.Model):
    _name = "loantype.config"
    _description = "Loan Type Configurations"
    _rec_name = "loan_type"

    loan_type = fields.Char(string='Loan Type', required=True)
    active = fields.Boolean(string='Active', default=True)
