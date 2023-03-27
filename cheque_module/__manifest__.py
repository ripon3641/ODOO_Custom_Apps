# -*- coding:utf-8 -*-

{
    'name': 'Cheque Management',
    'version': '15.0.0',
    'category': 'Cheque Management',
    'author': 'Ripon Hossain',
    'sequence': -1000,
    'summary': 'Cheque Management System',
    'description': "Cheque Management System",
    'depends': ['mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/cheque_management.xml',
        'views/payment_cheque.xml',
        'views/cheque_configuration.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}