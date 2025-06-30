# -*- coding: utf-8 -*-
{
    'name': "custom_dashboard_icons",

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
    'depends': ['base','purchase','project_todo','website','survey','hr_attendance','im_livechat','account_accountant',
                'my_chatgpt_module','calendar','contacts','crm','board','sales_team','mail','documents','website_sale',
                'hr','documents','mail','hr_payroll','point_of_sale','mass_mailing','hr_expense','fleet',
                'stock','sale','hr_holidays','project','helpdesk','spreadsheet_dashboard'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

