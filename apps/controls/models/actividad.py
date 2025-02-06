from apps.lib.decoradors.decoradors import getter_setter, from_to_dict

@getter_setter()
@from_to_dict()
class Actividad:
    def __init__(self):
        self.__uid = ""
        self.__nombre = ""
        self.__descripcion = ""
        self.__fecha_entrega = None
        
        self.__paralelo_uid = ""
        self.__esta_activa = False
        self.__estudiantes = []
        self.__es_grupal = False
        self.__test_estres = ""
        self.__link_test = ""
        self.__es_obligatoria = False
        self.__es_publico = False  # True si los resultados son públicos
        self.__estado = "pendiente"  # valores: "pendiente" o "completada"
