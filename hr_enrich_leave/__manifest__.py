# -*- coding: utf-8 -*-
{
    'name': "hr_enrich_leave",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_holidays','hr_enrich_employee','account_fiscal_year'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/leave_related_security.xml',
        'data/sequence.xml',
        'data/leave_allocation_corn.xml',
        'views/views.xml',
        'views/inherited_leave_type.xml',
        'views/hr_leave_default_configuration.xml',
        'views/leave_condition.xml',
        'views/compensatory_day.xml',
        'views/inherit_leave.xml',
        'views/menu.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'hr_enrich_leave/static/src/dashboard/inherit_time_off_dashboard.xml',
                'hr_enrich_leave/static/src/dashboard/inherit_time_off_card.js',
                # Don't include dark mode files in light mode

            ],
    }

}

