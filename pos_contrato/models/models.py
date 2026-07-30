from odoo import models, fields, api
from datetime import timedelta, date

class ProjectProject(models.Model):
    _inherit = 'project.project'
    coordinator_id = fields.Many2one('res.users', string="Coordinador Financiero", required=1)
    mesa_expediente_id = fields.Many2one('eterp.mesa.entrada.expediente', string='Expediente')

    def action_open_project_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Project',
            'res_model': 'project.project',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('project.edit_project').id,
            'target': 'current',
        }

    state_project = fields.Selection([
        ('draft', 'En proceso'),
        ('execution', 'En ejecución'),
        ('done', 'Finalizado'),
        ('rendered', 'Rendido')
    ], string='Estado del Proyecto', default='draft', tracking=True)

    # Supongamos que usas este campo para el plazo
    fecha_acreditacion = fields.Date(string="Fecha de Acreditación")

    def action_set_execution(self):
        for rec in self:
            rec.state_project = 'execution'

    @api.model
    def cron_auto_advance_projects(self):
        """Pasar automáticamente de ejecución a finalizado según fecha fin"""
        today = fields.Date.today()
        projects = self.search([
            ('state_project', '=', 'execution'),
            ('date', '<', today)
        ])
        for project in projects:
            project.state_project = 'done'
            # Crear actividad en lugar de mensaje
            for user in filter(None, [project.user_id, project.coordinator_id]):
                self.env['mail.activity'].create({
                    'res_model_id': self.env.ref('project.model_project_project').id,
                    'res_id': project.id,
                    'user_id': user.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': "Proyecto finalizado automáticamente",
                    'note': "El proyecto ha pasado automáticamente a la etapa Finalizado.",
                })


    @api.model
    def cron_notify_pending_rendition(self):
        """Notifica 15 días antes de rendición y cambia a 'Rendido' después de 60 días de fecha_str"""
        today = fields.Date.today()
        target_day = today + timedelta(days=15)

        # Solo proyectos en estado 'done'
        projects = self.search([('state_project', '=', 'done')])

        for project in projects:
            # Obtener el último pago con fecha_str (asumiendo One2many: pagos_ids)
            last_pago = project.pagos_ids.filtered(lambda p: p.fecha_str).sorted('fecha_str', reverse=True)[:1]

            if not last_pago:
                continue

            fecha_acreditacion = last_pago.fecha_str
            if not fecha_acreditacion:
                continue

            rendicion_day = fecha_acreditacion + timedelta(days=60)

            if rendicion_day == target_day:
                # Notificar 15 días antes
                for user in filter(None, [project.user_id, project.coordinator_id]):
                    self.env['mail.activity'].create({
                        'res_model_id': self.env.ref('project.model_project_project').id,
                        'res_id': project.id,
                        'user_id': user.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'summary': "Rendición próxima",
                        'note': "Recordatorio: El proyecto debe rendirse en 15 días.",
                    })
            elif rendicion_day <= today:
                # Cambiar estado automáticamente
                project.state_project = 'rendered'

    asignacion_ids = fields.One2many('asignacion.financiera.line', 'proyecto_id', string='Asignaciones Financieras')
    
class AsignacionFinancieraLine(models.Model):
    _name = 'asignacion.financiera.line'
    _description = 'Línea de Asignación Financiera'

    proyecto_id = fields.Many2one('project.project', string='Proyecto', ondelete='cascade', required=True)
    mes = fields.Selection([
        ('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'),
        ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'),
        ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Septiembre'),
        ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ], string='Mes', required=True)
    monto_asignado = fields.Monetary(string='Monto Asignado')
    monto_obligado = fields.Monetary(string='Monto Obligado')
    monto_pagado = fields.Monetary(string='Monto Pagado')
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True, default=lambda self: self.env.company.currency_id)




class ProjectPagos(models.Model):
    _inherit = "project.pagos"
    _description = "Pagos del Proyecto"

    project_id = fields.Many2one("project.project", string="Proyecto", required=True)

    resolucion_snd = fields.Many2one(
        "project.juridica",
        string="Resolución SND",
        domain="[('project_id', '=', project_id)]",
    )

    str_resolucion_snd = fields.Char(string="STR N°")
    fecha_str = fields.Date(string="Fecha de STR")
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    monto_obligado = fields.Monetary(
        string="Monto Obligado",
        currency_id="currency_id",
    )

    fecha_vencimiento_str = fields.Date(string="Fecha de Vencimiento de STR")

    @api.model
    def create(self, vals):
        record = super(ProjectPagos, self).create(vals)
        record._actualizar_linea_asignacion()
        return record

    def write(self, vals):
        res = super(ProjectPagos, self).write(vals)
        self._actualizar_linea_asignacion()
        return res

    def _actualizar_linea_asignacion(self):
        for pago in self:
            if not pago.fecha_str or not pago.project_id:
                continue

            mes = pago.fecha_str.strftime('%m')

            # Buscar línea existente
            asignacion_line = self.env['asignacion.financiera.line'].search([
                ('proyecto_id', '=', pago.project_id.id),
                ('mes', '=', mes)
            ], limit=1)

            if asignacion_line:
                asignacion_line.write({
                    'monto_obligado': pago.monto_obligado,
                })
            else:
                asignacion_line = self.env['asignacion.financiera.line'].create({
                    'proyecto_id': pago.project_id.id,
                    'mes': mes,
                    'monto_obligado': pago.monto_obligado,
                    'currency_id': pago.currency_id.id,
                })

            # Buscar proveedor y asignar monto pagado
            proveedor = self.env['project.proveedor'].search([
                ('project_id', '=', pago.project_id.id)
            ], limit=1)

            if proveedor:
                asignacion_line.write({
                    'monto_pagado': proveedor.monto_pagado
                })
