# -*- coding:utf-8 -*-

{
    'name': 'Bank Loan Management',
    'version': '15.0.0',
    'category': 'Accounting',
    'author': 'Ripon Hossain',
    'sequence': -1000,
    'summary': 'Bank Loan Management',
    'description': "Bank Loan Management",
    'depends': ['mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/bank_loan_management.xml',
        'views/loan_configurations.xml',
        'views/loan_type_config.xml',
        'views/loan_installment.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}