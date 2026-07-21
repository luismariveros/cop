# -*- coding: utf-8 -*-

from . import models


def uninstall_hook(cr, registry):
    cr.execute("DELETE FROM ir_model_data WHERE module = 'eterp_paraguay'")
