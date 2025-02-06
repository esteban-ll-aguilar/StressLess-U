from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.estudiante import Estudiante
from apps import db, firebase
import firebase_admin
from firebase_admin import auth

class EstudianteDAO(DAOControl):
    def __init__(self):
        super().__init__(Estudiante())
        self.__estudiante = None


    @property
    def _estudiante(self):
        if self.__estudiante is None:
            self.__estudiante = Estudiante()

        return self.__estudiante

    @_estudiante.setter
    def _estudiante(self, value):
        self.__estudiante = value


    def save(self, uid: str = ''):
        return super().save(object=self._estudiante, uid=uid)
    
    def get(self, uid):
        usuario =db.collection('usuarios').document(uid).get()
        return Estudiante().from_dict(usuario.to_dict())
    
    @property
    def get_all(self):
        return super().get_all(object=self._estudiante)
    
    @property
    def update(self):
        objecto = self._estudiante
        uid = str(objecto.uid) if isinstance(objecto.uid, int) else objecto.uid
        return db.collection('usuarios').document(uid).update(objecto.to_dict)
    
    def get_all_documents_by_attribute(self, attribute: str, condition: str):
        """Obtener documentos por atributo"""
        from apps import db 
        docs = db.collection('usuarios').where(attribute, '==', condition).stream()
        list_objects = []
        for doc in docs:
            list_objects.append(Estudiante().from_dict(doc.to_dict()))
        return list_objects
    
    def get_all_documentes_by_uids_list(self, attribute: str, listuids: list):
        """Obtener documentos por lista de UIDs"""
        return super().get_all_documentes_by_uids_list(self._estudiante, attribute, listuids)
    
    def obtener_usuarios_con_rol(self, rol: str):
        """Obtener usuarios por rol"""
        from apps import db 
        users = db.collection('usuarios').where('rol', '==', rol).stream()
        list_users = []
        for user in users:
            list_users.append(Estudiante().from_dict(user.to_dict()))
        return list_users



