from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.docente import Docente
from apps import db, firebase
import firebase_admin
from firebase_admin import auth

class DocenteDAO(DAOControl):
    def __init__(self):
        super().__init__(Docente())
        self.__docente = None


    @property
    def _docente(self):
        if self.__docente is None:
            self.__docente = Docente()

        return self.__docente

    @_docente.setter
    def _docente(self, value):
        self.__docente = value


    def save(self, uid: str = ''):
        return super().save(object=self._docente, uid=uid)
    
    def get(self, uid):
        usuario =db.collection('usuarios').document(uid).get()
        return Docente().from_dict(usuario.to_dict())
    
    @property
    def get_all(self):
        return super().get_all(self._docente)
    
    @property
    def update(self):
        objecto = self._estudviante
        uid = str(objecto.uid) if isinstance(objecto.uid, int) else objecto.uid
        return db.collection('usuarios').document(uid).update(objecto.to_dict)
    
    