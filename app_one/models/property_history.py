from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.populate import compute


class PropertyHistory(models.Model):
    _name = 'property.history'
    _description = 'Property History'

    user_id = fields.Many2one('res.users')
    property_id = fields.Many2one('property')
    old_state = fields.Char()
    new_state = fields.Char()
    reason = fields.Char()





