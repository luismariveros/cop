from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ruc = fields.Char(related='partner_id.ruc', store=True, readonly=True)
    documento = fields.Char(related='partner_id.ci', store=True, readonly=True)
    nombre_fantasia = fields.Char(related='partner_id.nf', store=True, readonly=True)
