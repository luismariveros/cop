# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from pytz import timezone, UTC
from datetime import datetime


# Modelo para Control OG 879
class GestionControl879(models.Model):
    _name = "gestion.control.879"
    _description = "Control OG 879 - Transferencias de Capital al Sector Privado"

    gestion_operacional_id = fields.Many2one(
        "gestion.operacional", string="Gestión Operacional"
    )

    # Estados de cumplimiento
    ESTADOS_CUMPLIMIENTO = [
        ("cumple", "Cumple"),
        ("no_cumple", "No Cumple"),
        ("no_aplica", "No Aplica"),
    ]

    # Información general

    observaciones = fields.Text(string="Observaciones")

    # Art 6: Control 879
    art6_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="a) Programas o Proyectos Deportivos o cualquier tipo de eventos financiados por el Objeto de Gasto 879",
    )

    art7_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="a) Para Entidades Inscriptas en el Registro de Entidades Deportivas: La Nota deberá estar suscripta (con firmas originales) por representantes autorizados conforme a las normativas vigentes...",
    )
    art7_2 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Formulario de Elaboración de Proyectos - Ficha Técnica (con firmas originales) (Anexo II)",
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
    # Art 10 (para OG 879)
    art10_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string='Para las transferencias de capital imputables al Objeto del Gasto 879, sólo se podrán programar gastos de inversión destinados a los "IV Juegos Latinoamericanos de Olimpiadas Especiales 2024 y II Juegos Panamericanos Junior 2025".',
    )
    art10_2 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Obras contempladas en el Convenio Marco Aprobado"
    )

    # Anexos de obras (para OG 879)
    anexo12 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Anexo XII: Aprobación del proyecto de obras"
    )
    anexo13 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Anexo XIII: Pago del proyecto de obras"
    )
    anexo14 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Anexo XIV: Resumen del certificado de obras"
    )
    anexo15 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Anexo XV: Certificado de obras"
    )
    anexo16 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Anexo XVI: Presupuesto de obra"
    )
    anexo17 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Anexo XVII: Cronograma físico-financiero"
    )
    anexo18 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Anexo XVIII: Fotografías de las obras"
    )

    # Art 11: Pólizas de seguros
    art11_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Póliza de Ejecución del contrato (10%)"
    )
    art11_2 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Póliza de Anticipo Financiero (anticipo de hasta 20% y asegurado al 100%)",
    )
    art11_3 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="c) Póliza de Seguro de Responsabilidad Civil."
    )
    art11_4 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="d) Póliza de Seguro Contra Todo Riesgo Contratista.",
    )
    art11_5 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="e) Póliza de Seguro por Accidentes Personales (conforme a cantidad de personal y salarios).",
    )
    art11_6 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Ampliación de Garantía por cambios en cronograma"
    )
    art11_7 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Entrega de pólizas a la UEP dentro de 5 días"
    )

    # Art 15 (común)
    art15_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO,
        string="Para la adquisición de bienes y servicios u obras a partir de Gs.: 4.999.999.-, las Entidades deberán realizar un proceso competitivo de adquisión con por lo menos 3 (tres) presupuestos que deberán contener los siguientes datos verificables...",
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
        ESTADOS_CUMPLIMIENTO,
        string="c) En caso de productos o bienes adquiridos de un representante exclusivo se deberá acompañar una nota de aclaración emitida y firmada por el proveedor o documento que lo acredite...",
    )
    # Art 18 (común)
    art18_1 = fields.Selection(
        ESTADOS_CUMPLIMIENTO, string="Uso del logo de UEP, SND y otras entidades"
    )
