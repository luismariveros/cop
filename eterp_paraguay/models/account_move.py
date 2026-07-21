from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.sql import index_exists, drop_index


class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.onchange('journal_id')
    def _compute_ocultar(self):
        #Ocultar campos cuando el journal_id es diferente
        if self.journal_id.x_fiscal == True:
                self.x_ocultar = False               
        else:
            self.x_ocultar = True

    x_ocultar = fields.Boolean(compute='_compute_ocultar')
    _
    sql_constraints = [
        (
            "unique_name",
            "",
            "El numero de factura debe ser único.",
        ),
        (
            "unique_name_py",
            "",
            "El número de factura debe ser único para la misma compañía.",
        ),
    ]

    def _auto_init(self):
        super()._auto_init()
        # Update the generic unique name constraint to not consider the purchases in latam companies.
        # The name should be unique by partner for those documents.
        if not index_exists(self.env.cr, "account_move_unique_name_py"):
            drop_index(self.env.cr, "account_move_unique_name", self._table)
            self.env.cr.execute(
                """
                    CREATE UNIQUE INDEX account_move_unique_name
                                     ON account_move(name, journal_id)
                                  WHERE (state = 'posted' AND name != '/'
                                    AND (move_type NOT IN ('in_invoice', 'in_refund', 'in_receipt')));
                    CREATE UNIQUE INDEX account_move_unique_name_py
                                     ON account_move(name, commercial_partner_id, company_id, l10n_py_timbrado)
                                  WHERE (state = 'posted' AND name != '/'
                                    AND (move_type IN ('in_invoice', 'in_refund', 'in_receipt')));
                """
            )

    ruc = fields.Char(related="partner_id.ruc", store=True, readonly=True)
    documento = fields.Char(related="partner_id.ci", store=True, readonly=True)
    nombre_fantasia = fields.Char(related="partner_id.nf", store=True, readonly=True)

    l10n_latam_document_number = fields.Char(
        # compute='_compute_l10n_latam_document_number',
        inverse="_inverse_l10n_latam_document_number",
        string="Document Number",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    l10n_py_timbrado = fields.Char(
        string="Timbrado Proveedor",
        help="Numero de timbrado de la factura del proveedor",
    )
    l10n_py_validity_end = fields.Date(
        string="Validez Timbrado", help="Fecha de caducidad del timbrado del proveedor"
    )
    sufijo_doc = fields.Char("Sufijo")

    # @api.depends('name')
    # def _compute_l10n_latam_document_number(self):
    #     recs_with_name = self.filtered(lambda x: x.name != '/')
    #     for rec in recs_with_name:
    #         name = rec.name
    #         doc_code_prefix = False
    #         name_split = name.split(" ")
    #         if name and len(name_split) > 1:
    #             name = name_split[0]
    #         rec.l10n_latam_document_number = name
    #     remaining = self - recs_with_name
    #     remaining.l10n_latam_document_number = False

    @api.onchange("l10n_latam_document_number", "sufijo_doc")
    def _inverse_l10n_latam_document_number(self):
        print("entro1")
        for rec in self:
            if  rec.l10n_latam_document_number:
                print("entro")
                document_number = self._format_document_number(
                    rec.l10n_latam_document_number
                )
                if rec.l10n_latam_document_number != document_number:
                    rec.l10n_latam_document_number = document_number
                if not rec.sufijo_doc:
                    rec.name = document_number
                else:
                    rec.name = "%s %s" % (document_number, rec.sufijo_doc)
                

    def _format_document_number(self, document_number):
        args = document_number.split("-")
        failed = False
        if len(args) != 3:
            failed = True
        else:
            suc, exp, number = args
            if len(suc) > 3 or not suc.isdigit():
                failed = True
            elif len(exp) > 3 or not number.isdigit():
                failed = True
            elif len(number) > 7 or not number.isdigit():
                failed = True
            mask = "{:>03s}-{:>03s}-{:>07s}"
            document_number = mask.format(suc, exp, number)
        if failed:
            msg = "'%s' " + _("no es un valor valido para el documento") + " '%s'.\n%s"
            raise ValidationError(
                msg
                % (
                    document_number,
                    self.name,
                    _(
                        "El numero de documento debe ser ingresado separando con el "
                        "signo menos (-) cada parte, debe tener un maximo de 3 "
                        "digitos para Codigo de Establecimiento y Punto de Expedicion "
                        "y un maximo de 7 digitos para el numero de documento. "
                        "Los siguientes son ejemplos de numeros validos:\n"
                        "* 1-1-1\n"
                        "* 003-001-0000087\n"
                        "* 25-45-885"
                    ),
                )
            )
        return document_number

    def action_post(self):
        if  self.x_ocultar is False:            
            if self.move_type in ["in_invoice", "in_refund"]:
                # Verificar la longitud y tipo de timbrado
                if not self.l10n_py_timbrado:
                    raise ValidationError(
                        _("La longitud del timbrado debe ser de ocho digitos")
                    )
                if not self.l10n_py_validity_end:
                    raise ValidationError(_("Ingresa la fecha de validez del timbrado"))
                if len(self.l10n_py_timbrado) != 8:
                    raise ValidationError(
                        _("La longitud del timbrado debe ser de ocho digitos")
                    )
                try:
                    int(self.l10n_py_timbrado)
                except ValueError:
                    raise ValidationError(_("El timbrado debe ser numérico"))
                if not self.invoice_date:
                    raise ValidationError(_("Ingrese la fecha de la factura"))
                if self.invoice_date > self.l10n_py_validity_end:
                    raise ValidationError(
                        _("La fecha de la factura es posterior a la validez del timbrado")
                    )
                # llamar al metodo original
                super().action_post()
            else:
                # llamar al metodo original
                super().action_post()           
        else:
            print("entro3")
            print(self.l10n_latam_document_number)
            self.l10n_latam_document_number = ''
            self.l10n_py_timbrado = ''
            self.l10n_py_validity_end = ''
            self.name = ''
            super().action_post()
            

    def _post(self, soft=True):
        for invoice in self:
            if invoice.move_type in ["out_invoice", "out_refund"]:
                seq = invoice.journal_id.sequence_id
                seq_date = self.env["ir.sequence.date_range"].search(
                    [
                        ("sequence_id", "=", seq.id),
                        ("date_from", "<=", invoice.date),
                        ("date_to", ">=", invoice.date),
                    ],
                    limit=1,
                )
                if seq_date:
                    invoice.l10n_py_validity_end = seq_date.date_to
                    invoice.l10n_py_timbrado = seq_date.timbrado
        return super()._post(soft)

    # Se sobreescribe este método para evitar el warning en el cambio de nombre
    # @api.onchange('name', 'highest_name')
    def _onchange_name_warning(self):
        return

    @api.constrains("name", "journal_id", "state")
    def _check_unique_sequence_number(self):
        """This uniqueness verification is only valid for customer invoices, and vendor bills that does not use
        documents. A new constraint method _check_unique_vendor_number has been created just for validate for this purpose"""
        vendor = self.filtered(lambda x: x.is_purchase_document())
        return super(AccountMove, self - vendor)._check_unique_sequence_number()

    @api.constrains("name", "partner_id", "company_id","invoice_date")
    def _check_unique_vendor_number(self):
        """The constraint _check_unique_sequence_number is valid for customer bills but not valid for us on vendor
        bills because the uniqueness must be per partner"""
        for rec in self.filtered(
            lambda x: x.name
            and x.name != "/"
            and x.is_purchase_document()
            and x.commercial_partner_id
            and x.invoice_date
        ):
            domain = [
                ("move_type", "=", rec.move_type),
                # by validating name we validate l10n_latam_document_type_id
                ("name", "=", rec.name),
                ("company_id", "=", rec.company_id.id),
                ("id", "!=", rec.id),
                ("commercial_partner_id", "=", rec.commercial_partner_id.id),
                # allow to have to equal if they are cancelled
                ("state", "!=", "cancel"),
                ("invoice_date", "=", rec.invoice_date),
            ]
            if rec.search(domain):
                raise ValidationError(
                    _("Vendor bill number must be unique per vendor and company.")
                ) 