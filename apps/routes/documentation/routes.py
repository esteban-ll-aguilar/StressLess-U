from flask import render_template
from flask_babel import gettext
from apps import logger
from apps.routes.documentation import blueprint

@blueprint.route("/")
def index():
    """{{ _('Página principal de documentación') }}"""
    return render_template("documentation/index.html")

@blueprint.route("/google-forms")
def google_forms():
    """{{ _('Documentación de Google Forms') }}"""
    return render_template("documentation/google_forms.html")

@blueprint.route("/notificaciones")
def notificaciones():
    """{{ _('Documentación de notificaciones') }}"""
    return render_template("documentation/notificaciones.html")

@blueprint.route("/api")
def api():
    """{{ _('Documentación de la API') }}"""
    return render_template("documentation/api.html")
