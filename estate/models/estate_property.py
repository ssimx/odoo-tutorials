from odoo import fields, models, api, exceptions
from odoo.tools.float_utils import float_compare, float_is_zero
from datetime import timedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(
        string='Availability Date',
        copy=False,
        default=lambda self: (fields.Date.today() + timedelta(days=90))
    )
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        help='The orientation of the garden'
    )
    state = fields.Selection(
        string='State',
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        default='new',
        help='The state of the property',
        copy=False,
        required=True,
    )
    active = fields.Boolean(string='Active', default=True)
    property_type_id = fields.Many2one(string='Property Type', comodel_name='estate.property.type')
    buyer_id = fields.Many2one(string='Buyer', comodel_name='res.partner', copy=False)
    salesperson_id = fields.Many2one(
        string='Salesperson',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many(string='Tags', comodel_name='estate.property.tag')
    offer_ids = fields.One2many(
        string='Offers',
        comodel_name='estate.property.offer',
        inverse_name='property_id'
    )
    total_area = fields.Integer(string='Total Area', compute='_compute_total_area')
    best_offer = fields.Float(string='Best Offer', compute='_compute_best_offer')

    _sql_constraints = [
        (
            'property_expected_price_positive',
            'CHECK(expected_price > 0)',
            'Property expected price must be strictly positive.'
        ),
        (
            'property_selling_price_positive',
            'CHECK(selling_price >= 0)',
            'Property selling price must be positive.'
        ),
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue

            minimum_price = record.expected_price * 0.9

            if float_compare(
                record.selling_price,
                minimum_price,
                precision_digits=2
            ) < 0:
                raise exceptions.ValidationError(
                    'Selling price cannot be lower than 90% of expected price.'
                )

    @api.constrains('date_availability')
    def _check_date_availability(self):
        for record in self:
            if record.date_availability < fields.Date.today():
                raise exceptions.ValidationError('Date availability must be in the future.')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped('price'), default=0)

    @api.onchange('garden')
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = False
        else:
            self.garden_area = 10
            self.garden_orientation = 'north'

    def action_set_status_sold(self):
        if self.state == 'sold' or self.state == 'canceled':
            raise exceptions.UserError('Property is already sold or canceled')
        for record in self:
            record.state = 'sold'
        return True

    def action_set_status_canceled(self):
        if self.state == 'sold' or self.state == 'canceled':
            raise exceptions.UserError('Property is already sold or canceled')
        for record in self:
            record.state = 'canceled'
        return True

    @api.ondelete(at_uninstall=False)
    def _ondelete_check_state(self):
        for record in self:
            # Prevent deletion if not in 'new' or 'canceled'
            if record.state not in ('new', 'canceled'):
                raise exceptions.UserError(
                    "You can only delete properties with state 'New' or 'Canceled'."
                )

        # Deletion proceeds as default
        # (The actual unlink happens after this check in the Odoo core)