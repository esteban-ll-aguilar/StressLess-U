from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.reporte_estres import ReporteEstres

class ReporteEstresDAO(DAOControl):
    def __init__(self):
        super().__init__(ReporteEstres())
        self.__reporte_estres = None


    @property
    def _reporte_estres(self):
        if self.__reporte_estres is None:
            self.__reporte_estres = ReporteEstres()
        return self.__reporte_estres

    @_reporte_estres.setter
    def _reporte_estres(self, value):
        self.__reporte_estres = value


    @property
    def save(self):
        return super().save(self._reporte_estres)
    
    def get(self, uid):
        return super().get(uid, self._reporte_estres)
    
    @property
    def get_all(self):
        return super().get_all(self._reporte_estres)
    
    @property
    def update(self):
        return super().update(self._reporte_estres)
    
