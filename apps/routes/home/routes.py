# -*- encoding: utf-8 -*-
"""
Home Routes Module
"""

from apps.routes.home import blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound
from flask_babel import refresh, gettext
import logging
from apps.routes.authentication.services import AuthService
from apps.lib.decoradors.decoradors import solo_permitido_a

logger = logging.getLogger(__name__)
auth_service = AuthService()

@blueprint.route('/')
@login_required
def index():
    """{{ _('Ruta principal que redirige al dashboard') }}"""
    logger.info(gettext("User {} accessing home page").format(current_user.uid))
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






@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
@solo_permitido_a(administrador=True, docente=True, estudiante=True)
def profile():
    """{{ _('Gestión del perfil de usuario') }}"""
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            success, error = auth_service.update_user_settings(current_user.uid, data)
            
            if success:
                refresh()  # Refrescar configuración de idioma
                flash(gettext("Profile updated successfully"), 'success')
            else:
                flash(gettext("Error updating profile: {}").format(error), 'danger')
            
            return redirect(url_for('home_blueprint.profile'))
        except Exception as e:
            logger.error(gettext("Error updating profile: {}").format(str(e)))
            flash(gettext("Error updating profile"), 'danger')
            return redirect(url_for('home_blueprint.profile'))

    logger.info(gettext("User {} accessing their profile").format(current_user.uid))
    return render_template('accounts/profile/profile.html', user=current_user)

#/auth/update_layout/
@blueprint.route('/update_layout', methods=['POST'])
@login_required
def update_layout():
    try:
        data = request.get_json()
        success, error = auth_service.update_user_layout(current_user.uid, data['layout'])
        if success:
            flash(gettext("Layout updated successfully"), 'success')
        else:
            flash(gettext("Error updating layout: {}").format(error), 'danger')
        return redirect(url_for('home_blueprint.profile'))
    except Exception as e:
        logger.error(gettext("Error updating layout: {}").format(str(e)))
        flash(gettext("Error updating layout"), 'danger')
        return redirect(url_for('home_blueprint.profile'))
    



@blueprint.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """{{ _('Actualizar el perfil del usuario') }}"""
    data = request.form.to_dict()
    print(data)
    success, error = auth_service.update_user(current_user.uid, data)
    if success:
        flash(gettext("Profile updated successfully"), 'success')
    else:   
        flash(gettext("Error updating profile: {}").format(error), 'danger')
    return redirect(url_for('home_blueprint.profile'))
    




@blueprint.route('/components')
def components():
    """{{ _('Ruta principal que redirige al dashboard') }}"""
    return render_template('home/index.html')


@blueprint.route('/<template>')
def route_template(template):
    """{{ _('Manejador dinámico de templates') }}"""
    try:
        if not template.endswith('.html'):
            template += '.html'

        segment = get_segment(request)
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        logger.error(gettext("Template not found: {}").format(template))
        return render_template('home/page-404.html'), 404
    except Exception as e:
        logger.error(gettext("Error rendering template {}: {}").format(template, str(e)))
        return render_template('home/page-500.html'), 500


def get_segment(request):
    """{{ _('Extraer el nombre de la página actual de la petición') }}"""
    try:
        segment = request.path.split('/')[-1]
        return segment if segment else 'index'
    except Exception as e:
        logger.error(gettext("Error getting segment: {}").format(str(e)))
        return None


