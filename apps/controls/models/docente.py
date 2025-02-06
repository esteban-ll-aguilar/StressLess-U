from apps.controls.models.usuarios import Usuario

class Docente(Usuario):
    def __init__(self):
        super().__init__()
        self._Usuario__datos.update({
            "rol": "docente",
            "estudiantes": [],
            "test_estres": [],
            "actividades": []
        })
