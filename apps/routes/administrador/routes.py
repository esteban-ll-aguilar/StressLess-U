from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_babel import gettext
from apps import logger, firebase, db

from firebase_admin import auth
from apps.routes.administrador import blueprint
from flask_login import login_required
from apps.lib.utils.errors import handle_errors
from apps.lib.decoradors.decoradors import solo_permitido_a
import pandas as pd
from apps.controls.dao_controls.usuario_dao import UsuarioDAO
from apps.controls.dao_controls.materia_dao import MateriaDAO
from apps.controls.dao_controls.paralelo_dao import ParaleloDAO
from apps.lib.services.excel.excel import procesar_excel
from apps.lib.services.usuarios.usuarios import obtener_correo_usuarios, validar_correo
from io import BytesIO

@blueprint.route("/")
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def index():
    """{{ _('Ruta principal del dashboard') }}"""
    logger.info(gettext("✅ Accediendo a la página principal del dashboard"))
    return redirect(url_for('administrador.ver_usuarios'))

@blueprint.route("/ver-usuarios")
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def ver_usuarios():
    """{{ _('Ver lista de usuarios') }}"""
    try:
        tipo = request.args.get('tipo', 'todos')
        estado = request.args.get('estado', 'todos')
        busqueda = request.args.get('busqueda', '').lower()
        
        usuarios = []
        usuario_dao = UsuarioDAO()
        
        # Obtener usuarios según el tipo seleccionado
        if tipo == 'estudiante':
            usuarios.extend(usuario_dao.obtener_usuarios_con_rol('estudiante'))
        elif tipo == 'docente':
            usuarios.extend(usuario_dao.obtener_usuarios_con_rol('docente'))
        elif tipo == 'administrador':
            usuarios.extend(usuario_dao.obtener_usuarios_con_rol('administrador'))
        else:
            usuarios.extend(usuario_dao.obtener_usuarios_con_rol('estudiante'))
            usuarios.extend(usuario_dao.obtener_usuarios_con_rol('docente'))
            usuarios.extend(usuario_dao.obtener_usuarios_con_rol('administrador'))
        
        # Filtrar por estado
        if estado != 'todos':
            esta_activo = estado == 'activo'
            usuarios = [u for u in usuarios if u.esta_activo == esta_activo]
        
        # Filtrar por búsqueda
        if busqueda:
            usuarios = [u for u in usuarios if 
                       busqueda in u.primer_nombre.lower() or
                       busqueda in u.primer_apellido.lower() or
                       busqueda in u.correo.lower()]
        
        return render_template(
            "administrador/ver_usuarios.html",
            usuarios=[usuario.to_dict for usuario in usuarios],
            tipo_actual=tipo,
            estado_actual=estado,
            busqueda_actual=busqueda
        )
    except Exception as e:
        logger.error(f"❌ Error al obtener usuarios: {str(e)}")
        flash(gettext('Error al obtener usuarios: {}').format(str(e)), 'error')
        return redirect(url_for('administrador.index'))

@blueprint.route("/usuarios/<uid>")
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def obtener_usuario(uid):
    """{{ _('Obtener datos de un usuario') }}"""
    try:
        usuario = UsuarioDAO().get(uid)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify(usuario.to_dict)
    except Exception as e:
        logger.error(f"❌ Error al obtener usuario: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blueprint.route("/usuarios/<uid>/rol/cambiar", methods=['PUT'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def cambiar_rol_usuario(uid):
    """{{ _('Cambiar el rol de un usuario') }}"""
    try:
        data = request.get_json()
        nuevo_rol = data.get('rol')
        if not nuevo_rol:
            return jsonify({
                'success': False,
                'message': gettext('Rol no especificado')
            }), 400
        
        usuario_dao = UsuarioDAO()
        usuario_dao.cambiar_rol(uid, nuevo_rol)
        
        return jsonify({
            'success': True,
            'message': gettext('Rol actualizado exitosamente')
        })
    except Exception as e:
        logger.error(f"❌ Error al cambiar rol: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/usuarios/<uid>/rol/eliminar", methods=['PUT'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def eliminar_rol_usuario(uid):
    """{{ _('Eliminar el rol de un usuario') }}"""
    try:
        usuario_dao = UsuarioDAO()
        usuario_dao.eliminar_rol(uid)
        
        return jsonify({
            'success': True,
            'message': gettext('Rol eliminado exitosamente')
        })
    except Exception as e:
        logger.error(f"❌ Error al eliminar rol: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/usuarios/<uid>/actualizar", methods=['PUT'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def actualizar_usuario(uid):
    """{{ _('Actualizar datos de un usuario') }}"""
    try:
        data = request.get_json()
        usuario_dao = UsuarioDAO()
        usuario = usuario_dao.get(uid)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': gettext('Usuario no encontrado')
            }), 404
        
        # Actualizar datos del usuario
        usuario_dao._usuario = usuario
        usuario_dao._usuario.primer_nombre = data['primer_nombre']
        usuario_dao._usuario.segundo_nombre = data.get('segundo_nombre', '')
        usuario_dao._usuario.primer_apellido = data['primer_apellido']
        usuario_dao._usuario.segundo_apellido = data.get('segundo_apellido', '')
        
        # Verificar si el correo cambió
        if data['correo'] != usuario.correo:
            # Verificar que el nuevo correo no exista
            if data['correo'] in obtener_correo_usuarios():
                return jsonify({
                    'success': False,
                    'message': gettext('El correo ya está en uso')
                }), 400
            usuario_dao._usuario.correo = data['correo']
        
        usuario_dao.update
        
        return jsonify({
            'success': True,
            'message': gettext('Usuario actualizado exitosamente')
        })
    except Exception as e:
        logger.error(f"❌ Error al actualizar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/usuarios/<uid>/dar-baja", methods=['PUT'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def dar_baja_usuario(uid):
    """{{ _('Dar de baja a un usuario') }}"""
    try:
        usuario_dao = UsuarioDAO()
        usuario = usuario_dao.get(uid)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': gettext('Usuario no encontrado')
            }), 404
        
        usuario_dao._usuario = usuario
        usuario_dao._usuario.esta_activo = False
        usuario_dao.update
        
        return jsonify({
            'success': True,
            'message': gettext('Usuario dado de baja exitosamente')
        })
    except Exception as e:
        logger.error(f"❌ Error al dar de baja usuario: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/usuarios/<uid>/activar", methods=['PUT'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def activar_usuario(uid):
    """{{ _('Activar a un usuario') }}"""
    try:
        usuario_dao = UsuarioDAO()
        usuario = usuario_dao.get(uid)
        
        if not usuario:
            return jsonify({
                'success': False,
                'message': gettext('Usuario no encontrado')
            }), 404
        
        usuario_dao._usuario = usuario
        usuario_dao._usuario.esta_activo = True
        usuario_dao.update
        
        return jsonify({
            'success': True,
            'message': gettext('Usuario activado exitosamente')
        })
    except Exception as e:
        logger.error(f"❌ Error al activar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/crear-usuario")
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def crear_usuario():
    """{{ _('Página de creación de usuarios') }}"""
    logger.info(gettext("✅ Accediendo a la página de creación de usuarios"))
    return render_template("administrador/crear_usuario.html")

@blueprint.route("/crear-estudiante", methods=['POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def crear_estudiante():
    """{{ _('Crear un nuevo estudiante') }}"""
    try:
        data = request.form.to_dict()
        if data['email'] in obtener_correo_usuarios():
            flash(gettext('El estudiante ya existe en el sistema'), 'info')
        else:
            UsuarioDAO().registrar_usuario(data, es_estudiante=True)
            flash(gettext('Estudiante creado exitosamente'), 'success')
    except Exception as e:
        logger.error(f"❌​ ​Error al crear estudiante: {str(e)}")
        flash(gettext('Error al crear estudiante: {}').format(str(e)), 'error')
    return redirect(url_for('administrador.crear_usuario'))

@blueprint.route("/crear-docente", methods=['POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def crear_docente():
    """{{ _('Crear un nuevo docente') }}"""
    try:
        data = request.form.to_dict()
        if data['email'] in obtener_correo_usuarios():
            flash(gettext('El docente ya existe en el sistema'), 'info')
        else:
            UsuarioDAO().registrar_usuario(data, es_docente=True)
            flash(gettext('Docente creado exitosamente'), 'success')
    except Exception as e:
        logger.error(f"❌​ ​Error al crear docente: {str(e)}")
        flash(gettext('Error al crear docente: {}').format(str(e)), 'error')
    return redirect(url_for('administrador.crear_usuario'))

@blueprint.route("/crear-administrador", methods=['POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def crear_administrador():
    """{{ _('Crear un nuevo administrador') }}"""
    try:
        data = request.form.to_dict()
        if data['email'] in obtener_correo_usuarios():
            flash(gettext('El administrador ya existe en el sistema'), 'info')
        else:
            UsuarioDAO().registrar_usuario(data, es_administrador=True)
            flash(gettext('Administrador creado exitosamente'), 'success')
    except Exception as e:
        logger.error(f"❌​ ​Error al crear administrador: {str(e)}")
        flash(gettext('Error al crear administrador: {}').format(str(e)), 'error')
    return redirect(url_for('administrador.crear_usuario'))

@blueprint.route("/cargar-usuarios-excel", methods=['POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def cargar_usuarios_excel():
    """{{ _('Cargar usuarios desde archivo Excel') }}"""
    try:
        if 'file' not in request.files:
            flash(gettext('No se seleccionó ningún archivo'), 'error')
            return redirect(url_for('administrador.crear_usuario'))
        
        file = request.files['file']
        if not file.filename:
            flash(gettext('No se seleccionó ningun archivo'), 'error')
            return redirect(url_for('administrador.crear_usuario'))
        
        tipo_usuario = request.form.get('tipo_usuario')
        if tipo_usuario not in ['estudiante', 'docente']:
            flash(gettext('Tipo de usuario no valido'), 'error')
            return redirect(url_for('administrador.crear_usuario'))
        
        resultado, creados_error = procesar_excel(file, tipo_usuario)
        if resultado:
            flash(gettext(f'{creados_error} {tipo_usuario.capitalize()} cargados exitosamente'), 'success')
        else:
            flash(gettext(f'Error al cargar los {tipo_usuario.capitalize()} desde el archivo Excel: {creados_error}'), 'error')
    except Exception as e:
        logger.error(f"❌​ ​Error al cargar archivo Excel: {str(e)}")
        flash(gettext('Error al cargar archivo Excel: {}').format(str(e)), 'error')
    return redirect(url_for('administrador.crear_usuario'))

@blueprint.route("/crear-test", methods=["GET", 'POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def crear_test():
    """{{ _('Crear un nuevo test') }}"""
    return render_template('administrador/crear_test.html')

@blueprint.route("/obtener-docentes")
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def obtener_docentes():
    """{{ _('Obtener lista de docentes') }}"""
    try:
        search = request.args.get('term', '').lower()
        docentes = UsuarioDAO().obtener_usuarios_con_rol('docente')
        docentes_filtrados = [
            docente for docente in docentes
            if search in docente.primer_nombre.lower() or 
               search in docente.primer_apellido.lower() or 
               search in docente.correo.lower()
        ]
        return jsonify([{
            'email': docente.correo,
            'nombre': f"{docente.primer_nombre} {docente.primer_apellido}"
        } for docente in docentes_filtrados])
    except Exception as e:
        logger.error(f"❌​ ​Error al obtener docentes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blueprint.route("/compartir-test", methods=['POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def compartir_test():
    """{{ _('Compartir test con docentes seleccionados') }}"""
    try:
        data = request.get_json()
        test_id = data.get('test_id')
        docentes = data.get('docentes', [])
        
        if not test_id or not docentes:
            return jsonify({
                'success': False,
                'message': gettext('Datos incompletos')
            }), 400

        from apps.lib.services.tests.test import compartir_formulario_varios_correo
        resultado = compartir_formulario_varios_correo(test_id, docentes)
        
        if resultado:
            return jsonify({
                'success': True,
                'message': gettext('Test compartido exitosamente')
            })
        else:
            return jsonify({
                'success': False,
                'message': gettext('Error al compartir el test')
            }), 500
    except Exception as e:
        logger.error(f"❌​ ​Error al compartir test: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@blueprint.route("/ver-materias")
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def ver_materias():
    """{{ _('Ver todas las materias') }}"""
    try:
        materias = MateriaDAO().get_all
        logger.info(gettext("✅ Accediendo a la lista de materias"))
        return render_template(
            "administrador/materias/ver_materias.html",
            materias=[materia.to_dict for materia in materias]
        )
    except Exception as e:
        logger.error(f"❌​ ​Error al obtener materias: {str(e)}")
        flash(gettext('Error al obtener materias: {}').format(str(e)), 'error')
        return redirect(url_for('administrador.index'))

@blueprint.route("/crear-materia", methods=['GET', 'POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def crear_materia():
    """{{ _('Página de creación de materias') }}"""
    if request.method == 'GET':
        logger.info(gettext("✅ Accediendo a la página de creación de materias"))
        return render_template("administrador/materias/crear_materias.html")
    else:  # POST
        try:
            data = request.form.to_dict()
            materia_dao = MateriaDAO()
            materia_dao._materia.nombre = data['nombre']

            materia = materia_dao.get_all_documents_by_attribute('nombre', data['nombre'])
            if len(materia) > 0:
                flash(gettext('La materia ya existe'), 'error')
                return redirect(url_for('administrador.crear_materia'))

            materia_dao._materia.descripcion = data.get('descripcion', '')
            materia_dao.save
            flash(gettext('Materia creada exitosamente'), 'success')
        except Exception as e:
            logger.error(f"❌​ ​Error al crear materia: {str(e)}")
            flash(gettext('Error al crear materia: {}').format(str(e)), 'error')
        return redirect(url_for('administrador.crear_materia'))

@blueprint.route("/ver-paralelos")
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def ver_paralelos():
    """{{ _('Ver todos los paralelos') }}"""
    try:
        paralelos = [paralelo.to_dict for paralelo in ParaleloDAO().get_all]
        materias = {materia.uid: materia.to_dict for materia in MateriaDAO().get_all}
        docentes = {docente.uid: docente.to_dict for docente in UsuarioDAO().obtener_usuarios_con_rol('docente')}

        
        logger.info(gettext("✅ Accediendo a la lista de paralelos"))
        return render_template(
            "administrador/paralelos/ver_paralelos.html",
            paralelos=paralelos,
            materias=materias,
            docentes=docentes
        )
    except Exception as e:
        logger.error(f"❌​ ​Error al obtener paralelos: {str(e)}")
        flash(gettext('Error al obtener paralelos: {}').format(str(e)), 'error')
        return redirect(url_for('administrador.index'))

@blueprint.route("/crear-paralelo", methods=['GET', 'POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def crear_paralelo():
    """{{ _('Página de creación de paralelos') }}"""
    if request.method == 'GET':
        materias = MateriaDAO().get_all
        docentes = UsuarioDAO().obtener_usuarios_con_rol('docente')
        logger.info(gettext("✅ Accediendo a la página de creación de paralelos"))
        return render_template(
            "administrador/paralelos/crear_paralelo.html",
            materias=materias,
            docentes=docentes
        )
    else:  # POST
        try:
            data = request.form.to_dict()
            paralelo_dao = ParaleloDAO()
            
            # Verificar si ya existe un paralelo con el mismo nombre
            paralelos_existentes = paralelo_dao.get_all
            if any(p.nombre == data['nombre'] for p in paralelos_existentes):
                if any(p.materia_uid == data['materia_uid'] for p in paralelos_existentes):
                    flash(gettext('Ya existe un paralelo con ese nombre y materia'), 'error')
                    return redirect(url_for('administrador.crear_paralelo'))
            
            # Crear el paralelo
            paralelo_dao._paralelo.nombre = data['nombre']
            paralelo_dao._paralelo.materia_uid = data['materia_uid']
            paralelo_dao._paralelo.docente_uid = data['docente_uid']
            paralelo_dao._paralelo.descripcion = data.get('descripcion', '')
            paralelo_dao.save
            
            flash(gettext('Paralelo creado exitosamente'), 'success')
            return redirect(url_for('administrador.ver_paralelos'))
        except Exception as e:
            logger.error(f"❌​ ​Error al crear paralelo: {str(e)}")
            flash(gettext('Error al crear paralelo: {}').format(str(e)), 'error')
            return redirect(url_for('administrador.crear_paralelo'))

@blueprint.route("/editar-paralelo/<uid>", methods=['GET', 'POST'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def editar_paralelo(uid):
    """{{ _('Página de edición de paralelos') }}"""
    paralelo_dao = ParaleloDAO()
    paralelo = paralelo_dao.get(uid)
    
    if not paralelo:
        flash(gettext('Paralelo no encontrado'), 'error')
        return redirect(url_for('administrador.ver_paralelos'))
    
    if request.method == 'GET':
        materias = MateriaDAO().get_all
        docentes = UsuarioDAO().obtener_usuarios_con_rol('docente')
        return render_template(
            "administrador/paralelos/crear_paralelo.html",
            paralelo=paralelo,
            materias=materias,
            docentes=docentes
        )
    else:  # POST
        try:
            data = request.form.to_dict()
            
            # Verificar si el nuevo nombre ya existe en otro paralelo
            paralelos_existentes = paralelo_dao.get_all()
            if any(p.nombre == data['nombre'] and p.uid != uid for p in paralelos_existentes):
                if any(p.materia_uid == data['materia_uid'] and p.uid != uid for p in paralelos_existentes):
                    flash(gettext('Ya existe otro paralelo con ese nombre y materia'), 'error')
                    return redirect(url_for('administrador.editar_paralelo', uid=uid))
            
            # Actualizar datos del paralelo
            paralelo_dao._paralelo.nombre = data['nombre']
            paralelo_dao._paralelo.materia_uid = data['materia_uid']
            paralelo_dao._paralelo.docente_uid = data['docente_uid']
            paralelo_dao._paralelo.descripcion = data.get('descripcion', '')
            
            paralelo_dao.save
            flash(gettext('Paralelo actualizado exitosamente'), 'success')
            return redirect(url_for('administrador.ver_paralelos'))
        except Exception as e:
            logger.error(f"❌​ ​Error al actualizar paralelo: {str(e)}")
            flash(gettext('Error al actualizar paralelo: {}').format(str(e)), 'error')
            return redirect(url_for('administrador.editar_paralelo', uid=uid))

@blueprint.route("/paralelos/<uid>/eliminar", methods=['DELETE'])
@login_required
@solo_permitido_a(administrador=True)
@handle_errors
def eliminar_paralelo(uid):
    """{{ _('Eliminar un paralelo') }}"""
    try:
        ParaleloDAO().delete(uid)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"❌​ ​Error al eliminar paralelo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
