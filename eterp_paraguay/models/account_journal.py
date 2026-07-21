# importamos los módulos bases de odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

#importamos los módulos bases de odoo y heraedamos account_journal, luego creamos un campo tipo check, para idenficar si es un diario fiscal o no fiscal
class AccountJournal(models.Model):
    _inherit = "account.journal"
    x_fiscal = fields.Boolean(string='Fiscal', default=True)