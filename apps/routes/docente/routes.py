from flask import render_template, jsonify, redirect, url_for, flash, request
from flask_babel import gettext
from apps import logger
from apps.routes.docente import blueprint
from flask_login import login_required, current_user
from apps.lib.utils.errors import handle_errors
from apps.lib.decoradors.decoradors import solo_permitido_a
from apps.controls.dao_controls.paralelo_dao import ParaleloDAO
from apps.controls.dao_controls.materia_dao import MateriaDAO
from apps.controls.dao_controls.actividad_dao import ActividadDAO
from apps.controls.dao_controls.estudiante_dao import EstudianteDAO
from apps.controls.dao_controls.test_estres_dao import TestEstresDAO
from apps.controls.dao_controls.resultado_test_dao import ResultadoTestDAO
from apps.controls.dao_controls.notificacion_dao import NotificacionDAO
from apps.lib.services.tests.test import list_google_forms, duplicar_formulario, compartir_formulario_varios_correo, obtener_link_respuesta, obtener_respuestas_formulario
from datetime import datetime
import json
from flask_mail import Message
from apps import mail
from .configurar_notificaciones import configurar_notificaciones_route

# Registrar la ruta de configuración de notificaciones
blueprint.add_url_rule('/configurar-notificaciones', 'configurar_notificaciones', 
                      configurar_notificaciones_route, methods=['GET', 'POST'])

@blueprint.route("/")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def index():
    """{{ _('Ruta principal del dashboard') }}"""
    logger.info(gettext("✅ Accediendo a la página principal del dashboard"))
    
    return render_template(
        "dashboard/welcome_docente.html",
    )

@blueprint.route("/calendario")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def calendario():
    """{{ _('Ver calendario académico') }}"""
    try:
        # Obtener paralelos donde el docente es el actual
        paralelos = [paralelo.to_dict for paralelo in ParaleloDAO().get_all_documents_by_attribute("docente_uid", current_user.uid)]
        
        # Obtener todas las materias
        materias = {materia.uid: materia.to_dict for materia in MateriaDAO().get_all}
        
        # Obtener todos los estudiantes de los paralelos
        estudiantes = []
        estudiante_dao = EstudianteDAO()
        for paralelo in paralelos:
            for uid in paralelo['estudiantes']:
                estudiante = estudiante_dao.get(uid)
                if estudiante:
                    estudiantes.append(estudiante.to_dict)
        
        # Obtener la lista de formularios de Google
        google_forms = list_google_forms()
        if google_forms is None:
            flash(gettext('Error al obtener los formularios de Google'), 'error')
            return redirect(url_for('docente.index'))
        
        logger.info(gettext("✅ Accediendo al calendario académico"))
        return render_template(
            "docente/calendario.html",
            paralelos=paralelos,
            materias=materias,
            estudiantes=estudiantes,
            google_forms=google_forms
        )
    except Exception as e:
        logger.error(f"❌ Error al acceder al calendario: {str(e)}")
        flash(gettext('Error al acceder al calendario: {}').format(str(e)), 'error')
        return redirect(url_for('docente.index'))

@blueprint.route("/actividades/calendario")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def obtener_actividades_calendario():
    """{{ _('Obtener actividades para el calendario') }}"""
    try:
        # Obtener todos los paralelos del docente
        paralelos = ParaleloDAO().get_all_documents_by_attribute("docente_uid", current_user.uid)
        paralelo_uids = [paralelo.uid for paralelo in paralelos]
        
        # Obtener actividades de todos los paralelos del docente
        actividades = []
        for paralelo_uid in paralelo_uids:
            actividades_paralelo = ActividadDAO().get_all_documents_by_attribute("paralelo_uid", paralelo_uid)
            actividades.extend(actividades_paralelo)
        
        try:
            # Formatear actividades para el calendario
            eventos = []
            logger.info(f"Total de actividades encontradas: {len(actividades)}")
            
            for actividad in actividades:
                logger.info(f"Procesando actividad: {actividad.uid} - {actividad.nombre}")
                logger.info(f"Fecha entrega: {actividad.fecha_entrega}")
                
                if not actividad.fecha_entrega:
                    logger.warning(f"Actividad {actividad.uid} no tiene fecha de entrega")
                    continue
                
                evento = {
                    'id': actividad.uid,
                    'title': actividad.nombre,
                    'description': actividad.descripcion or '',
                    'start': actividad.fecha_entrega,
                    'end': actividad.fecha_entrega,
                    'paralelo_uid': actividad.paralelo_uid,
                    'backgroundColor': '#4680ff',
                    'borderColor': '#4680ff',
                    'allDay': True,  # Para asegurar que se muestre en el calendario
                    'test_estres': actividad.test_estres,
                    'link_test': actividad.link_test,
                    'es_grupal': actividad.es_grupal,
                    'estudiantes': actividad.estudiantes,
                    'esta_activa': actividad.esta_activa,
                    'es_obligatoria': actividad.es_obligatoria
                }
                logger.info(f"Evento formateado: {evento}")
                eventos.append(evento)
            
            logger.info(f"Total de eventos formateados: {len(eventos)}")
            return jsonify(eventos)
        except Exception as e:
            logger.error(f"Error al formatear eventos: {str(e)}")
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"❌ Error al obtener actividades: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blueprint.route("/actividades/crear", methods=['POST'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def crear_actividad_calendario():
    """{{ _('Crear una nueva actividad desde el calendario') }}"""
    try:
        data = request.get_json()
        
        # Verificar que el paralelo pertenezca al docente
        paralelo = ParaleloDAO().get(data['paralelo_uid'])
        if not paralelo or paralelo.docente_uid != current_user.uid:
            return jsonify({'success': False, 'error': gettext('No tiene permiso para crear actividades en este paralelo')}), 403
        
        # Crear la actividad
        actividad_dao = ActividadDAO()
        actividad_dao._actividad.nombre = data['title']
        actividad_dao._actividad.descripcion = data.get('description', '')
        actividad_dao._actividad.fecha_entrega = data['start']
        actividad_dao._actividad.esta_activa = data.get('esta_activa', True)
        actividad_dao._actividad.paralelo_uid = data['paralelo_uid']
        actividad_dao._actividad.test_estres = data.get('test_estres', '')
        actividad_dao._actividad.es_grupal = data.get('es_grupal', False)
        actividad_dao._actividad.estudiantes = data.get('estudiantes', []) if data.get('es_grupal', False) else []
        actividad_dao._actividad.es_obligatoria = data.get('es_obligatoria', False)
        
        # Duplicar y compartir el formulario si se especificó uno
        if data.get('test_estres'):
            nuevo_form_id = duplicar_formulario(data['test_estres'], data['title'])
            if not nuevo_form_id:
                return jsonify({'success': False, 'error': gettext('Error al duplicar el formulario')}), 500
            
            # Obtener el link de respuesta
            link_test = obtener_link_respuesta(nuevo_form_id)
            if not link_test:
                return jsonify({'success': False, 'error': gettext('Error al obtener el link del formulario')}), 500
            
            
            # Obtener los correos de los estudiantes
            estudiantes_correos = []
            if data.get('es_grupal', False):
                # Si es grupal, solo compartir con los estudiantes seleccionados
                estudiante_dao = EstudianteDAO()
                for uid in data.get('estudiantes', []):
                    estudiante = estudiante_dao.get(uid)
                    if estudiante:
                        estudiantes_correos.append(estudiante.correo)
            else:
                # Si no es grupal, compartir con todos los estudiantes del paralelo
                paralelo = ParaleloDAO().get(data['paralelo_uid'])
                for uid in paralelo.estudiantes:
                    estudiante = EstudianteDAO().get(uid)
                    if estudiante:
                        estudiantes_correos.append(estudiante.correo)
            
            # Compartir el formulario con los estudiantes
            if not compartir_formulario_varios_correo(nuevo_form_id, estudiantes_correos, 'reader'):
                return jsonify({'success': False, 'error': gettext('Error al compartir el formulario')}), 500
            
            actividad_dao._actividad.test_estres = nuevo_form_id
            actividad_dao._actividad.link_test = link_test
        
        actividad_dao.save
        
        return jsonify({'success': True, 'id': actividad_dao._actividad.uid})
    except Exception as e:
        logger.error(f"❌ Error al crear actividad: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blueprint.route("/actividades/<uid>/actualizar", methods=['PUT'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def actualizar_actividad_calendario(uid):
    """{{ _('Actualizar una actividad desde el calendario') }}"""
    try:
        actividad = ActividadDAO().get(uid)
        if not actividad:
            return jsonify({'success': False, 'error': gettext('Actividad no encontrada')}), 404
        
        # Verificar que el paralelo pertenezca al docente
        paralelo = ParaleloDAO().get(actividad.paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            return jsonify({'success': False, 'error': gettext('No tiene permiso para modificar esta actividad')}), 403
        
        data = request.get_json()
        # Actualizar la actividad
        actividad_dao = ActividadDAO()
        actividad_dao._actividad = actividad
        actividad_dao._actividad.nombre = data['title']
        actividad_dao._actividad.descripcion = data.get('description', '')
        actividad_dao._actividad.fecha_entrega = data['start']
        actividad_dao._actividad.paralelo_uid = data['paralelo_uid']
        actividad_dao._actividad.esta_activa = data.get('esta_activa', True)
        actividad_dao._actividad.es_grupal = data.get('es_grupal', False)
        actividad_dao._actividad.estudiantes = data.get('estudiantes', []) if data.get('es_grupal', False) else []
        actividad_dao._actividad.es_obligatoria = data.get('es_obligatoria', False)
        
        # Si se cambió el formulario, duplicar y compartir el nuevo
        if data.get('test_estres') and data['test_estres'] != actividad.test_estres:
            nuevo_form_id = duplicar_formulario(data['test_estres'], data['title'])
            if not nuevo_form_id:
                return jsonify({'success': False, 'error': gettext('Error al duplicar el formulario')}), 500
            
            # Obtener el link de respuesta
            link_test = obtener_link_respuesta(nuevo_form_id)
            if not link_test:
                return jsonify({'success': False, 'error': gettext('Error al obtener el link del formulario')}), 500
            
            # Obtener los correos de los estudiantes
            estudiantes_correos = []
            if data.get('es_grupal', False):
                # Si es grupal, solo compartir con los estudiantes seleccionados
                estudiante_dao = EstudianteDAO()
                for uid in data.get('estudiantes', []):
                    estudiante = estudiante_dao.get(uid)
                    if estudiante:
                        estudiantes_correos.append(estudiante.correo)
            else:
                # Si no es grupal, compartir con todos los estudiantes del paralelo
                paralelo = ParaleloDAO().get(data['paralelo_uid'])
                actividad_dao._actividad.estudiantes = paralelo.estudiantes
                for uid in paralelo.estudiantes:
                    estudiante = EstudianteDAO().get(uid)
                    if estudiante:
                        estudiantes_correos.append(estudiante.correo)
            
            # Compartir el formulario con los estudiantes
            if not compartir_formulario_varios_correo(nuevo_form_id, estudiantes_correos, 'reader'):
                return jsonify({'success': False, 'error': gettext('Error al compartir el formulario')}), 500
            
            actividad_dao._actividad.test_estres = nuevo_form_id
            actividad_dao._actividad.link_test = link_test
        
        actividad_dao.update
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌ Error al actualizar actividad: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blueprint.route("/actividades/<uid>/actualizar-fechas", methods=['PUT'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def actualizar_fechas_actividad(uid):
    """{{ _('Actualizar fechas de una actividad (drag & drop)') }}"""
    try:
        actividad = ActividadDAO().get(uid)
        if not actividad:
            return jsonify({'success': False, 'error': gettext('Actividad no encontrada')}), 404
        
        # Verificar que el paralelo pertenezca al docente
        paralelo = ParaleloDAO().get(actividad.paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            return jsonify({'success': False, 'error': gettext('No tiene permiso para modificar esta actividad')}), 403
        
        data = request.get_json()
        
        # Actualizar fechas
        actividad_dao = ActividadDAO()
        actividad_dao._actividad = actividad
        actividad_dao._actividad.fecha_entrega = data['start']
        
        actividad_dao.update
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌ Error al actualizar fechas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blueprint.route("/notificaciones")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def ver_notificaciones():
    """{{ _('Ver notificaciones del docente') }}"""
    try:
        # Obtener todas las notificaciones del docente
        notificaciones = NotificacionDAO().get_by_docente(current_user.uid)
        
        logger.info(gettext("✅ Accediendo a las notificaciones"))
        return render_template(
            "docente/notificaciones.html",
            notificaciones=notificaciones
        )
    except Exception as e:
        logger.error(f"❌ Error al obtener notificaciones: {str(e)}")
        flash(gettext('Error al obtener notificaciones: {}').format(str(e)), 'error')
        return redirect(url_for('docente.index'))

@blueprint.route("/notificaciones/<uid>/marcar-leida", methods=['POST'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def marcar_notificacion_leida(uid):
    """{{ _('Marcar una notificación como leída') }}"""
    try:
        # Verificar que la notificación pertenezca al docente
        notificacion = NotificacionDAO().get(uid)
        if not notificacion or notificacion.docente_uid != current_user.uid:
            return jsonify({'success': False, 'error': gettext('No tiene permiso para modificar esta notificación')}), 403
        
        # Marcar como leída
        NotificacionDAO().marcar_como_leida(uid)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌ Error al marcar notificación como leída: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blueprint.route("/notificaciones/marcar-todas-leidas", methods=['POST'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def marcar_todas_notificaciones_leidas():
    """{{ _('Marcar todas las notificaciones como leídas') }}"""
    try:
        NotificacionDAO().marcar_todas_como_leidas(current_user.uid)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌ Error al marcar todas las notificaciones como leídas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@blueprint.route("/forms/<form_id>/privacidad", methods=['PUT'])
@login_required
@solo_permitido_a(docente=True)
@handle_errors
def actualizar_privacidad_form(form_id):
    """{{ _('Actualizar la privacidad de un formulario') }}"""
    try:
        data = request.get_json()
        es_publico = data.get('es_publico')
        
        if es_publico is None:
            return jsonify({
                'success': False,
                'message': gettext('Privacidad no especificada')
            }), 400
        
        from apps.lib.services.tests.apps_script_service import actualizar_permisos_form
        if actualizar_permisos_form(form_id, es_publico):
            return jsonify({
                'success': True,
                'message': gettext('Privacidad actualizada exitosamente')
            })
        else:
            return jsonify({
                'success': False,
                'message': gettext('Error al actualizar privacidad')
            }), 500
    except Exception as e:
        logger.error(f"❌ Error al actualizar privacidad: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/forms/<form_id>/estudiantes", methods=['PUT'])
@login_required
@solo_permitido_a(docente=True)
@handle_errors
def actualizar_estudiantes_form(form_id):
    """{{ _('Actualizar estudiantes de un formulario') }}"""
    try:
        data = request.get_json()
        estudiantes = data.get('estudiantes', [])
        
        # Obtener correos de los estudiantes
        estudiante_dao = EstudianteDAO()
        correos = []
        for uid in estudiantes:
            estudiante = estudiante_dao.get(uid)
            if estudiante:
                correos.append(estudiante.correo)
        
        from apps.lib.services.tests.apps_script_service import compartir_formulario_varios_correo
        if compartir_formulario_varios_correo(form_id, correos):
            return jsonify({
                'success': True,
                'message': gettext('Estudiantes actualizados exitosamente')
            })
        else:
            return jsonify({
                'success': False,
                'message': gettext('Error al actualizar estudiantes')
            }), 500
    except Exception as e:
        logger.error(f"❌ Error al actualizar estudiantes: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/forms/<form_id>/estudiantes/eliminar", methods=['PUT'])
@login_required
@solo_permitido_a(docente=True)
@handle_errors
def eliminar_estudiantes_form(form_id):
    """{{ _('Eliminar estudiantes de un formulario') }}"""
    try:
        data = request.get_json()
        estudiantes = data.get('estudiantes', [])
        
        # Obtener correos de los estudiantes
        estudiante_dao = EstudianteDAO()
        correos = []
        for uid in estudiantes:
            estudiante = estudiante_dao.get(uid)
            if estudiante:
                correos.append(estudiante.correo)
        
        from apps.lib.services.tests.apps_script_service import eliminar_permisos_form
        if eliminar_permisos_form(form_id, correos):
            return jsonify({
                'success': True,
                'message': gettext('Estudiantes eliminados exitosamente')
            })
        else:
            return jsonify({
                'success': False,
                'message': gettext('Error al eliminar estudiantes')
            }), 500
    except Exception as e:
        logger.error(f"❌ Error al eliminar estudiantes: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500



@blueprint.route("/resultados")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def ver_resultados():
    """{{ _('Ver resultados de tests de estrés') }}"""
    try:
        # Obtener paralelos donde el docente es el actual
        paralelos = [paralelo.to_dict for paralelo in ParaleloDAO().get_all_documents_by_attribute("docente_uid", current_user.uid)]
        
        # Obtener todas las materias
        materias = {materia.uid: materia.to_dict for materia in MateriaDAO().get_all}
        
        logger.info(gettext("✅ Accediendo a la vista de resultados"))
        return render_template(
            "docente/resultados_test.html",
            paralelos=paralelos,
            materias=materias
        )
    except Exception as e:
        logger.error(f"❌ Error al acceder a resultados: {str(e)}")
        flash(gettext('Error al acceder a resultados: {}').format(str(e)), 'error')
        return redirect(url_for('docente.index'))

@blueprint.route("/resultados/obtener")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def obtener_resultados():
    """{{ _('Obtener resultados de tests con filtros') }}"""
    try:
        # Obtener parámetros de filtro
        paralelo_uid = request.args.get('paralelo')
        estudiante_uid = request.args.get('estudiante')
        nivel_estres = request.args.get('nivel_estres')
        fecha = request.args.get('fecha')
        
        # Obtener actividades del docente
        actividades = []
        paralelos = ParaleloDAO().get_all_documents_by_attribute("docente_uid", current_user.uid)
        for paralelo in paralelos:
            actividades.extend(ActividadDAO().get_all_documents_by_attribute("paralelo_uid", paralelo.uid))
        
        # Filtrar actividades por paralelo si se especifica
        if paralelo_uid:
            actividades = [a for a in actividades if a.paralelo_uid == paralelo_uid]
        
        # Obtener resultados de los formularios
        resultados = []
        for actividad in actividades:
            if actividad.test_estres:
                try:
                    respuestas = obtener_respuestas_formulario(actividad.test_estres)
                    if respuestas and 'responses' in respuestas:
                        for respuesta in respuestas['responses']:
                            # Filtrar por estudiante si se especifica
                            estudiante_email = respuesta.get('respondentEmail')
                            if estudiante_uid:
                                estudiante = EstudianteDAO().get(estudiante_uid)
                                if not estudiante or estudiante.correo != estudiante_email:
                                    continue
                            
                            # Calcular nivel de estrés
                            total_score = 0
                            max_score = 0
                            for answer in respuesta.get('answers', {}).values():
                                score = int(answer.get('textAnswers', {}).get('answers', [{}])[0].get('value', '0'))
                                total_score += score
                                max_score += 4
                            
                            nivel_estres = (total_score / max_score * 100) if max_score > 0 else 0
                            
                            # Filtrar por nivel de estrés si se especifica
                            if nivel_estres:
                                if nivel_estres == 'critico' and nivel_estres < 80:
                                    continue
                                elif nivel_estres == 'alto' and (nivel_estres < 60 or nivel_estres >= 80):
                                    continue
                                elif nivel_estres == 'medio' and (nivel_estres < 40 or nivel_estres >= 60):
                                    continue
                                elif nivel_estres == 'bajo' and nivel_estres >= 40:
                                    continue
                            
                            # Filtrar por fecha si se especifica
                            if fecha:
                                fecha_respuesta = datetime.strptime(respuesta.get('createTime', ''), '%Y-%m-%dT%H:%M:%S.%fZ').date()
                                if fecha_respuesta != datetime.strptime(fecha, '%Y-%m-%d').date():
                                    continue
                            
                            resultados.append({
                                'estudiante_email': estudiante_email,
                                'fecha': respuesta.get('createTime', ''),
                                'test_nombre': actividad.nombre,
                                'nivel_estres': nivel_estres,
                                'es_critico': nivel_estres >= 80,
                                'respuestas': respuesta.get('answers', {})
                            })
                except Exception as e:
                    logger.error(f"Error al obtener respuestas del formulario {actividad.test_estres}: {str(e)}")
        
        # Calcular estadísticas
        estadisticas = {
            'distribucion': {
                'critico': len([r for r in resultados if r['nivel_estres'] >= 80]),
                'alto': len([r for r in resultados if 60 <= r['nivel_estres'] < 80]),
                'medio': len([r for r in resultados if 40 <= r['nivel_estres'] < 60]),
                'bajo': len([r for r in resultados if r['nivel_estres'] < 40])
            },
            'evolucion': {}
        }
        
        # Calcular evolución temporal
        resultados_ordenados = sorted(resultados, key=lambda x: x['fecha'])
        for resultado in resultados_ordenados:
            mes = datetime.strptime(resultado['fecha'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m')
            if mes not in estadisticas['evolucion']:
                estadisticas['evolucion'][mes] = []
            estadisticas['evolucion'][mes].append(resultado['nivel_estres'])
        
        # Calcular promedios mensuales
        for mes in estadisticas['evolucion']:
            estadisticas['evolucion'][mes] = sum(estadisticas['evolucion'][mes]) / len(estadisticas['evolucion'][mes])
        
        return jsonify({
            'resultados': resultados,
            'estadisticas': estadisticas
        })
        
        # Obtener todos los resultados
        resultados_dao = ResultadoTestDAO()
        resultados = []
        
        # Aplicar filtros
        if paralelo_uid:
            # Obtener estudiantes del paralelo
            paralelo = ParaleloDAO().get(paralelo_uid)
            if paralelo and paralelo.docente_uid == current_user.uid:
                estudiantes_uids = paralelo.estudiantes
                for estudiante_uid in estudiantes_uids:
                    resultados.extend(resultados_dao.get_by_estudiante(estudiante_uid))
        elif estudiante_uid:
            # Verificar que el estudiante pertenezca a un paralelo del docente
            paralelos = ParaleloDAO().get_all_documents_by_attribute("docente_uid", current_user.uid)
            for paralelo in paralelos:
                if estudiante_uid in paralelo.estudiantes:
                    resultados.extend(resultados_dao.get_by_estudiante(estudiante_uid))
                    break
        else:
            # Obtener resultados de todos los estudiantes en paralelos del docente
            paralelos = ParaleloDAO().get_all_documents_by_attribute("docente_uid", current_user.uid)
            for paralelo in paralelos:
                for estudiante_uid in paralelo.estudiantes:
                    resultados.extend(resultados_dao.get_by_estudiante(estudiante_uid))
        
        # Filtrar por nivel de estrés
        if nivel_estres:
            if nivel_estres == 'critico':
                resultados = [r for r in resultados if r.nivel_estres >= 80]
            elif nivel_estres == 'alto':
                resultados = [r for r in resultados if 60 <= r.nivel_estres < 80]
            elif nivel_estres == 'medio':
                resultados = [r for r in resultados if 40 <= r.nivel_estres < 60]
            elif nivel_estres == 'bajo':
                resultados = [r for r in resultados if r.nivel_estres < 40]
        
        # Filtrar por fecha
        if fecha:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            resultados = [r for r in resultados if r.fecha.date() == fecha_obj.date()]
        
        # Obtener información adicional para cada resultado
        resultados_formateados = []
        estudiante_dao = EstudianteDAO()
        test_dao = TestEstresDAO()
        
        for resultado in resultados:
            estudiante = estudiante_dao.get(resultado.estudiante_uid)
            test = test_dao.get(resultado.test_uid)
            if estudiante and test:
                resultados_formateados.append({
                    'uid': resultado.uid,
                    'estudiante_nombre': f"{estudiante.primer_nombre} {estudiante.primer_apellido}",
                    'test_nombre': test.nombre,
                    'fecha': resultado.fecha.isoformat(),
                    'nivel_estres': resultado.nivel_estres,
                    'es_critico': resultado.es_critico,
                    'respuestas': resultado.respuestas
                })
        
        # Calcular estadísticas
        estadisticas = {
            'distribucion': {
                'critico': len([r for r in resultados if r.nivel_estres >= 80]),
                'alto': len([r for r in resultados if 60 <= r.nivel_estres < 80]),
                'medio': len([r for r in resultados if 40 <= r.nivel_estres < 60]),
                'bajo': len([r for r in resultados if r.nivel_estres < 40])
            },
            'evolucion': {}
        }
        
        # Calcular evolución temporal
        resultados_ordenados = sorted(resultados, key=lambda x: x.fecha)
        for resultado in resultados_ordenados:
            mes = resultado.fecha.strftime('%Y-%m')
            if mes not in estadisticas['evolucion']:
                estadisticas['evolucion'][mes] = []
            estadisticas['evolucion'][mes].append(resultado.nivel_estres)
        
        # Calcular promedios mensuales
        for mes in estadisticas['evolucion']:
            estadisticas['evolucion'][mes] = sum(estadisticas['evolucion'][mes]) / len(estadisticas['evolucion'][mes])
        
        # Verificar niveles críticos y crear notificaciones
        for resultado in resultados:
            if resultado.nivel_estres >= 80 and not resultado.notificado:
                # Obtener el docente del estudiante
                estudiante = estudiante_dao.get(resultado.estudiante_uid)
                if estudiante:
                    for paralelo in paralelos:
                        if estudiante.uid in paralelo.estudiantes:
                            # Crear notificación
                            NotificacionDAO().crear_notificacion_nivel_critico(
                                paralelo.docente_uid,
                                estudiante.uid,
                                resultado.uid,
                                resultado.nivel_estres
                            )
                            # Marcar resultado como notificado
                            resultado_dao = ResultadoTestDAO()
                            resultado_dao._resultado_test = resultado
                            resultado_dao._resultado_test.notificado = True
                            resultado_dao.update
                            break
        
        return jsonify({
            'resultados': resultados_formateados,
            'estadisticas': estadisticas
        })
    except Exception as e:
        logger.error(f"❌ Error al obtener resultados: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blueprint.route("/resultados/enviar-reporte", methods=['POST'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def enviar_reporte():
    """{{ _('Enviar reporte de resultados por correo') }}"""
    try:
        data = request.get_json()
        email = data.get('email')
        formato = data.get('formato', 'pdf')
        
        # Obtener resultados con los filtros aplicados
        resultados_response = obtener_resultados()
        if isinstance(resultados_response, tuple):
            return resultados_response
        
        resultados_data = json.loads(resultados_response.get_data(as_text=True))
        
        # Crear mensaje de correo
        msg = Message(
            subject=gettext('Reporte de Resultados de Tests de Estrés'),
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email]
        )
        
        # Generar contenido del correo
        msg.body = f"""
        {gettext('Reporte de Resultados de Tests de Estrés')}
        
        {gettext('Resumen de Estadísticas')}:
        - {gettext('Nivel Crítico')}: {resultados_data['estadisticas']['distribucion']['critico']}
        - {gettext('Nivel Alto')}: {resultados_data['estadisticas']['distribucion']['alto']}
        - {gettext('Nivel Medio')}: {resultados_data['estadisticas']['distribucion']['medio']}
        - {gettext('Nivel Bajo')}: {resultados_data['estadisticas']['distribucion']['bajo']}
        """
        
        # TODO: Generar archivo adjunto según formato seleccionado
        
        # Enviar correo
        mail.send(msg)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌ Error al enviar reporte: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@blueprint.route("/ver-paralelos")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def ver_paralelos():
    """{{ _('Ver paralelos asignados al docente') }}"""
    try:
        # Obtener paralelos donde el docente es el actual
        paralelos = [paralelo.to_dict for paralelo in ParaleloDAO().get_all_documents_by_attribute("docente_uid", current_user.uid)]
        
        # Obtener todas las materias y convertirlas en un diccionario para fácil acceso
        materias = {materia.uid: materia.to_dict for materia in MateriaDAO().get_all}
        
        logger.info(gettext("✅ Accediendo a la lista de paralelos del docente"))
        return render_template(
            "docente/ver_paralelos.html",
            paralelos=paralelos,
            materias=materias
        )
    except Exception as e:
        logger.error(f"❌ Error al obtener paralelos: {str(e)}")
        flash(gettext('Error al obtener paralelos: {}').format(str(e)), 'error')
        return redirect(url_for('docente.index'))


@blueprint.route("/paralelos/<paralelo_uid>/actividades")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def ver_actividades(paralelo_uid):
    """{{ _('Ver actividades de un paralelo') }}"""
    try:
        # Obtener el paralelo
        paralelo = ParaleloDAO().get(paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            flash(gettext('Paralelo no encontrado'), 'error')
            return redirect(url_for('docente.ver_paralelos'))
        
        # Obtener la materia
        materia = MateriaDAO().get(paralelo.materia_uid)
        if not materia:
            flash(gettext('Materia no encontrada'), 'error')
            return redirect(url_for('docente.ver_paralelos'))
        
        # Obtener las actividades del paralelo
        actividades = [actividad.to_dict for actividad in ActividadDAO().get_all_documents_by_attribute("paralelo_uid", paralelo_uid)]
        
        logger.info(gettext("✅ Accediendo a la lista de actividades del paralelo"))
        return render_template(
            "docente/ver_actividades.html",
            paralelo=paralelo.to_dict,
            materia=materia.to_dict,
            actividades=actividades
        )
    except Exception as e:
        logger.error(f"❌ Error al obtener actividades: {str(e)}")
        flash(gettext('Error al obtener actividades: {}').format(str(e)), 'error')
        return redirect(url_for('docente.ver_paralelos'))


@blueprint.route("/paralelos/<paralelo_uid>/actividades/crear", methods=['GET', 'POST'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def crear_actividad(paralelo_uid):
    """{{ _('Crear una nueva actividad') }}"""
    try:
        # Obtener el paralelo
        paralelo = ParaleloDAO().get(paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            flash(gettext('Paralelo no encontrado'), 'error')
            return redirect(url_for('docente.ver_paralelos'))
        
        # Obtener la materia
        materia = MateriaDAO().get(paralelo.materia_uid)
        if not materia:
            flash(gettext('Materia no encontrada'), 'error')
            return redirect(url_for('docente.ver_paralelos'))

        if request.method == 'POST':
            nombre = request.form['nombre']
            form_id = request.form['test_estres']
            
            # Duplicar el formulario con el nombre de la actividad
            nuevo_form_id = duplicar_formulario(
                form_id, 
                nombre,
                es_publico='es_publico' in request.form,
                es_obligatorio='es_obligatorio' in request.form
            )
            if not nuevo_form_id:
                flash(gettext('Error al duplicar el formulario'), 'error')
                return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
            
            # Obtener el link de respuesta
            link_test = obtener_link_respuesta(nuevo_form_id)
            if not link_test:
                flash(gettext('Error al obtener el link del formulario'), 'error')
                return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
            
            # Obtener los correos de los estudiantes
            estudiantes_correos = []
            if 'es_grupal' in request.form:
                # Si es grupal, solo compartir con los estudiantes seleccionados
                estudiantes_seleccionados = request.form.getlist('estudiantes')
                estudiante_dao = EstudianteDAO()
                for uid in estudiantes_seleccionados:
                    estudiante = estudiante_dao.get(uid)
                    if estudiante:
                        estudiantes_correos.append(estudiante.correo)
            else:
                # Si no es grupal, compartir con todos los estudiantes del paralelo
                for uid in paralelo.estudiantes:
                    estudiante = EstudianteDAO().get(uid)
                    if estudiante:
                        estudiantes_correos.append(estudiante.correo)
            
            # Compartir el formulario con los estudiantes
            if not compartir_formulario_varios_correo(nuevo_form_id, estudiantes_correos, 'reader'):
                flash(gettext('Error al compartir el formulario'), 'error')
                return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
            
            # Crear la actividad
            actividad_dao = ActividadDAO()
            actividad_dao._actividad.nombre = nombre
            actividad_dao._actividad.descripcion = request.form['descripcion']
            actividad_dao._actividad.fecha_entrega = request.form['fecha_entrega']
            actividad_dao._actividad.esta_activa = 'esta_activa' in request.form
            actividad_dao._actividad.paralelo_uid = paralelo_uid
            actividad_dao._actividad.test_estres = nuevo_form_id
            actividad_dao._actividad.link_test = link_test
            actividad_dao._actividad.es_grupal = 'es_grupal' in request.form
            actividad_dao._actividad.es_obligatoria = 'es_obligatoria' in request.form
            actividad_dao._actividad.es_publico = 'es_publico' in request.form
            
            # Si es grupal, guardar los estudiantes seleccionados
            if 'es_grupal' in request.form:
                estudiantes_seleccionados = request.form.getlist('estudiantes')
                actividad_dao._actividad.estudiantes = estudiantes_seleccionados if estudiantes_seleccionados else []
            else:
                # Si no es grupal, asignar todos los estudiantes del paralelo
                actividad_dao._actividad.estudiantes = list(paralelo.estudiantes) if paralelo.estudiantes else []
            
            # Guardar la actividad
            actividad_dao.save
            
            # Configurar permisos del formulario según la privacidad
            from apps.lib.services.tests.apps_script_service import actualizar_permisos_form
            actualizar_permisos_form(nuevo_form_id, 'es_publico' in request.form)
            
            flash(gettext('Actividad creada exitosamente'), 'success')
            return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
        
        # Obtener la lista de formularios de Google
        google_forms = list_google_forms()
        if google_forms is None:
            flash(gettext('Error al obtener los formularios de Google'), 'error')
            return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
        
        # Obtener los estudiantes del paralelo
        estudiantes = []
        estudiante_dao = EstudianteDAO()
        for uid in paralelo.estudiantes:
            estudiante = estudiante_dao.get(uid)
            if estudiante:
                estudiantes.append(estudiante.to_dict)

        return render_template(
            "docente/form_actividad.html",
            paralelo=paralelo.to_dict,
            materia=materia.to_dict,
            google_forms=google_forms,
            estudiantes=estudiantes
        )
    except Exception as e:
        logger.error(f"❌ Error al crear actividad: {str(e)}")
        flash(gettext('Error al crear actividad: {}').format(str(e)), 'error')
        return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))


@blueprint.route("/paralelos/<paralelo_uid>/actividades/<actividad_uid>/editar", methods=['GET', 'POST'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def editar_actividad(paralelo_uid, actividad_uid):
    """{{ _('Editar una actividad existente') }}"""
    try:
        # Obtener el paralelo
        paralelo = ParaleloDAO().get(paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            flash(gettext('Paralelo no encontrado'), 'error')
            return redirect(url_for('docente.ver_paralelos'))
        
        # Obtener la materia
        materia = MateriaDAO().get(paralelo.materia_uid)
        if not materia:
            flash(gettext('Materia no encontrada'), 'error')
            return redirect(url_for('docente.ver_paralelos'))
        
        # Obtener la actividad
        actividad = ActividadDAO().get(actividad_uid)
        if not actividad or actividad.paralelo_uid != paralelo_uid:
            flash(gettext('Actividad no encontrada'), 'error')
            return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))

        if request.method == 'POST':
            nombre = request.form['nombre']
            form_id = request.form['test_estres']
            
            # Solo duplicar y compartir si el formulario cambió
            if form_id != actividad.test_estres:
                # Duplicar el formulario con el nombre de la actividad
                nuevo_form_id = duplicar_formulario(form_id, nombre)
                if not nuevo_form_id:
                    flash(gettext('Error al duplicar el formulario'), 'error')
                    return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
                
                # Obtener el link de respuesta
                link_test = obtener_link_respuesta(nuevo_form_id)
                if not link_test:
                    flash(gettext('Error al obtener el link del formulario'), 'error')
                    return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
                
                # Obtener los correos de los estudiantes
                estudiantes_correos = []
                if 'es_grupal' in request.form:
                    # Si es grupal, solo compartir con los estudiantes seleccionados
                    estudiantes_seleccionados = request.form.getlist('estudiantes')
                    estudiante_dao = EstudianteDAO()
                    for uid in estudiantes_seleccionados:
                        estudiante = estudiante_dao.get(uid)
                        if estudiante:
                            estudiantes_correos.append(estudiante.correo)
                else:
                    # Si no es grupal, compartir con todos los estudiantes del paralelo
                    for uid in paralelo.estudiantes:
                        estudiante = EstudianteDAO().get(uid)
                        if estudiante:
                            estudiantes_correos.append(estudiante.correo)
                
                # Compartir el formulario con los estudiantes
                if not compartir_formulario_varios_correo(nuevo_form_id, estudiantes_correos, 'reader'):
                    flash(gettext('Error al compartir el formulario'), 'error')
                    return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
            
            # Actualizar la actividad
            actividad_dao = ActividadDAO()
            actividad_dao._actividad = actividad
            actividad_dao._actividad.nombre = nombre
            actividad_dao._actividad.descripcion = request.form['descripcion']
            actividad_dao._actividad.fecha_entrega = request.form['fecha_entrega']
            actividad_dao._actividad.esta_activa = 'esta_activa' in request.form
            actividad_dao._actividad.es_grupal = 'es_grupal' in request.form
            actividad_dao._actividad.es_obligatoria = 'es_obligatoria' in request.form
            
            # Si es grupal, actualizar los estudiantes seleccionados
            if 'es_grupal' in request.form:
                estudiantes_seleccionados = request.form.getlist('estudiantes')
                actividad_dao._actividad.estudiantes = estudiantes_seleccionados if estudiantes_seleccionados else []
            else:
                # Si no es grupal, asignar todos los estudiantes del paralelo
                actividad_dao._actividad.estudiantes = list(paralelo.estudiantes) if paralelo.estudiantes else []
            
            if form_id != actividad.test_estres:
                actividad_dao._actividad.test_estres = nuevo_form_id
                actividad_dao._actividad.link_test = link_test
                
                # Configurar permisos del nuevo formulario según la privacidad
                from apps.lib.services.tests.apps_script_service import actualizar_permisos_form
                actualizar_permisos_form(nuevo_form_id, 'es_publico' in request.form)
            elif actividad.es_publico != ('es_publico' in request.form):
                # Si cambió la privacidad pero no el formulario, actualizar permisos
                from apps.lib.services.tests.apps_script_service import actualizar_permisos_form
                actualizar_permisos_form(actividad.test_estres, 'es_publico' in request.form)
            
            actividad_dao.update
            
            flash(gettext('Actividad actualizada exitosamente'), 'success')
            return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
        
        # Obtener la lista de formularios de Google
        google_forms = list_google_forms()
        if google_forms is None:
            flash(gettext('Error al obtener los formularios de Google'), 'error')
            return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))
        
        # Obtener los estudiantes del paralelo
        estudiantes = []
        estudiante_dao = EstudianteDAO()
        for uid in paralelo.estudiantes:
            estudiante = estudiante_dao.get(uid)
            if estudiante:
                estudiantes.append(estudiante.to_dict)

        return render_template(
            "docente/form_actividad.html",
            paralelo=paralelo.to_dict,
            materia=materia.to_dict,
            actividad=actividad.to_dict,
            google_forms=google_forms,
            estudiantes=estudiantes
        )
    except Exception as e:
        logger.error(f"❌ Error al editar actividad: {str(e)}")
        flash(gettext('Error al editar actividad: {}').format(str(e)), 'error')
        return redirect(url_for('docente.ver_actividades', paralelo_uid=paralelo_uid))


@blueprint.route("/actividades/<uid>/eliminar", methods=['DELETE'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def eliminar_actividad(uid):
    """{{ _('Eliminar una actividad') }}"""
    try:
        actividad = ActividadDAO().get(uid)
        if not actividad:
            return jsonify({'success': False, 'error': gettext('Actividad no encontrada')}), 404
        
        # Verificar que el paralelo pertenezca al docente
        paralelo = ParaleloDAO().get(actividad.paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            return jsonify({'success': False, 'error': gettext('No tiene permiso para eliminar esta actividad')}), 403
        
        ActividadDAO().delete(uid)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌ Error al eliminar actividad: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@blueprint.route("/paralelos/<paralelo_uid>/estudiantes")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def ver_estudiantes(paralelo_uid):
    """{{ _('Ver estudiantes de un paralelo') }}"""
    try:
        # Obtener el paralelo
        paralelo = ParaleloDAO().get(paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            return jsonify({'error': gettext('Paralelo no encontrado')}), 404
        
        # Obtener los estudiantes del paralelo
        estudiantes = []
        estudiante_dao = EstudianteDAO()
        
        # Verificar que paralelo.estudiantes no sea None
        if paralelo.estudiantes:
            for uid in paralelo.estudiantes:
                estudiante = estudiante_dao.get(uid)
                if estudiante:
                    estudiantes.append({
                        'uid': estudiante.uid,
                        'primer_nombre': estudiante.primer_nombre,
                        'primer_apellido': estudiante.primer_apellido
                    })
        
        return jsonify(estudiantes)
    except Exception as e:
        logger.error(f"❌ Error al obtener estudiantes: {str(e)}")
        flash(gettext('Error al obtener estudiantes: {}').format(str(e)), 'error')
        return redirect(url_for('docente.ver_paralelos'))


@blueprint.route("/buscar-estudiantes")
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def buscar_estudiantes():
        """{{ _('Buscar estudiantes para agregar al paralelo') }}"""
        try:
            search = request.args.get('term', '').lower()
            print("Iniciando búsqueda:", search)
            
            estudiantes = EstudianteDAO().obtener_usuarios_con_rol('estudiante')
            print("Total de estudiantes encontrados:", len(estudiantes))
            
            estudiantes_filtrados = []
            for estudiante in estudiantes:
                if (search in estudiante.primer_nombre.lower() or 
                    search in estudiante.primer_apellido.lower() or 
                    search in estudiante.correo.lower()):
                    estudiantes_filtrados.append({
                        'email': estudiante.correo,
                        'nombre': f"{estudiante.primer_nombre} {estudiante.segundo_nombre if estudiante.segundo_nombre else ''} {estudiante.primer_apellido} {estudiante.segundo_apellido if estudiante.segundo_apellido else ''}".strip()
                    })
            
            print("Estudiantes filtrados:", estudiantes_filtrados)
            return jsonify(estudiantes_filtrados)
        except Exception as e:
            logger.error(f"❌ Error al buscar estudiantes: {str(e)}")
            return jsonify({'error': str(e)}), 500


@blueprint.route("/paralelos/<paralelo_uid>/estudiantes/agregar", methods=['POST'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def agregar_estudiantes(paralelo_uid):
    """{{ _('Agregar estudiantes al paralelo') }}"""
    try:
        print(request.get_json())
        # Verificar que el paralelo pertenezca al docente
        paralelo = ParaleloDAO().get(paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            return jsonify({'success': False, 'error': gettext('No tiene permiso para modificar este paralelo')}), 403
        
        data = request.get_json()
        estudiantes_emails = data.get('estudiantes', [])
        
        if not estudiantes_emails:
            return jsonify({
                'success': False,
                'message': gettext('No se proporcionaron estudiantes')
            }), 400

        # Obtener los estudiantes por correo
        estudiantes = []
        for email in estudiantes_emails:
            estudiante_list = EstudianteDAO().get_all_documents_by_attribute("correo", email)
            if estudiante_list:
                estudiantes.append(estudiante_list[0])

            print("Estudiantes encontrados:", estudiantes)

        if not estudiantes:
            return jsonify({
                'success': False,
                'message': gettext('No se encontraron estudiantes')
            }), 404

        # Actualizar la lista de estudiantes del paralelo
        paralelo_dao = ParaleloDAO()
        paralelo_dao._paralelo = paralelo
        
        # Inicializar la lista de estudiantes si es necesario
        if not paralelo.estudiantes:
            paralelo.estudiantes = []
        
        # Agregar los estudiantes que no estén ya en el paralelo
        estudiantes_agregados = 0
        for estudiante in estudiantes:
            if estudiante.uid not in paralelo.estudiantes:
                paralelo.estudiantes.append(estudiante.uid)
                # Actualizar el estudiante
                estudiante_dao = EstudianteDAO()
                if not estudiante.paralelos:
                    estudiante.paralelos = []
                estudiante.paralelos.append(paralelo_uid)

                estudiante_dao._estudiante = estudiante
                estudiante_dao.update
                estudiantes_agregados += 1
        
        if estudiantes_agregados > 0:
            paralelo_dao.update
        
        return jsonify({
            'success': True,
            'message': gettext('Estudiantes agregados exitosamente')
        })
    except Exception as e:
        logger.error(f"❌ Error al agregar estudiantes: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@blueprint.route("/paralelos/<paralelo_uid>/estudiantes/<estudiante_uid>/eliminar", methods=['DELETE'])
@login_required
@handle_errors
@solo_permitido_a(docente=True)
def eliminar_estudiante(paralelo_uid, estudiante_uid):
    """{{ _('Eliminar un estudiante del paralelo') }}"""
    try:
        # Verificar que el paralelo pertenezca al docente
        paralelo = ParaleloDAO().get(paralelo_uid)
        if not paralelo or paralelo.docente_uid != current_user.uid:
            return jsonify({'success': False, 'error': gettext('No tiene permiso para modificar este paralelo')}), 403
        
        # Eliminar el estudiante de la lista
        if estudiante_uid in paralelo.estudiantes:
            paralelo_dao = ParaleloDAO()
            paralelo_dao._paralelo = paralelo
            paralelo.estudiantes.remove(estudiante_uid)
            paralelo_dao.update
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌ Error al eliminar estudiante: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
