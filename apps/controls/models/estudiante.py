from apps.controls.models.usuarios import Usuario

class Estudiante(Usuario):
    def __init__(self):
        super().__init__()
        self._Usuario__datos.update({
            "rol": "estudiante",
            "actividades": [],
            "docentes": [],
            "test_estres": [],
            "paralelos": [],
        })
