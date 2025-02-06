import os
from dotenv import load_dotenv
from flask import url_for, redirect, Response
from flask_login import current_user
from apps.controls.dao_controls.usuario_dao import UsuarioDAO
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import logging

from apps.lib.utils.constants import CLIENT_SECRETS_FILE, SCOPES

# {{ _('Configurar logging') }}
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# {{ _('Cargar variables de entorno') }}
load_dotenv()

def verify_credentials():
    """{{ _('Verificar y obtener credenciales válidas') }}"""
    try:
        # Verificar si hay credenciales almacenadas
        if not (isinstance(current_user.credenciales, dict) and 'token' in current_user.credenciales):
            logger.warning("No hay credenciales almacenadas")
            return False, None
            
        # Intentar crear credenciales
        try:
            print(current_user.credenciales)
            creds = Credentials(
                token=current_user.credenciales.get('token'),
                refresh_token=current_user.credenciales.get('refresh_token'),
                scopes=SCOPES,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=current_user.credenciales.get('client_id'),
                client_secret=current_user.credenciales.get('client_secret'),
                # expiry=current_user.credenciales.get('expires')
            )
            
            # Verificar validez
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    # Si el token ha expirado, usamos el refresh token para obtener un nuevo access token
                    logger.info("Token expirado, intentando refrescar...")
                    creds.refresh(Request())  # Refresh del token

                    # Aquí puedes guardar el nuevo token y refresh token si quieres
                    current_user.credenciales['token'] = creds.token
                    current_user.credenciales['refresh_token'] = creds.refresh_token
                    current_user.credenciales['client_id'] = creds.client_id
                    current_user.credenciales['client_secret'] = creds._client_secret
                    current_user.credenciales['expires'] = creds.expiry
                else:
                    logger.warning("Credenciales inválidas o expiradas sin refresh token disponible")
                    return False, None
                
            return True, creds
            
        except Exception as token_error:
            logger.warning(f"Error al crear credenciales: {str(token_error)}")
            return False, None
            
    except Exception as e:
        logger.error(f"❌​ Error al verificar credenciales: {str(e)}")
        return False, None

# {{ _('Configurar Google OAuth') }}
def get_google_flow():
    """{{ _('Obtener flujo OAuth de Google') }}"""
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('autenticacion.oauth2callback', _external=True)
    )
    # Configurar parámetros adicionales para el flujo de autorización
    flow.authorization_url_kwargs = {
        'access_type': 'offline',  
        'include_granted_scopes': 'true',
        'prompt': 'select_account consent'
    }
    return flow

def save_credentials(credentials):
    """{{ _('Guardar el token de acceso del usuario temporalmente') }}"""
    try:
        # Solo guardamos el token y los scopes que son lo esencial
        logger.debug(f"Credenciales a guardar - token: {credentials.token[:10]}...")
        print(credentials.__dict__)
        
        current_user.credenciales = {
            'token': credentials.token,
            'scopes': SCOPES,
            'client_id': credentials.client_id,
            'refresh_token': credentials.refresh_token,
            'client_secret': credentials._client_secret,
            'expires': credentials.expiry
        }
        
        logger.debug(f"Credenciales guardadas: {current_user.credenciales}")

        usuario = UsuarioDAO()
        usuario._usuario = usuario._usuario.from_dict(current_user.to_dict)

        if not usuario._usuario:
            return
        usuario.update
    except Exception as e:
        logger.error(f"❌​ Error al guardar credenciales: {str(e)}")
        raise

def load_credentials():
    """{{ _('Cargar credenciales del usuario') }}"""
    return verify_credentials()
