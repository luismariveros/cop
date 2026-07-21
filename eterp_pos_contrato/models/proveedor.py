from odoo import models, fields, api

class ProjectProveedor(models.Model):
    _inherit = 'project.proveedor'

    monto_contrato = fields.Float(string='Monto de Contrato')
    monto_pagado = fields.Monetary(string='Monto Pagado', compute='_compute_montos', store=True)
    pendiente_de_pago = fields.Monetary(string='Pendiente de Pago', compute='_compute_montos', store=True)
    currency_id = fields.Many2one('res.currency', related='project_id.currency_id', readonly=True)
    archivo_adjunto = fields.Binary(string="Adjunto")
    nombre_archivo_adjunto = fields.Char(string="Nombre")
    @api.depends('monto_contrato', 'partner_id', 'project_id')
    def _compute_montos(self):
        for rec in self:
            total_pagado = 0.0

            if rec.partner_id and rec.project_id:
                orders = self.env['purchase.order'].search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('state', 'in', ['purchase', 'done']),
                    ('proyect_id', '=', rec.project_id.id),
                    ('sin_secuencia', '=', False),
                ])
                invoices = self.env['account.move'].search([
                    ('move_type', '=', 'in_invoice'),
                    ('invoice_origin', 'in', orders.mapped('name')),
                    ('state', '=', 'posted'),
                ])

                for pagos in invoices.mapped('pagos_ids'):
                    if pagos:
                        total_pagado += pagos.amount

            rec.importe_total = rec.monto_contrato or 0.0
            rec.monto_pagado = total_pagado
            rec.pendiente_de_pago = (rec.monto_contrato or 0.0) - total_pagado


