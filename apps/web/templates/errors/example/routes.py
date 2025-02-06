from flask import Blueprint, render_template, jsonify, abort
from apps.lib.utils.errors import handle_errors
from flask_login import login_required
import logging

logger = logging.getLogger(__name__)

example_blueprint = Blueprint('example_blueprint', __name__)

# Ejemplo 1: Uso básico del decorador handle_errors
@example_blueprint.route('/basic-example')
@handle_errors
def basic_example():
    # Simulamos un error al intentar acceder a una variable que no existe
    non_existent_variable.some_method()
    return "Esta línea nunca se ejecutará"

# Ejemplo 2: Manejo de errores con template no encontrado
@example_blueprint.route('/template-error')
@handle_errors
def template_error():
    # Intentamos renderizar una plantilla que no existe
    return render_template('non_existent_template.html')

# Ejemplo 3: Manejo de errores con validación y abort
@example_blueprint.route('/user/<int:user_id>')
@handle_errors
@login_required
def get_user(user_id):
    if user_id <= 0:
        # Lanzamos un error 400 Bad Request
        abort(400, description="El ID de usuario debe ser un número positivo")
    
    # Simulamos que no encontramos el usuario
    if user_id > 1000:
        # Lanzamos un error 404 Not Found
        abort(404, description=f"Usuario con ID {user_id} no encontrado")
    
    return jsonify({"user_id": user_id, "name": "Usuario de ejemplo"})

# Ejemplo 4: Manejo de errores con excepciones personalizadas
class CustomBusinessError(Exception):
    pass

@example_blueprint.route('/business-logic')
@handle_errors
def business_logic():
    try:
        # Simulamos alguna lógica de negocio que puede fallar
        raise CustomBusinessError("Error en la lógica de negocio")
    except CustomBusinessError as e:
        logger.error(f"❌​ ​Error de negocio: {str(e)}")
        abort(400, description=str(e))

# Ejemplo 5: Manejo de errores en operaciones de base de datos
@example_blueprint.route('/database-operation')
@handle_errors
def database_operation():
    try:
        # Simulamos un error de base de datos
        raise Exception("Error de conexión a la base de datos")
    except Exception as e:
        logger.error(f"❌​ ​Error de base de datos: {str(e)}")
        abort(500, description="Error al conectar con la base de datos")

# Ejemplo 6: Manejo de errores con permisos
@example_blueprint.route('/admin-only')
@handle_errors
@login_required
def admin_only():
    # Simulamos verificación de permisos
    user_is_admin = False
    if not user_is_admin:
        abort(403, description="Solo los administradores pueden acceder a esta página")
    
    return "Contenido solo para administradores"

# Ejemplo 7: Manejo de errores en operaciones asíncronas
@example_blueprint.route('/async-operation')
@handle_errors
def async_operation():
    try:
        # Simulamos una operación asíncrona que falla
        raise TimeoutError("La operación tardó demasiado tiempo")
    except TimeoutError as e:
        logger.error(f"❌​ ​Error de timeout: {str(e)}")
        abort(504, description="La operación tardó demasiado tiempo en completarse")

"""
Para usar estos ejemplos:

1. Registra el blueprint en tu aplicación Flask:

from apps.example.routes import example_blueprint

app.register_blueprint(example_blueprint, url_prefix='/example')

2. Accede a las rutas:

- Error básico: /example/basic-example
- Error de template: /example/template-error
- Error de usuario: /example/user/0 o /example/user/1001
- Error de negocio: /example/business-logic
- Error de base de datos: /example/database-operation
- Error de permisos: /example/admin-only
- Error de timeout: /example/async-operation

Cada ruta mostrará diferentes tipos de errores manejados por nuestro sistema.
"""
