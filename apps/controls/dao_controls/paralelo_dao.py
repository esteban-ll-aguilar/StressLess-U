from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.paralelo import Paralelo

class ParaleloDAO(DAOControl):
    def __init__(self):
        super().__init__(Paralelo())
        self.__paralelo = None


    @property
    def _paralelo(self):
        if self.__paralelo is None:
            self.__paralelo = Paralelo()
        return self.__paralelo
    
    @_paralelo.setter
    def _paralelo(self, value):
        self.__paralelo = value

    


    @property
    def save(self):
        return super().save(self._paralelo)
    
    def get(self, uid):
        return super().get(uid, self._paralelo)
    
    @property
    def get_all(self):
        return super().get_all(self._paralelo)
    
    @property
    def update(self):
        return super().update(self._paralelo)
    
    def get_all_documents_by_attribute_in_array(self, attribute: str, value: str):
        return super().get_all_documents_by_attribute_in_array(self._paralelo, attribute, value)
    
    def get_all_documents_by_attribute(self, attribute: str, value: str):
        return super().get_all_documents_by_attribute(self._paralelo, attribute, value)
    
    
