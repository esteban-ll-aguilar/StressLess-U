from apps.lib.decoradors.decoradors import getter_setter, from_to_dict

@getter_setter()
@from_to_dict()
class TestEstres:
    def __init__(self):
        self.__uid = ""
        self.__descripcion = ""
        self.__fecha = ""
        self.__estado = ""
        self.__preguntas = []
        self.__puntaje = 0
        self.__actividades = []
        self.__estudiantes = []  # Lista de estudiantes participantes
        self.__docente = ""
        self.__es_publico = False  # True si los resultados son públicos
        self.__form_id = ""  # ID del formulario de Google Forms
