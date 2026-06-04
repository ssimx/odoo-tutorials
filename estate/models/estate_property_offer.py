from odoo import fields, models, api, exceptions
from odoo.fields import Date
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(string='Price')
    status = fields.Selection(string='Status', selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner', required=True)
    property_id = fields.Many2one(string='Property', comodel_name='estate.property', required=True)
    validity = fields.Integer(string='Validity', default=7)
    date_deadline = fields.Date(string='Deadline', compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    property_type_id = fields.Many2one(
        comodel_name='estate.property.type',
        string='Property Type',
        related='property_id.property_type_id',
        store=True
    )

    _sql_constraints = [
        (
            'property_offer_price_positive',
            'CHECK(price > 0)',
            'Property offer price must be strictly positive.'
        )
    ]

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else Date.today()
            record.date_deadline = create_date + timedelta(days=record.validity)
     
    @api.onchange('date_deadline')
    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else Date.today()
            record.validity = (record.date_deadline - create_date).days

    @api.model
    def create(self, vals):
        # Ensure property_id and price are supplied in vals
        property_id = vals.get('property_id')
        price = vals.get('price')
        if property_id and price is not None:
            property_obj = self.env['estate.property'].browse(property_id)
            # Check if there is any existing offer with greater or equal price
            existing_max = max(property_obj.offer_ids.mapped('price') or [0])
            if price <= existing_max:
                raise exceptions.UserError('You cannot create an offer with a lower amount than an existing offer.')
        # Create offer
        offer = super(EstatePropertyOffer, self).create(vals)
        # Set the property state to 'offer_received' as soon as an offer is created
        if offer.property_id and offer.property_id.state == 'new':
            offer.property_id.state = 'offer_received'
        return offer

    def action_accept_offer(self):
        for record in self:
            if record.status in ('accepted', 'refused'):
                raise exceptions.UserError('Offer is already accepted or refused')
            elif record.property_id.state != 'offer_received':
                raise exceptions.UserError('Property is not in offer received state')
        for record in self:
            record.status = 'accepted'
            record.property_id.state = 'sold'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
        return True

    def action_refuse_offer(self):
        for record in self:
            if record.status in ('accepted', 'refused'):
                raise exceptions.UserError('Offer is already accepted or refused')
        for record in self:
            record.status = 'refused'
        return True