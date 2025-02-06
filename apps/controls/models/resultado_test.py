from apps.lib.decoradors.decoradors import getter_setter, from_to_dict

@getter_setter()
@from_to_dict()
class ResultadoTest:
    def __init__(self):
        self.__uid = ""
        self.__test_uid = ""  # ID del test de estrés
        self.__estudiante_uid = ""  # ID del estudiante
        self.__fecha = None  # Fecha de realización
        self.__respuestas = {}  # Diccionario con las respuestas
        self.__nivel_estres = 0  # Nivel de estrés calculado
        self.__es_critico = False  # Si el nivel es crítico
        self.__notificado = False  # Si ya se notificó el nivel crítico
        self.__publico = True  # Si el resultado es público o privado
