# -*- encoding: utf-8 -*-
"""
Inicialización de la aplicación Flask
"""

from flask import Flask, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from importlib import import_module
from google.cloud import firestore
from google.oauth2 import service_account
import pyrebase
from firebase_admin import credentials as admin_credentials
import firebase_admin
from apps.config import Config, babel
from apps.lib.utils.errors import register_error_handlers
import logging
import os


# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

login_manager = LoginManager()
# csrf = CSRFProtect()
mail = Mail()
firebase = None
db = None


def init_firebase():
    """{{ _('Inicializar Firebase y Firestore') }}"""
    global firebase, db
    try:
        firebase = pyrebase.initialize_app(Config.FIREBASE_CONFIG)
        logger.info("✅ Pyrebase inicializado correctamente.")
        credentials = service_account.Credentials.from_service_account_file(Config.FIREBASE_SERVICE_ACCOUNT_PATH)
        db = firestore.Client(credentials=credentials)

        #Now init with firebase admin
        credentials_from_f_admin = admin_credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(credentials_from_f_admin)
        logger.info("✅ Cliente Firestore inicializado correctamente.")
    except Exception as e:
        logger.error(f"❌​ ​Error al inicializar Firebase y Firestore: {str(e)}")
        raise


    
def register_extensions(app):
    """{{ _('Registrar extensiones de Flask') }}"""
    # Configurar Flask-Mail
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
    )
    mail.init_app(app)
    logger.info("✅ Flask-Mail inicializado correctamente.")

    # Inicializar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'autenticacion.login'
    login_manager.login_message = '{{ _("Por favor, inicie sesión para acceder a esta página.") }}'

    # Configurar user_loader
    @login_manager.user_loader
    def load_user(user_id):
        from apps.controls.models.usuarios import Usuario
        try:
            user_doc = db.collection('usuarios').document(user_id).get()
            if user_doc.exists:
                return Usuario.from_dict(user_doc.to_dict())
        except Exception as e:
            logger.error(f"❌​ ​Error loading user: {str(e)}")
        return None
    logger.info("✅ LoginManager inicializado correctamente.")
    
    # Inicializar Babel para i18n
    babel.init_app(app, locale_selector=Config.get_locale)
    logger.info("✅ Babel inicializado correctamente.")
    
    # Inicializar Firebase
    init_firebase()

def register_blueprints(app):
    """{{ _('Registrar blueprints de la aplicación') }}"""
    for module_name in ('authentication', 'home', 'estudiante', 'docente', 'administrador', 'rutas_comunes','documentation'):
        module = import_module('apps.routes.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)
        logger.info(f"✅🔥 Blueprint registrado: {module_name}")

def register_filters(app):
    """{{ _('Registrar filtros de la aplicación') }}"""
    from apps.lib.services.apps import filters

    app.jinja_env.filters['format_date'] = filters.format_date









def create_app(config):
    """{{ _('Crear y configurar la aplicación Flask') }}"""
    app = Flask(__name__,
                template_folder='web/templates',
                static_folder='web/static')
    app.config.from_object(config)
    
    # Configurar clave secreta
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(24)
        logger.warning("No se encontró SECRET_KEY, se generó una nueva.")
    else:
        logger.info("SECRET_KEY configurada correctamente.")
    
    # Configuración de seguridad
    app.config.update(
        SESSION_COOKIE_SECURE=False,  # False para desarrollo
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=3600,  # 1 hora
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_DURATION=2592000,  # 30 dias
        CSRF_ENABLED=True,
        WTF_CSRF_ENABLED=True
    )
    logger.info("⚙️ Configuración de seguridad aplicada.")

    # Configuración de i18n
    app.config.update(
        BABEL_TRANSLATION_DIRECTORIES=os.path.join(os.getcwd(), 'translations'),
        BABEL_DEFAULT_LOCALE='en',
        BABEL_SUPPORTED_LOCALES=Config.LANGUAGES
    )
    logger.info("⚙️ Configuración de i18n aplicada.")

    try:
        # Registrar extensiones y blueprints
        register_extensions(app)
        register_blueprints(app)
        register_filters(app)
        
        # Registrar manejadores de errores
        register_error_handlers(app)
        
        logger.info("🚀 Aplicación Flask creada y configurada correctamente.")
    except Exception as e:
        logger.error(f"❌​ ​Error al crear la aplicación Flask: {str(e)}")
        raise

    return app
