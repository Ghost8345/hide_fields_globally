# __manifest__.py
{
    'name': 'Base Field Hider',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Dynamically hides specified fields across all views.',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hidden_field_config_views.xml',
    ],
    "license": "OEEL-1",
    "category": "Customization",
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
}