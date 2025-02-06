from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.usuarios import Usuario
from apps import db, firebase
import firebase_admin
from firebase_admin import auth
from flask_babel import gettext
from apps import logging

logger = logging.getLogger(__name__)

class UsuarioDAO(DAOControl):
    def __init__(self):
        super().__init__(Usuario())
        self.__usuario = None


    @property
    def _usuario(self):
        if self.__usuario is None:
            self.__usuario = Usuario()

        return self.__usuario

    @_usuario.setter
    def _usuario(self, value):
        self.__usuario = value


    def save(self, uid: str = ''):
        return super().save(object=self._usuario, uid=uid)
    
    def get(self, uid):
        return super().get(uid, self._usuario)
    
    @property
    def get_all(self):
        return super().get_all(self._usuario)
    
    @property
    def update(self):
        return super().update(self._usuario)
    
    @property
    def delete(self):
        return super().delete(self._usuario)

    def iniciar_sesion(self, email, password):
        try:
            user = firebase.auth().sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(e)
            return None

    def recuperar_contrasena(self, email):
        try:
            auth.generate_password_reset_link(email)
            return True
        except Exception as e:
            print(e)
            return False

    def cambiar_contrasena(self, uid, password):
        try:
            auth.update_user(uid, password=password)
            return True
        except Exception as e:
            print(e)
            return False
        
    def obtener_usuarios_con_rol(self, rol):
        """{{ _('Obtener usuarios con un rol específico') }}"""
        try:
            return super().get_all_documents_by_attribute(self._usuario, 'rol', rol)
        except Exception as e:
            logger.error(f"❌ Error al obtener usuarios con rol {rol}: {str(e)}")
            return []

    def cambiar_rol(self, uid: str, nuevo_rol: str):
        """{{ _('Cambiar el rol de un usuario') }}"""
        try:
            usuario_ref = db.collection('usuarios').document(uid)
            usuario_doc = usuario_ref.get()
            
            if not usuario_doc.exists:
                raise ValueError(gettext('Usuario no encontrado'))
            
            usuario_data = usuario_doc.to_dict()
            rol_actual = usuario_data.get('rol', '')
            
            # Preparar datos específicos según el nuevo rol
            updates = {'rol': nuevo_rol}
            
            
            usuario_ref.update(updates)
            logger.info(f"✅ Rol cambiado de {rol_actual} a {nuevo_rol} para usuario {uid}")
            return True
        except Exception as e:
            logger.error(f"❌ Error al cambiar rol: {str(e)}")
            raise e

    def eliminar_rol(self, uid: str):
        """{{ _('Eliminar el rol de un usuario') }}"""
        try:
            usuario_ref = db.collection('usuarios').document(uid)
            usuario_doc = usuario_ref.get()
            
            if not usuario_doc.exists:
                raise ValueError(gettext('Usuario no encontrado'))
            
            # Preparar datos para eliminar
            updates = {'rol': ''}
            
            usuario_ref.update(updates)
            logger.info(f"✅ Rol eliminado para usuario {uid}")
            return True
        except Exception as e:
            logger.error(f"❌ Error al eliminar rol: {str(e)}")
            raise e
        

    def registrar_usuario(self, usuario: object, es_administrador: bool = False, 
                          es_docente: bool = False, es_estudiante: bool = False):
        try:
            user_dao = usuario
            usuario = usuario._usuario
            print(usuario.to_dict)
            
            if es_estudiante:
                usuario.rol = 'estudiante'
            elif es_docente:
                usuario.rol = 'docente'
            elif es_administrador:
                usuario.rol = 'administrador'
            else:
                print('No se pudo determinar el rol del usuario.')
                return False

            #Preparar datos para Firestore
            try:
                user = firebase.auth().create_user_with_email_and_password(
                    email=usuario.correo,
                    password=str(usuario.cedula) # Usar la cédula como contraseña inicial
                )
                user_dao.save(uid=user['localId'])
                print('Usuario registrado con éxito.')
                return user['localId']

            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
            return False
