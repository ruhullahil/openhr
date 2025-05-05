# -*- coding: utf-8 -*-
{
    'name': "Maintenance",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','maintenance','stock_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/security.xml',
        'data/seq.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/inherited_product_tempalate.xml',
        'views/maintenance_equipment_sate.xml',
        'views/inherited_maintenance_equipment.xml',
        'views/location_user_configuration.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

