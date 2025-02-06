from apps.routes.rutas_comunes import blueprint
from flask import jsonify, render_template, redirect, url_for
from flask_login import login_required
from apps.lib.utils.errors import handle_errors
from apps.lib.decoradors.decoradors import solo_permitido_a
import json

from apps.lib.services.tests.test  import (
    list_google_forms,
    get_form_details,
    lista_de_formularios_de_varios_propietarios,
    obtener_respuestas_formulario
)
from apps.controls.dao_controls.usuario_dao import UsuarioDAO

@blueprint.route("/ver-tests", methods=["GET"])
@login_required
@solo_permitido_a(administrador=True, docente=True)
@handle_errors
def ver_tests():
    """
    Permite ver los test que tiene el usuario esto solo estara disponible para el administrador y docente
    """
    try:
        lista = list_google_forms()
        if lista is None:  # Credenciales inválidas
            return redirect(url_for('autenticacion.authenticacion_google_forms'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return render_template("test/ver_tests.html", lista=lista)


@blueprint.route("/test-detalle/<string:id>", methods=["GET"])
@login_required
@solo_permitido_a(administrador=True, docente=True)
@handle_errors
def detalle_test(id):
    """
    Permite ver los test que tiene el usuario esto solo estara disponible para el administrador y docente
    
    """
    try:
        form = get_form_details(id)
        if form is None:  # Credenciales inválidas
            return redirect(url_for('autenticacion.authenticacion_google_forms'))
            
        respuestas = obtener_respuestas_formulario(id)
        if respuestas is None:  # Credenciales inválidas
            return redirect(url_for('autenticacion.authenticacion_google_forms'))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return render_template("components/tests/detalle_test.html", form=form, respuestas=respuestas.get('responses', []))


@blueprint.route("/tests-compatidos-conmigo", methods=["GET"])
@login_required
@solo_permitido_a(administrador=True, docente=True)
@handle_errors
def tests_compatidos_conmigo():
    """
    Permite ver los test que tiene el usuario esto solo estara disponible para el administrador y docente
    """
    admins = UsuarioDAO().obtener_usuarios_con_rol('administrador')
    correos = []
    for usuario in admins:
        correos.append(usuario.correo)

    print(correos)
    lista = lista_de_formularios_de_varios_propietarios(correos=correos)
    if lista is None:  # Credenciales inválidas
        return redirect(url_for('autenticacion.authenticacion_google_forms'))
    return render_template("test/tests_compatidos_conmigo.html", lista=lista)
