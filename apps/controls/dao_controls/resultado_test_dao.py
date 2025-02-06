from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.resultado_test import ResultadoTest

class ResultadoTestDAO(DAOControl):
    def __init__(self):
        super().__init__(ResultadoTest())
        self._resultado_test = ResultadoTest()
        self._collection_name = "resultados_test"

    @property
    def resultado_test(self):
        return self._resultado_test

    @resultado_test.setter
    def resultado_test(self, resultado_test):
        self._resultado_test = resultado_test

    def save(self):
        """Guardar resultado de test en la base de datos"""
        return super().save(self._resultado_test)

    def update(self):
        """Actualizar resultado de test en la base de datos"""
        return super().update(self._resultado_test)

    def delete(self, uid):
        """Eliminar resultado de test de la base de datos"""
        return super().delete(uid, ResultadoTest)

    def get(self, uid):
        """Obtener resultado de test por ID"""
        return super().get(uid, ResultadoTest)

    def get_all(self):
        """Obtener todos los resultados de test"""
        return super().get(ResultadoTest)

    def get_by_estudiante(self, estudiante_uid):
        """Obtener todos los resultados de test de un estudiante"""
        return self.get_all_documents_by_attribute("estudiante_uid", estudiante_uid, ResultadoTest)

    def get_by_test(self, test_uid):
        """Obtener todos los resultados de un test específico"""
        return self.get_all_documents_by_attribute("test_uid", test_uid, ResultadoTest)

    def get_resultados_publicos(self):
        """Obtener todos los resultados públicos"""
        return self.get_all_documents_by_attribute("publico", True, ResultadoTest)
