{
    'name': 'Lab Management',
    'version': '1.0',
    'summary': 'Manage Patients, Lab Tests and Imaging',
    'author': 'Rehab',
    'category': 'Healthcare',
    'depends': ['base', 'sale'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizard/select_lab_type_wizard.xml',
        'views/lab_menu.xml',
        'views/account_move_views.xml',
        'views/patient_views.xml',
        'views/test_type_views.xml',
        'views/visit_views.xml',
        'views/test_result_views.xml',
        'views/lab_patient_invoice_views.xml',
        'reports/patient_visit_report.xml',
        'data/visit_server_action.xml',
        'data/report_data.xml',
        'data/visit_invoice_action.xml',
        'data/email_template.xml',
    ],
    'installable': True,
    'application': True,
}
