from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'sequence, name'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence to order property types'
    )
    name = fields.Char(string='Name', required=True)

    property_ids = fields.One2many(
        'estate.property',
        'property_type_id',
        string='Properties'
    )

    _sql_constraints = [
        (
            'property_type_name_unique',
            'UNIQUE(name)',
            'Property type name must be unique.'
        )
    ]