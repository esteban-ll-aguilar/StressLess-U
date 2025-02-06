# -*- encoding: utf-8 -*-
"""
Authentication Routes
"""

from flask import render_template, redirect, request, url_for, jsonify, flash
from flask_login import current_user, logout_user, login_required
from flask_babel import gettext
from apps import login_manager
from apps.routes.authentication import blueprint
from apps.routes.authentication.forms import LoginForm
from apps.routes.authentication.services import AuthService
from apps.config import Config
from apps.lib.utils.errors import handle_errors
from apps.lib.decoradors.decoradors import solo_permitido_a
from apps.lib.services.auth.auth_google_forms import get_google_flow, save_credentials, verify_credentials

import json
import logging
import pickle
import os
from dotenv import load_dotenv
load_dotenv()

SCOPES = os.getenv('GOOGLE_OAUTH_SCOPES','').split(',')

# {{ _('Configurar logging') }}
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# {{ _('Inicializar servicio de autenticación') }}
AUTH_SERVICE = AuthService()

@blueprint.route('/')
@handle_errors
def route_default():
    """{{ _('Ruta por defecto') }}"""
    url = url_for('home_blueprint.index')
    if current_user.is_authenticated and current_user.rol == 'administrador':
        url = url_for('administrador.index')
    elif current_user.is_authenticated and current_user.rol == 'docente':
        url = url_for('docente.index')
    elif current_user.is_authenticated and current_user.rol == 'estudiante':
        url = url_for('estudiante.index')
    else:
        url = url_for('autenticacion.login')

    return redirect(url)

@blueprint.route('/login', methods=['GET', 'POST'])
@handle_errors
def login():
    """{{ _('Ruta de inicio de sesión') }}"""
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))

    login_form = LoginForm(request.form)

    if request.method == 'POST':
        if request.content_type == 'application/json':
            # {{ _('Login con token de Firebase') }}
            if not request.is_json:
                return jsonify({'error': gettext('Invalid JSON request')}), 400
            
            json_data = request.get_json()
            if not json_data:
                return jsonify({'error': gettext('No JSON data provided')}), 400

            id_token = json_data.get('idToken')
            if not id_token:
                return jsonify({'error': gettext('ID token not provided')}), 400

            success, error = AUTH_SERVICE.process_firebase_token(id_token)
            if success:
                return jsonify({'success': True, 'redirect': url_for('home_blueprint.index')}), 200
            else:
                return jsonify({'error': gettext('Authentication error') + f': {error}'}), 500

    return render_template('accounts/login.html',
                         form=login_form,
                         firebase_config=json.dumps(Config.FIREBASE_CONFIG))



@blueprint.route('/olvido-contrasena', methods=['GET', 'POST'])
@handle_errors
def olvido_contrasena():
    if request.method == 'POST':
        email = request.form.get('email')
        AUTH_SERVICE.send_password_reset_email(email)
        flash(gettext('Se te ha enviado un correo para restablecer tu contraseña'), 'info')
        return redirect(url_for('autenticacion.olvido_contrasena'))
    return render_template('accounts/olvido_contrasena.html')










@blueprint.route('/logout')
@handle_errors
def logout():
    """{{ _('Ruta de cierre de sesión') }}"""
    logout_user()
    logger.info("User logged out")
    flash(gettext('You have successfully logged out'), 'success')
    return redirect(url_for('autenticacion.login'))

@blueprint.route("/authenticacion-google-forms")
@login_required
@handle_errors
@solo_permitido_a(administrador=True, docente=True)
def authenticacion_google_forms():
    """{{ _('Autenticación con Google Forms') }}"""
    try:
        # Verificar credenciales
        is_valid, _ = verify_credentials()
        if is_valid:
            flash(gettext('Ya estás autenticado con Google Forms'), 'info')
            return redirect(url_for('home_blueprint.index'))
        # Iniciar flujo de autenticación
        flow = get_google_flow()
        auth_url, _ = flow.authorization_url()
        return redirect(auth_url)

    except Exception as e:
        logger.error(f"❌​ ​Error en autenticación de Google Forms: {str(e)}")
        flash(gettext('Error al iniciar autenticación con Google Forms'), 'error')
        return redirect(url_for('home_blueprint.index'))

@blueprint.route('/oauth2callback')
@login_required
@handle_errors
@solo_permitido_a(administrador=True, docente=True)
def oauth2callback():
    """{{ _('Callback de OAuth2 para Google Forms') }}"""
    try:
        # Configurar flujo OAuth 2.0
        flow = get_google_flow()
        
        # Obtener credenciales
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Guardar credenciales
        try:
            save_credentials(credentials)
        except Exception as e:
            logger.error(f"❌​ ​Error al guardar credenciales: {str(e)}")
            raise
        
        flash(gettext('Autenticación con Google Forms completada exitosamente'), 'success')
        return redirect(url_for('home_blueprint.index'))

    except Exception as e:
        logger.error(f"❌​ ​Error en callback de OAuth: {str(e)}")
        flash(gettext(f'Error en la autenticación con Google Forms {str(e)}'), 'error')
        return redirect(url_for('home_blueprint.index'))






@login_manager.unauthorized_handler
def unauthorized_handler():
    """{{ _('Manejador de accesos no autorizados') }}"""
    logger.warning("Unauthorized access attempt")
    flash(gettext('Unauthorized access. Please log in.'), 'warning')
    return redirect(url_for('autenticacion.login'))

@blueprint.errorhandler(403)
def access_forbidden(error):
    """{{ _('Manejador de errores 403') }}"""
    logger.warning("Error 403: Access forbidden")
    flash(gettext('Access forbidden. You do not have permission to access this page.'), 'danger')
    return render_template('home/page-403.html'), 403
