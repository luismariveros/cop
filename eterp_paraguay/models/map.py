from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.sql import index_exists, drop_index


class AccountMove(models.Model):
    _inherit = "account.move"
    # location = fields.Char(help="Enlace a la ubicación", string='Ubicación')
    @api.onchange("location")
    def format_location(self):
        for rec in self:
            print(" rec=>>>>>>>>>", rec.location)