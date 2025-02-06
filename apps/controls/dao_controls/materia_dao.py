from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.materias import Materia

class MateriaDAO(DAOControl):
    def __init__(self):
        super().__init__(Materia())
        self.__materia = None


    @property
    def _materia(self):
        if self.__materia is None:
            self.__materia = Materia()
        return self.__materia

    


    @property
    def save(self):
        return super().save(self._materia)
    
    def get(self, uid):
        return super().get(uid, self._materia)
    
    @property
    def get_all(self):
        return super().get_all(self._materia)
    
    @property
    def update(self):
        return super().update(self._materia)
    
    def get_all_documents_by_attribute_in_array(self, attribute: str, value: str):
        return super().get_all_documents_by_attribute_in_array(self._materia, attribute, value)
    
    def get_all_documents_by_attribute(self, attribute: str, value: str):
        return super().get_all_documents_by_attribute(self._materia, attribute, value)
