# -*- coding:utf-8 -*-

{
    'name': 'New Product Create',
    'version': '15.0.0',
    'category': 'Inventory',
    'author': 'Ripon Hossain',
    'sequence': -1000,
    'summary': 'New Product Create Management',
    'description': "New Product Create Management",
    'depends': ['mail', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/product_create.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'licence': 'LGPL-3',
}