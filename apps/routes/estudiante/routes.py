from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_babel import gettext
from apps import logger
from apps.routes.estudiante import blueprint
from flask_login import login_required, current_user
from apps.lib.utils.errors import handle_errors
from apps.lib.decoradors.decoradors import solo_permitido_a
from apps.controls.dao_controls.actividad_dao import ActividadDAO
from apps.controls.dao_controls.resultado_test_dao import ResultadoTestDAO
from apps.controls.dao_controls.test_estres_dao import TestEstresDAO
from apps.controls.dao_controls.paralelo_dao import ParaleloDAO
from apps.controls.dao_controls.estudiante_dao import EstudianteDAO
from apps.controls.dao_controls.materia_dao import MateriaDAO

@blueprint.route("/")
@login_required
@handle_errors
@solo_permitido_a(estudiante=True)
def index():
    """{{ _('Página principal del estudiante') }}"""
    try:
        # Obtener actividades pendientes
        actividades = ActividadDAO().get_actividades_by_estudiante(current_user.uid)
        actividades_pendientes = []
        for actividad in actividades:
            if actividad.esta_activa and actividad.fecha_entrega:
                # Verificar si hay respuestas del estudiante
                estado = "pendiente"
                if actividad.link_test:
                    try:
                        respuestas = obtener_respuestas_formulario(actividad.test_estres)
                        if respuestas and 'responses' in respuestas:
                            for respuesta in respuestas['responses']:
                                if respuesta.get('respondentEmail') == current_user.correo:
                                    estado = "completada"
                                    break
                    except Exception as e:
                        logger.error(f"Error al obtener respuestas: {str(e)}")

                actividades_pendientes.append({
                    'nombre': actividad.nombre,
                    'paralelo_nombre': ParaleloDAO().get(actividad.paralelo_uid).nombre,
                    'fecha_entrega': actividad.fecha_entrega,
                    'es_obligatoria': actividad.es_obligatoria,
                    'link_test': actividad.link_test,
                    'estado': estado
                })
        
        # Ordenar por fecha de entrega y limitar a 5
        actividades_pendientes = sorted(
            actividades_pendientes, 
            key=lambda x: x['fecha_entrega'] if x['fecha_entrega'] else ""
        )[:5]
        
        # Obtener totales
        total_actividades = len(actividades_pendientes)
        total_tests = len([a for a in actividades_pendientes if a['es_obligatoria']])
        total_paralelos = len([p for p in ParaleloDAO().get_all if current_user.uid in p.estudiantes])
        nivel_estres = 0
        
        logger.info(gettext("✅ Accediendo a la página principal del estudiante"))
        return render_template(
            "dashboard/welcome_estudiante.html",
            total_actividades=total_actividades,
            total_tests=total_tests,
            total_paralelos=total_paralelos,
            nivel_estres=nivel_estres,
            actividades_pendientes=actividades_pendientes
        )
    except Exception as e:
        logger.error(f"❌ Error al cargar dashboard: {str(e)}")
        flash(gettext('Error al cargar dashboard: {}').format(str(e)), 'error')
        return render_template(
            "dashboard/welcome_estudiante.html",
            total_actividades=0,
            total_tests=0,
            total_paralelos=0,
            nivel_estres=0,
            actividades_pendientes=[]
        )

@blueprint.route("/calendario")
@login_required
@handle_errors
@solo_permitido_a(estudiante=True)
def calendario():
    """{{ _('Calendario de actividades académicas') }}"""
    logger.info(gettext("✅ Accediendo al calendario de actividades"))
    actividades = ActividadDAO().get_actividades_by_estudiante(current_user.uid)
    
    # Convertir actividades a diccionarios y formatear fechas
    actividades_dict = []
    for actividad in actividades:
        actividad_dict = actividad.to_dict
        # Asegurarse de que la fecha sea string en formato ISO
        if actividad_dict.get('fecha_entrega'):
            actividad_dict['fecha_entrega'] = actividad_dict['fecha_entrega'].isoformat() if hasattr(actividad_dict['fecha_entrega'], 'isoformat') else str(actividad_dict['fecha_entrega'])
        actividades_dict.append(actividad_dict)
    
    return render_template(
        "estudiante/calendario.html",
        actividades=actividades_dict
    )

@blueprint.route("/ver-actividades")
@login_required
@handle_errors
@solo_permitido_a(estudiante=True)
def ver_actividades():
    """{{ _('Ver listado de actividades') }}"""
    logger.info(gettext("✅ Accediendo al listado de actividades"))
    actividades = ActividadDAO().get_actividades_by_estudiante(current_user.uid)
    
    # Convertir actividades a diccionarios y formatear fechas
    actividades_dict = []
    for actividad in actividades:
        actividad_dict = actividad.to_dict
        # Asegurarse de que la fecha sea string en formato ISO
        if actividad_dict.get('fecha_entrega'):
            actividad_dict['fecha_entrega'] = actividad_dict['fecha_entrega'].isoformat() if hasattr(actividad_dict['fecha_entrega'], 'isoformat') else str(actividad_dict['fecha_entrega'])
        actividades_dict.append(actividad_dict)
    
    return render_template(
        "estudiante/ver_actividades.html",
        actividades=actividades_dict
    )

@blueprint.route("/ver-tests")
@login_required
@handle_errors
@solo_permitido_a(estudiante=True)
def ver_tests():
    """{{ _('Ver tests asignados') }}"""
    logger.info(gettext("✅ Accediendo a los tests asignados"))
    # Obtener actividades que tienen tests asociados
    actividades = ActividadDAO().get_actividades_by_estudiante(current_user.uid)
    
    # Convertir actividades a diccionarios y formatear fechas
    actividades_dict = []
    for actividad in actividades:
        if actividad.link_test:  # Solo incluir actividades con test
            actividad_dict = actividad.to_dict
            # Asegurarse de que la fecha sea string en formato ISO
            if actividad_dict.get('fecha_entrega'):
                actividad_dict['fecha_entrega'] = actividad_dict['fecha_entrega'].isoformat() if hasattr(actividad_dict['fecha_entrega'], 'isoformat') else str(actividad_dict['fecha_entrega'])
            actividades_dict.append(actividad_dict)
    
    return render_template(
        "estudiante/tests/ver_tests.html",
        actividades=actividades_dict
    )

from apps.lib.services.tests.test import obtener_respuestas_formulario
import re

@blueprint.route("/historial-tests")
@login_required
@handle_errors
@solo_permitido_a(estudiante=True)
def historial_tests():
    """{{ _('Historial de tests realizados') }}"""
    logger.info(gettext("✅ Accediendo al historial de tests"))
    
    # Obtener actividades que tienen tests asociados
    actividades = ActividadDAO().get_actividades_by_estudiante(current_user.uid)
    actividades_con_test = [
        actividad for actividad in actividades 
        if actividad.link_test
    ]
    
    # Obtener resultados de los formularios
    resultados = []
    for actividad in actividades_con_test:
        try:
            # Extraer el ID del formulario del link
            # Manejar diferentes formatos de URL de Google Forms
            form_id = None
            if 'forms.gle' in actividad.link_test:
                match = re.search(r'forms\.gle/([^/\s]+)', actividad.link_test)
                if match:
                    form_id = match.group(1)
            elif '/forms/d/' in actividad.link_test:
                match = re.search(r'/forms/d/([^/\s]+)', actividad.link_test)
                if match:
                    form_id = match.group(1)
            elif '/d/' in actividad.link_test:
                match = re.search(r'/d/([^/\s]+)', actividad.link_test)
                if match:
                    form_id = match.group(1)

            if form_id:
                try:
                    respuestas = obtener_respuestas_formulario(form_id)
                    if respuestas and 'responses' in respuestas:
                        for respuesta in respuestas['responses']:
                            resultado = {
                                'nombre': actividad.nombre,
                                'descripcion': actividad.descripcion,
                                'fecha_realizacion': respuesta.get('createTime', ''),
                                'respuestas': respuesta.get('answers', {})
                            }
                            resultados.append(resultado)
                except Exception as e:
                    logger.error(f"Error al obtener respuestas del formulario {form_id}: {str(e)}")
            else:
                logger.warning(f"No se pudo extraer el ID del formulario del link: {actividad.link_test}")
        except Exception as e:
            logger.error(f"Error al procesar la actividad {actividad.nombre}: {str(e)}")
    
    return render_template(
        "estudiante/tests/historial_tests.html",
        resultados=resultados
    )

@blueprint.route("/recomendaciones")
@login_required
@handle_errors
def recomendaciones():
    """{{ _('Recomendaciones para manejo del estrés') }}"""
    logger.info(gettext("✅ Accediendo a las recomendaciones"))
    return render_template(
        "estudiante/recomendaciones/recomendaciones.html"
    )

@blueprint.route("/actividades-fisicas")
@login_required
@handle_errors
def actividades_fisicas():
    """{{ _('Actividades físicas recomendadas') }}"""
    logger.info(gettext("✅ Accediendo a las actividades físicas"))
    return render_template(
        "estudiante/recomendaciones/actividades_fisicas.html"
    )

@blueprint.route("/contactos-bienestar")
@login_required
@handle_errors
def contactos_bienestar():
    """{{ _('Contactos de Bienestar Académico') }}"""
    logger.info(gettext("✅ Accediendo a los contactos de bienestar"))
    return render_template(
        "estudiante/recomendaciones/contactos_bienestar.html"
    )

@blueprint.route("/canal-ayuda")
@login_required
@handle_errors
def canal_ayuda():
    """{{ _('Canal de ayuda para estudiantes') }}"""
    logger.info(gettext("✅ Accediendo al canal de ayuda"))
    return render_template(
        "estudiante/canal_ayuda.html"
    )

@blueprint.route("/solicitar-ayuda", methods=['POST'])
@login_required
@handle_errors
def solicitar_ayuda():
    """{{ _('Procesar solicitud de ayuda') }}"""
    logger.info(gettext("✅ Procesando solicitud de ayuda"))
    # Aquí iría la lógica para procesar la solicitud
    flash(gettext('Tu solicitud ha sido enviada. Nos pondremos en contacto contigo pronto.'), 'success')
    return redirect(url_for('estudiante.canal_ayuda'))

@blueprint.route("/ver-paralelos")
@login_required
@handle_errors
@solo_permitido_a(estudiante=True)
def ver_paralelos():
    """{{ _('Ver paralelos del estudiante') }}"""
    try:
        # Obtener paralelos donde el estudiante está inscrito
        paralelos = [paralelo.to_dict for paralelo in ParaleloDAO().get_all if current_user.uid in paralelo.estudiantes]
        
        # Obtener materias asociadas
        materias = {materia.uid: materia.to_dict for materia in MateriaDAO().get_all}
        
        logger.info(gettext("✅ Accediendo a la lista de paralelos"))
        return render_template(
            "estudiante/ver_paralelos.html",
            paralelos=paralelos,
            materias=materias
        )
    except Exception as e:
        logger.error(f"❌ Error al obtener paralelos: {str(e)}")
        flash(gettext('Error al obtener paralelos: {}').format(str(e)), 'error')
        return redirect(url_for('estudiante.index'))

@blueprint.route("/compartir-resultados/<int:resultado_id>", methods=['POST'])
@login_required
@handle_errors
@solo_permitido_a(estudiante=True)
def compartir_resultados(resultado_id):
    """{{ _('Compartir resultados por correo') }}"""
    logger.info(gettext("✅ Compartiendo resultados de test"))
    resultado = ResultadoTestDAO().get_by_id(resultado_id)
    if resultado and resultado.estudiante_id == current_user.id:
        # Aquí iría la lógica para enviar el correo
        flash(gettext('Resultados compartidos exitosamente'), 'success')
    else:
        flash(gettext('No se encontró el resultado o no tienes permiso para compartirlo'), 'error')
    return redirect(url_for('estudiante.historial_tests'))
