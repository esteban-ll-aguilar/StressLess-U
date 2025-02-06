from apps.lib.decoradors.decoradors import getter_setter, from_to_dict

@getter_setter()
@from_to_dict()
class Notificacion:
    def __init__(self):
        self.__uid = ""
        self.__tipo = ""  # tipo de notificación (ej: "nivel_critico")
        self.__mensaje = ""  # mensaje de la notificación
        self.__fecha = None  # fecha de la notificación
        self.__leida = False  # si la notificación ha sido leída
        self.__docente_uid = ""  # ID del docente que recibe la notificación
        self.__estudiante_uid = ""  # ID del estudiante relacionado
        self.__resultado_test_uid = ""  # ID del resultado del test relacionado
