from apps.lib.decoradors.decoradors import getter_setter, from_to_dict

@getter_setter()
@from_to_dict()
class Paralelo:
    def __init__(self):
        self.__uid = ""
        self.__nombre = ""
        self.__materia_uid = ""
        self.__descripcion = ""
        self.__docente_uid = ""
        self.__estudiantes = []
        self.__actividades = []