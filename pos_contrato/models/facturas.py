from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    pagos_ids = fields.Many2many('account.payment', string='Pagos Registrados')


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        # Obtener facturas desde el contexto
        invoice_ids = self.env.context.get('active_ids', [])
        invoices = self.env['account.move'].browse(invoice_ids)

        # Llamar al método original
        res = super().action_create_payments()

        payments = self.env['account.payment']

        # Intentar obtener los payment_ids desde el domain de la acción (si aplica)
        if isinstance(res, dict):
            domain = res.get('domain', [])
            if domain and isinstance(domain, list):
                for cond in domain:
                    if isinstance(cond, (list, tuple)) and cond[0] == 'id' and cond[1] == 'in':
                        payment_ids = cond[2]
                        payments |= self.env['account.payment'].browse(payment_ids)

        # Fallback: usar los pagos reconciliados (por si res no los trae)
        if not payments:
            for invoice in invoices:
                payments |= invoice._get_reconciled_payments()

        # Asignar pagos encontrados a cada factura
        for invoice in invoices:
            invoice.pagos_ids |= payments

        return res
