from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.actividad import Actividad

class ActividadDAO(DAOControl):
    def __init__(self):
        super().__init__(Actividad())
        self.__actividad = None


    @property
    def _actividad(self):
        if self.__actividad is None:
            self.__actividad = Actividad()
        return self.__actividad

    @_actividad.setter
    def _actividad(self, value):
        self.__actividad = value


    @property
    def save(self):
        return super().save(self._actividad)
    
    def get(self, uid):
        return super().get(uid, self._actividad)
    
    @property
    def get_all(self):
        return super().get_all(self._actividad)
    
    @property
    def update(self):
        return super().update(self._actividad)
    
    def get_all_documents_by_attribute(self, attribute: str, condition: str):
        return super().get_all_documents_by_attribute(self._actividad, attribute, condition)
    
    def get_actividades_by_estudiante(self, estudiante_id: str):
        """Obtiene todas las actividades asignadas a un estudiante específico"""
        # Obtener todas las actividades
        todas_actividades = self.get_all
        # Filtrar las actividades donde el estudiante esté en la lista de estudiantes
        actividades_estudiante = [
            actividad for actividad in todas_actividades 
            if estudiante_id in actividad.estudiantes and actividad.esta_activa
        ]
        # Ordenar por fecha de entrega
        actividades_estudiante.sort(key=lambda x: x.fecha_entrega if x.fecha_entrega else "9999-12-31")
        return actividades_estudiante
