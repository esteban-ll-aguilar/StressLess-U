# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Blueprint
from apps import db # Importar la instancia de Firestore ya inicializada

# Importar funciones del modelo de usuario

blueprint = Blueprint(
    'administrador',
    __name__,
    url_prefix='/administrador'
)

# Importar vistas después de crear el blueprint para evitar importaciones circulares
from . import routes
