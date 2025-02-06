from googleapiclient.discovery import build
from apps.lib.services.auth.auth_google_forms import verify_credentials
from apps import logging
from flask_babel import gettext

logger = logging.getLogger(__name__)

NOTIFICATION_SCRIPT = '''
// Configurar propiedades del formulario
function configurarFormulario(esPublico, esObligatorio) {
  var properties = PropertiesService.getDocumentProperties();
  properties.setProperties({
    'es_publico': esPublico.toString(),
    'es_obligatorio': esObligatorio.toString()
  });
}

function onFormSubmit(e) {
  var form = FormApp.getActiveForm();
  var formResponse = e.response;
  var formId = form.getId();
  var itemResponses = formResponse.getItemResponses();
  var totalScore = 0;
  var maxScore = 0;
  
  // Obtener el correo del estudiante
  var studentEmail = formResponse.getRespondentEmail();
  var timestamp = formResponse.getTimestamp();
  
  // Verificar si el estudiante tiene permiso
  var form = FormApp.getActiveForm();
  var viewers = form.getViewers();
  var hasAccess = viewers.some(function(user) {
    return user.getEmail() == studentEmail;
  });
  if (!hasAccess) {
    Logger.log('Estudiante no autorizado: ' + studentEmail);
    return;
  }
  
  // Verificar si el formulario es obligatorio
  var formProperties = PropertiesService.getDocumentProperties();
  var isObligatorio = formProperties.getProperty('es_obligatorio') === 'true';
  if (!isObligatorio) {
    Logger.log('Formulario opcional, no se requiere verificación');
    return;
  }
  
  // Obtener las respuestas
  var answers = [];
  for (var i = 0; i < itemResponses.length; i++) {
    var itemResponse = itemResponses[i];
    var question = itemResponse.getItem().getTitle();
    var answer = itemResponse.getResponse();
    
    // Convertir la respuesta a número si es posible
    var score = 0;
    if (typeof answer === 'string') {
      // Si es una respuesta de texto, intentar convertir a número
      score = parseInt(answer) || 0;
    } else if (Array.isArray(answer)) {
      // Si es un array (respuestas múltiples), sumar los valores
      score = answer.reduce(function(sum, val) {
        return sum + (parseInt(val) || 0);
      }, 0);
    }
    
    totalScore += score;
    maxScore += 4; // Asumiendo escala de 0-4
    
    answers.push({
      question: question,
      answer: answer,
      score: score
    });
  }
  
  // Calcular porcentaje
  var percentage = (totalScore / maxScore) * 100;
  
  // Si el porcentaje es menor al 60%, enviar correo
  if (percentage < 60) {
    // Crear contenido detallado
    var details = answers.map(function(item) {
      return '<tr>' +
             '<td>' + item.question + '</td>' +
             '<td>' + item.answer + '</td>' +
             '<td>' + item.score + '</td>' +
             '</tr>';
    }).join('');
    
  // Obtener configuración del formulario
  var formProperties = PropertiesService.getDocumentProperties();
  var isPublic = formProperties.getProperty('es_publico') === 'true';
  var isObligatorio = formProperties.getProperty('es_obligatorio') === 'true';
  
  // Enviar correo al docente
  MailApp.sendEmail({
    to: Session.getEffectiveUser().getEmail(),
    subject: "Alerta: Resultado Bajo en Test de Estrés",
    htmlBody: `
      <h3>Alerta de Resultado Bajo</h3>
      <p>Un estudiante ha obtenido una puntuación baja en el test de estrés:</p>
      <ul>
        <li><strong>Estudiante:</strong> ${studentEmail}</li>
        <li><strong>Fecha:</strong> ${timestamp.toLocaleString()}</li>
        <li><strong>Puntuación:</strong> ${percentage.toFixed(1)}%</li>
        <li><strong>Tipo:</strong> ${isObligatorio ? 'Obligatorio' : 'Opcional'}</li>
        <li><strong>Privacidad:</strong> ${isPublic ? 'Público' : 'Privado'}</li>
      </ul>
        <h4>Detalle de Respuestas:</h4>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
          <tr>
            <th>Pregunta</th>
            <th>Respuesta</th>
            <th>Puntuación</th>
          </tr>
          ${details}
        </table>
        <p>Por favor, revisa los resultados detallados en el formulario.</p>
      `
    });
  }
}
'''

def configurar_notificaciones_form(form_id: str, es_publico: bool = False, es_obligatorio: bool = False):
    """{{ _('Configurar notificaciones automáticas para un formulario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return False

        # Construir el servicio de Apps Script
        script_service = build('script', 'v1', credentials=creds)

        # Crear un nuevo proyecto de Apps Script
        project = {
            'title': f'Notificaciones Test Estrés - {form_id}',
            'parentId': form_id
        }
        
        # Crear el proyecto
        created_project = script_service.projects().create(body=project).execute()
        project_id = created_project['scriptId']

        # Configurar el contenido del script
        files = [{
            'name': 'Código',
            'type': 'SERVER_JS',
            'source': NOTIFICATION_SCRIPT
        }, {
            'name': 'appsscript',
            'type': 'JSON',
            'source': '''{"timeZone":"America/Guayaquil","dependencies":{"enabledAdvancedServices":[{"userSymbol":"Forms","version":"v1","serviceId":"forms"}]},"exceptionLogging":"STACKDRIVER","runtimeVersion":"V8"}'''
        }]

        # Actualizar el contenido del proyecto
        script_service.projects().updateContent(
            scriptId=project_id,
            body={'files': files}
        ).execute()

        # Crear una nueva versión
        version = script_service.projects().versions().create(
            scriptId=project_id,
            body={'description': 'Initial version'}
        ).execute()

        # Crear una implementación
        deployment = script_service.projects().deployments().create(
            scriptId=project_id,
            body={
                'versionNumber': version['versionNumber'],
                'manifestFileName': 'appsscript',
                'description': 'Deployment for form notifications'
            }
        ).execute()

        # Configurar propiedades iniciales
        request = {
            'function': 'configurarFormulario',
            'parameters': [es_publico, es_obligatorio]
        }
        script_service.scripts().run(
            scriptId=project_id,
            body=request
        ).execute()

        # Crear el trigger para onFormSubmit
        trigger = {
            'eventType': 'ON_FORM_SUBMIT',
            'functionName': 'onFormSubmit'
        }
        script_service.projects().triggers().create(
            scriptId=project_id,
            body=trigger
        ).execute()

        logger.info(f"✅ Notificaciones configuradas exitosamente para el formulario {form_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Error al configurar notificaciones: {str(e)}")
        return False

def actualizar_permisos_form(form_id: str, es_publico: bool):
    """{{ _('Actualizar la privacidad de un formulario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return False

        # Construir el servicio de Google Drive
        drive_service = build('drive', 'v3', credentials=creds)

        # Configurar los permisos según la privacidad
        if es_publico:
            # Hacer público - cualquiera con el enlace puede ver
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
        else:
            # Hacer privado - solo usuarios específicos
            permission = {
                'type': 'private'
            }

        # Actualizar los permisos
        drive_service.permissions().create(
            fileId=form_id,
            body=permission
        ).execute()

        logger.info(f"✅ Privacidad actualizada exitosamente para el formulario {form_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Error al actualizar privacidad: {str(e)}")
        return False

def compartir_formulario_varios_correo(form_id: str, correos: list):
    """{{ _('Compartir formulario con varios correos') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return False

        # Construir el servicio de Google Drive
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Compartir el formulario con cada correo
        for correo in correos:
            permission = {
                'type': 'user',
                'role': 'reader',
                'emailAddress': correo
            }
            drive_service.permissions().create(
                fileId=form_id,
                body=permission,
                sendNotificationEmail=True
            ).execute()
        
        logger.info(f"✅ Formulario compartido exitosamente con {len(correos)} usuarios")
        return True
    except Exception as e:
        logger.error(f"❌ Error al compartir formulario: {str(e)}")
        return False

def eliminar_permisos_form(form_id: str, correos: list):
    """{{ _('Eliminar permisos de acceso al formulario') }}"""
    try:
        success, creds = verify_credentials()
        if not success:
            return False

        # Construir el servicio de Google Drive
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Obtener permisos actuales
        permisos = drive_service.permissions().list(fileId=form_id).execute()
        
        # Eliminar permisos para los correos especificados
        for permiso in permisos.get('permissions', []):
            if permiso.get('emailAddress') in correos:
                drive_service.permissions().delete(
                    fileId=form_id,
                    permissionId=permiso['id']
                ).execute()
        
        logger.info(f"✅ Permisos eliminados exitosamente para {len(correos)} usuarios")
        return True
    except Exception as e:
        logger.error(f"❌ Error al eliminar permisos: {str(e)}")
        return False
