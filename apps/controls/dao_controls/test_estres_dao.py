from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.test_estres import TestEstres
from apps import logging
from flask_babel import gettext

logger = logging.getLogger(__name__)

class TestEstresDAO(DAOControl):
    def __init__(self):
        super().__init__(TestEstres())
        self.__test_estres = None

    @property
    def _test_estres(self):
        if self.__test_estres is None:
            self.__test_estres = TestEstres()
        return self.__test_estres

    @_test_estres.setter
    def _test_estres(self, value):
        self.__test_estres = value

    @property
    def save(self):
        return super().save(self._test_estres)
    
    def get(self, uid):
        return super().get(uid, self._test_estres)
    
    @property
    def get_all(self):
        return super().get_all(self._test_estres)
    
    @property
    def update(self):
        return super().update(self._test_estres)
    
    def actualizar_privacidad(self, uid: str, es_publico: bool):
        """{{ _('Actualizar la privacidad de un test') }}"""
        try:
            test = self.get(uid)
            if not test:
                raise ValueError(gettext('Test no encontrado'))
            
            self._test_estres = test
            self._test_estres.es_publico = es_publico
            self.update
            return True
        except Exception as e:
            logger.error(f"❌ Error al actualizar privacidad: {str(e)}")
            raise e

    def agregar_estudiante(self, uid: str, estudiante_uid: str):
        """{{ _('Agregar un estudiante al test') }}"""
        try:
            test = self.get(uid)
            if not test:
                raise ValueError(gettext('Test no encontrado'))
            
            if estudiante_uid not in test.estudiantes:
                self._test_estres = test
                self._test_estres.estudiantes.append(estudiante_uid)
                self.update
            return True
        except Exception as e:
            logger.error(f"❌ Error al agregar estudiante: {str(e)}")
            raise e

    def eliminar_estudiante(self, uid: str, estudiante_uid: str):
        """{{ _('Eliminar un estudiante del test') }}"""
        try:
            test = self.get(uid)
            if not test:
                raise ValueError(gettext('Test no encontrado'))
            
            if estudiante_uid in test.estudiantes:
                self._test_estres = test
                self._test_estres.estudiantes.remove(estudiante_uid)
                self.update
            return True
        except Exception as e:
            logger.error(f"❌ Error al eliminar estudiante: {str(e)}")
            raise e

    def actualizar_estudiantes(self, uid: str, estudiantes: list):
        """{{ _('Actualizar la lista completa de estudiantes del test') }}"""
        try:
            test = self.get(uid)
            if not test:
                raise ValueError(gettext('Test no encontrado'))
            
            self._test_estres = test
            self._test_estres.estudiantes = estudiantes
            self.update
            return True
        except Exception as e:
            logger.error(f"❌ Error al actualizar estudiantes: {str(e)}")
            raise e
