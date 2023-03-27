# -*- coding:utf-8 -*-

{
    'name': 'Casting Schedule',
    'version': '15.0.0',
    'category': 'Casting Schedule',
    'author': 'Ripon Hossain',
    'sequence': -1000,
    'summary': 'Casting Schedule',
    'description': "Casting Schedule",
    'depends': ['mail', 'sale', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/casting_schedule.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}