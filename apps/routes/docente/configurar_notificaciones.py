from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_babel import gettext
from apps import logger
from flask_login import login_required, current_user
from apps.lib.utils.errors import handle_errors
from apps.lib.decoradors.decoradors import solo_permitido_a
from apps.lib.services.tests.test import list_google_forms
from apps.lib.services.tests.apps_script_service import configurar_notificaciones_form

def configurar_notificaciones_route():
    """{{ _('Configurar notificaciones para formularios existentes') }}"""
    try:
        # Obtener todos los formularios del docente
        formularios = list_google_forms()
        
        if request.method == 'POST':
            form_id = request.form.get('form_id')
            if form_id:
                if configurar_notificaciones_form(form_id):
                    flash(gettext('Notificaciones configuradas exitosamente'), 'success')
                else:
                    flash(gettext('Error al configurar las notificaciones'), 'error')
                return redirect(url_for('docente.configurar_notificaciones'))
        
        return render_template(
            'docente/configurar_notificaciones.html',
            formularios=formularios
        )
    except Exception as e:
        logger.error(f"Error al configurar notificaciones: {str(e)}")
        flash(gettext('Error al cargar los formularios'), 'error')
        return redirect(url_for('docente.index'))
