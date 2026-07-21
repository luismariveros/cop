# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from pytz import timezone, UTC
from datetime import datetime


# Modelo para Control OG 839
class GestionControl839(models.Model):
    _name = "gestion.control.839"
    _description = "Control OG 839 - Otras Transferencias Corrientes"

    gestion_operacional_id = fields.Many2one(
        "gestion.operacional", string="Gestión Operacional"
    )

    # Estados de cumplimiento
    ESTADOS_CUMPLIMIENTO = [
        ("cumple", "Cumple"),
        ("no_cumple", "No Cumple"),
        ("no_aplica", "No Aplica"),
    ]

    observaciones = fields.Text(string="Observaciones")

    # Art 6: Control 839
    art6_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Programas/Proyectos financiados por OG 839: Presentado hasta el 10 del mes de evaluación",
    )

    art7_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Entidades con Registro: Nota con firmas autorizadas, identificación del nombre del proyecto",
    )
    art7_2 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Formulario de Proyectos - Ficha Técnica con (con firmas originales)(Anexo II)",
    )
    art7_3 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Copia de acta de Comisión Directiva aprobando subvención",
    )
    art7_4 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Formulario B-01-01B: Programación de Ingresos (Anexo III)",
    )
    art7_5 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Formulario B-01-01C: Programación de Gastos (Anexo IV)",
    )
    art7_6 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Formulario B-01-01D: Planificación de Servicios (Anexo V)",
    )
    art7_7 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Constancia de Inscripción en el IDAP"
    )
    art7_8 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Copia del Registro Único del Contribuyente (RUC)"
    )
    art7_9 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Copia de Cédula Tributaria y Perfil del Contribuyente",
    )
    art7_10 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Certificado vigente de Cuenta Bancaria"
    )

    # Art 8: Específico para OG 839
    art8_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Programa o calendario del evento deportivo"
    )
    art8_2 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Documentación para pasajes y hospedaje"
    )
    art8_3 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Escala de pagos para servicios personales"
    )
    art8_4 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Listado de beneficiarios con copia de títulos de grado o tecnicatura...",
    )
    art8_5 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Contratación bajo OG 260 (Servicios Técnicos Profesionales), máximo Gs.:40.000.000",
    )
    art8_6 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Solicitud de indumentaria deportiva que no supere los Gs.:4.999.999",
    )
    art8_7 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Solicitud de compra de combustible, con proyección de uso",
    )
    art8_8 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Para solicitar subvenciones destinadas a la realización de capacitaciones...",
    )
    art8_9 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Para contratación de consultorías de mínimo tres postulantes",
    )

    # Art 15 (común para ambos controles)
    art15_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Adquisición de bienes o servicios desde Gs. 4.999.999 con los datos verificables",
    )
    art15_2 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Cuadro comparativo de ofertas - Formulario B 02-08 (Anexo IX) con el respectivo proyecto.",
    )
    art15_3 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="a) Prestaciones de servicios que alcancen el monto de Gs.: 4.999.999.-",
    )
    art15_4 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="b) Compras de un mismo proveedor, dentro del mismo mes, cuyo importe individual o la sumatoria de ésta alcancen o superen la suma de Gs.: 4.999.999.-",
    )
    art15_5 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Nota de representante exclusivo del proveedor"
    )

    # Art 16 (común)-
    art16_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Para solicitar subvenciones en moneda extranjera, se considerará el tipo de cambio publicado por el BCP, a la fecha declarada en la Ficha Técnica de Elaboración del Proyecto.",
    )

    # Art 17 (común)
    art17_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Las solicitudes de financiamiento para la provisión de viáticos al interior y exterior del país se regirán conforme a las Tabla de Valores de Viáticos al Interior (Formulario B-03-01) y Tabla de Valores de Viáticos para el exterior del país (Formulario B-03-02)",
    )

    # Art 18 (común)
    art18_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Uso del logo de UEP, SND y otras entidades"
    )
