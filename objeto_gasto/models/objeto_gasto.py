from odoo import models, fields, api


class ObjetoGasto(models.Model):
    _name = "objeto.gasto"
    _description = "Objeto de Gasto"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Nombre", required=True, tracking=True)
    year = fields.Integer(string="Año", required=True, tracking=True)
    active = fields.Boolean(string="Activo", default=True, tracking=True)

    detalle_ids = fields.One2many(
        "objeto.gasto.detalle",
        "objeto_gasto_id",
        string="Detalles",
        tracking=True,
    )

    detalle_resumen = fields.Text(
        string="Resumen de Detalles",
        compute="_compute_detalle_resumen",
        store=True,
        tracking=True,
    )

    last_updated_by = fields.Many2one(
        "res.users", string="Última Actualización por", readonly=True, tracking=True
    )

    @api.depends("detalle_ids")
    def _compute_detalle_resumen(self):
        for record in self:
            detalles = [
                f"Código: {d.codigo}, Nombre: {d.name}" for d in record.detalle_ids
            ]
            record.detalle_resumen = "\n".join(detalles)
            record.last_updated_by = self.env.user.id  # Asignar ID en lugar del objeto


class ObjetoGastoDetalle(models.Model):
    _name = "objeto.gasto.detalle"
    _description = "Detalle del Objeto de Gasto"
    _order = "codigo asc"
    _rec_name = "codigo_nombre"

    codigo = fields.Integer(string="Código", required=True)
    name = fields.Char(string="Nombre", required=True)
    descripcion = fields.Text(string="Descripción")
    objeto_gasto_id = fields.Many2one(
        "objeto.gasto", string="Objeto de Gasto", required=True
    )
    codigo_nombre = fields.Char(
        string="Código - Nombre", compute="_compute_codigo_nombre", store=True
    )

    @api.depends("codigo", "name")
    def _compute_codigo_nombre(self):
        for record in self:
            record.codigo_nombre = f"{record.codigo} - {record.name}"

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.objeto_gasto_id:
            record.objeto_gasto_id._compute_detalle_resumen()
        return record

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if record.objeto_gasto_id:
                record.objeto_gasto_id._compute_detalle_resumen()
        return res

    def unlink(self):
        objeto_gasto_ids = self.mapped("objeto_gasto_id")
        res = super().unlink()
        for objeto_gasto in objeto_gasto_ids:
            objeto_gasto._compute_detalle_resumen()
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    objeto_gasto_detalle_id = fields.Many2one(
        "objeto.gasto.detalle", string="Detalle de Objeto de Gasto"
    )

    nombre_gasto = fields.Char(
        string="Objeto de Gasto", compute="_compute_nombre_gasto", store=True
    )

    @api.depends("objeto_gasto_detalle_id")
    def _compute_nombre_gasto(self):
        for record in self:
            if record.objeto_gasto_detalle_id:
                record.nombre_gasto = f"{record.objeto_gasto_detalle_id.codigo} - {record.objeto_gasto_detalle_id.name}"
            else:
                record.nombre_gasto = ""
