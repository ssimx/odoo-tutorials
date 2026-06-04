{
    'name': 'Estate',
    'version': '1.9',
    'category': 'Real Estate',
    'sequence': 15,
    'summary': 'Manage your real estate properties',
    'website': 'https://www.odoo.com/app/estate',
    'depends': ['base'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_views.xml',
        'views/res_users_views.xml',
        'views/estate_menus.xml',
    ],
}