from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    property_ids = fields.Many2many(string='Tagged Properties', comodel_name='estate.property', inverse_name='tag_ids')
    color = fields.Integer(string='Color')
    
    _sql_constraints = [
    (
        'tag_name_unique',
        'UNIQUE(name)',
        'Tag name must be unique.'
    )
]