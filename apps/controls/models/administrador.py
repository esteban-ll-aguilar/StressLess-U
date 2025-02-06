from apps.controls.models.usuarios import Usuario

class Administrador(Usuario):
    def __init__(self):
        super().__init__()
        self._Usuario__datos.update({
            "rol": "administrador",
        })
