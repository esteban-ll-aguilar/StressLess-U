from googleapiclient.discovery import build
from flask import redirect, Response    
from apps.lib.services.auth.auth_google_forms import verify_credentials
from apps.lib.utils.constants import SCOPES
from apps.lib.services.tests.apps_script_service import configurar_notificaciones_form
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def list_google_forms():
    """{{ _('Obtener todos los formularios del usuario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return None
            
        # Construir el servicio de Google Drive
        service = build('drive', 'v3', credentials=creds)

        # Buscar archivos con el mimeType de Google Forms
        query = "mimeType='application/vnd.google-apps.form'"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            logger.info("No se encontraron formularios.")
            return []

        logger.debug("Formularios encontrados:")
        for file in files:
            logger.debug(f"- {file['name']} (ID: {file['id']})")
        return files

    except Exception as e:
        logger.error(f"Error al obtener los formularios: {str(e)}")
        return []

def get_form_details(form_id):
    """{{ _('Obtener los detalles de un formulario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return None
            
        # Construir el servicio de Google Forms
        service = build('forms', 'v1', credentials=creds)

        # Obtener los detalles del formulario
        form = service.forms().get(formId=form_id).execute()
        return form
    except Exception as e:
        logger.error(f"Error al obtener los detalles del formulario: {str(e)}")
        return {}

def compartir_formulario_varios_correo(form_id: str, correos: list = [], role='writer'):
    """{{ _('Compartir formulario con varios correos') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return None
            
        # Construir el servicio de Google Drive
        service = build('drive', 'v3', credentials=creds)

        # Compartir el formulario con cada correo
        for correo in correos:
            service.permissions().create(
                fileId=form_id,
                body={'role': role, 'type': 'user', 'emailAddress': correo},
                fields='id'
            ).execute()

        logger.info("Formulario compartido con éxito")
        return True
    except Exception as e:
        logger.error(f"Error al compartir el formulario: {str(e)}")
        return False

def lista_de_formularios_de_varios_propietarios(correos: list):
    """{{ _('Obtener lista de formularios de varios propietarios') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return None
            
        # Construir el servicio de Google Drive
        service = build('drive', 'v3', credentials=creds)

        # Crear la consulta para buscar los formularios de varios propietarios
        query_parts = [f"'{email}' in owners" for email in correos]
        query = "mimeType='application/vnd.google-apps.form' and (" + " or ".join(query_parts) + ")"

        # Hacer la consulta a la API
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            logger.info("No se encontraron formularios de los propietarios especificados.")
            return []

        logger.debug("Formularios encontrados:")
        for file in files:
            logger.debug(f"- {file['name']} (ID: {file['id']})")
        return files

    except Exception as e:
        logger.error(f"Error al obtener los formularios: {str(e)}")
        return []

def duplicar_formulario(form_id: str, name: str="", es_publico: bool = False, es_obligatorio: bool = False):
    """{{ _('Duplicar un formulario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return None
            
        # Construir el servicio de Google Drive
        service = build('drive', 'v3', credentials=creds)

        # Duplicar el formulario
        file = service.files().get(fileId=form_id).execute()
        copied_file = service.files().copy(
            fileId=form_id,
            body={'name': f"{file['name']} - {name} - {datetime.now().strftime('%a, %d %b %Y - %H:%M')}"}
        ).execute()
        
        nuevo_form_id = copied_file.get('id')
        if nuevo_form_id:
            # Configurar notificaciones y propiedades para el nuevo formulario
            if configurar_notificaciones_form(nuevo_form_id, es_publico, es_obligatorio):
                logger.info("Formulario duplicado y configurado con éxito")
            else:
                logger.warning("Formulario duplicado pero hubo un error en la configuración")
        
        return nuevo_form_id
    except Exception as e:
        logger.error(f"Error al duplicar el formulario: {str(e)}")
        return False

def obtener_link_respuesta(form_id: str):
    """{{ _('Obtener el link para responder el formulario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return None
            
        # Construir el servicio de Google Forms
        service = build('forms', 'v1', credentials=creds)

        # Obtener los detalles del formulario
        form = service.forms().get(formId=form_id).execute()
        return f"https://docs.google.com/forms/d/{form_id}/viewform"
    except Exception as e:
        logger.error(f"Error al obtener el link del formulario: {str(e)}")
        return None

def obtener_respuestas_formulario(form_id: str):
    """{{ _('Obtener las respuestas de un formulario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return None
            
        # Construir el servicio de Google Forms
        service = build('forms', 'v1', credentials=creds)

        # Obtener las respuestas del formulario
        responses = service.forms().responses().list(formId=form_id).execute()
        return responses
    except Exception as e:
        logger.error(f"Error al obtener las respuestas del formulario: {str(e)}")
        return {}
