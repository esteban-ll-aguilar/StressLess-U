# -*- encoding: utf-8 -*-
"""
Authentication Services
"""

from flask_login import login_user
from flask_babel import gettext
from apps import firebase, db
from apps.controls.models.usuarios import Usuario
from typing import Dict, Any, Tuple, Optional

class AuthService:
    def __init__(self):
        self.auth = firebase.auth()

    def process_firebase_token(self, id_token: str) -> Tuple[bool, Optional[str]]:
        """{{ _('Procesar el token de Firebase y obtener usuario') }}"""
        try:
            user_info = self.auth.get_account_info(id_token)
            if not user_info or 'users' not in user_info or not user_info['users']:
                return False, gettext('Invalid user information')

            print("Info original:", user_info)
            user_id = user_info['users'][0]['localId']

            if user_info['users'][0].get('providerUserInfo'):
                # encontrar si existe el provider de google.com y obtener el id la foto url
                for provider in user_info['users'][0]['providerUserInfo']:
                    if provider['providerId'] == 'google.com':
                        photo_url = provider.get('photoUrl')
                        break
                else:
                    photo_url = user_info['users'][0].get('photoUrl')
            else:
                photo_url = user_info['users'][0].get('photoUrl')

            user_doc = db.collection('usuarios').document(user_id).get()
            if not user_doc or not user_doc.exists:
                return False, gettext('User not found in database')
            
            user_data = user_doc.to_dict()
            if not user_data:
                return False, gettext('Invalid user data')

            # Actualizar la foto de perfil si el usuario inició sesión con Google
            db.collection('usuarios').document(user_id).update({
                'foto_url': photo_url
            })
            user_data['foto_url'] = photo_url
            
            print("User data:", user_data)
            flask_user = Usuario.from_dict(user_data)
            login_user(flask_user)
            return True, None

        except Exception as e:
            print("Error:", str(e))
            return False, str(e)

    def login_with_email(self, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """{{ _('Iniciar sesión con email y contraseña') }}"""
        try:
            # Intentar iniciar sesión con correo/contraseña
            user = self.auth.sign_in_with_email_and_password(email, password)
            success, error = self.process_firebase_token(user['idToken'])
            return success, error
        except Exception as e:
            error_message = str(e)
            if 'INVALID_LOGIN_CREDENTIALS' in error_message:
                try:
                    # Si falla, intentar crear una nueva cuenta con el mismo correo
                    user = self.auth.create_user_with_email_and_password(email, password)
                    success, error = self.process_firebase_token(user['idToken'])
                    return success, error
                except Exception as create_error:
                    return False, str(create_error)
            elif 'EMAIL_NOT_FOUND' in error_message:
                return False, gettext('Email is not registered.')
            elif 'INVALID_PASSWORD' in error_message:
                return False, gettext('Incorrect password. Please try again.')
            else:
                return False, str(e)

    def update_user_layout(self, user_id: str, layout: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """{{ _('Actualizar la configuración del usuario') }}"""
        try:
            db.collection('usuarios').document(user_id).update(
                {'settings.layout': layout}
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def update_user(self, user_id: str, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """{{ _('Actualizar los datos del usuario') }}"""
        try:
            # Actualizar solo los campos permitidos
            update_data = {
                'primer_nombre': data.get('primer_nombre', ''),
                'segundo_nombre': data.get('segundo_nombre', ''),
                'primer_apellido': data.get('primer_apellido', ''),
                'segundo_apellido': data.get('segundo_apellido', ''),
                'telefono': data.get('phone', ''),
                'settings': {
                    'timeZone': data.get('timeZone', 'UTC'),
                    'languagePreference': data.get('languagePreference', 'es')
                }
            }
            
            db.collection('usuarios').document(user_id).update(update_data)
            return True, None
        except Exception as e:
            return False, str(e)
        
    def send_password_reset_email(self, email: str) -> bool:
        """{{ _('Enviar correo para restablecer contraseña') }}"""
        firebase.auth().send_password_reset_email(email)
        return True
