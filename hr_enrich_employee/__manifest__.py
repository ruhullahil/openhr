# -*- coding: utf-8 -*-
{
    'name': "hr_enrich_employee",

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
    'depends': ['base','utm','hr_skills','hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/job_rank.xml',
        'views/hr_religion.xml',
        'views/location_type_configuration.xml',
        'views/views.xml',
        'views/inherited_hr_resume_line.xml',
        'views/location_configuration.xml',
        'views/inherited_work_location.xml',
        'views/menu.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'hr_enrich_employee/static/src/xml/inherit_resume_widget.xml',
            ],
        }
}

