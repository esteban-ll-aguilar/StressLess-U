from apps.lib.decoradors.decoradors import getter_setter, from_to_dict

@getter_setter()
@from_to_dict()
class ReporteEstres:
    def __init__(self):
        self.__uid = ""
        self.__fecha_reporte = None
        self.__test_estres = ""
        self.__descripcion = ""
        self.__docentes = []
        self.__administradores = []