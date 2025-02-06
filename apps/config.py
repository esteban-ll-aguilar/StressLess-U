# -*- encoding: utf-8 -*-
"""
Template Base Configuration
"""

import json
import logging
import os

from dotenv import load_dotenv
from flask import request
from flask_babel import Babel
from flask_login import current_user

from apps.lib.utils.firebase import get_firebase_cred_files

# Load environment variables from .env file
load_dotenv()

babel = Babel()

class Config(object):

    basedir = os.getcwd()

    # Set up the App SECRET_KEY
    SECRET_KEY = os.getenv("SECRET_KEY", "S#perS3crEt_007")

    # Firebase configuration
    FIREBASE_SERVICE_ACCOUNT_PATH, FIREBASE_CONFIG_PATH = get_firebase_cred_files()

    with open(FIREBASE_CONFIG_PATH, "r") as config_file:
        FIREBASE_CONFIG = json.load(config_file)

    # Babel configuration
    BABEL_DEFAULT_LOCALE = os.getenv('BABEL_DEFAULT_LOCALE', 'es')
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    LANGUAGES = ['en', 'es', 'nl']

    @staticmethod
    def get_locale():
        # Si el usuario está autenticado y tiene una preferencia de idioma
        if current_user and hasattr(current_user, 'settings'):
            user_lang = current_user.settings.get('languagePreference')
            if user_lang and user_lang in Config.LANGUAGES:
                return user_lang
        
        # Si no hay preferencia de usuario, usar el idioma por defecto
        return Config.BABEL_DEFAULT_LOCALE


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True

logger = logging.getLogger(__name__)

# Load all possible configurations
config_dict = {
    "Production": ProductionConfig,
    "Debug": DebugConfig
}
