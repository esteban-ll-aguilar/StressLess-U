from apps.lib.decoradors.decoradors import getter_setter, from_to_dict

@getter_setter()
@from_to_dict()
class Materia:
    def __init__(self):
        self.__uid = ""
        self.__nombre = ""
        self.__descripcion = ""
 