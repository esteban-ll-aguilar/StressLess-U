from flask import Flask
from apps.lib.utils.errors import register_error_handlers
from apps.tests.routes import example_blueprint

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'tu-clave-secreta'
    
    # Registrar los manejadores de error
    register_error_handlers(app)
    
    # Registrar el blueprint de ejemplo
    app.register_blueprint(example_blueprint, url_prefix='/example')
    
    return app

"""
Para usar esta aplicación de ejemplo:

1. Crea un archivo run.py en la raíz del proyecto:

from apps.example.app_setup import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

2. Ejecuta la aplicación:

python run.py

3. Accede a las diferentes rutas de ejemplo para ver cómo se manejan los errores:

http://localhost:5000/example/basic-example
http://localhost:5000/example/template-error
http://localhost:5000/example/user/0
http://localhost:5000/example/business-logic
etc.

Cada error será:
- Registrado en los logs con detalles completos
- Mostrado al usuario con un mensaje amigable
- Si eres admin, verás los detalles técnicos en la página de error
"""
