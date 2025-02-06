from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.administrador import Administrador
from apps import db, firebase
from firebase_admin import auth

class AdministradorDAO(DAOControl):
    def __init__(self):
        super().__init__(Administrador())
        self.__administrador = None


    @property
    def _administrador(self):
        if self.__administrador is None:
            self.__administrador = Administrador()

        return self.__administrador

    @_administrador.setter
    def _administrador(self, value):
        self.__administrador = value


    def save(self, uid: str = ''):
        return super().save(object=self._administrador, uid=uid)
    
    def get(self, uid: str):
        usuario =db.collection('usuarios').document(uid).get()
        return Administrador().from_dict(usuario.to_dict())
    
    @property
    def get_all(self):
        return super().get_all(self._administrador)
    
    @property
    def update(self):
        objecto = self._administrador
        uid = str(objecto.uid) if isinstance(objecto.uid, int) else objecto.uid
        return db.collection('usuarios').document(uid).update(objecto.to_dict)
    
    