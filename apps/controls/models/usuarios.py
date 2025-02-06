from ast import Dict
from flask_login import UserMixin
from typing import Dict, Any

class Usuario(UserMixin):
    def __init__(self):
        self.__datos = {
            "uid": "",
            "rol": "",
            "segundo_apellido": "",
            "primer_apellido": "",
            "segundo_nombre": "",
            "primer_nombre": "",
            "fecha_nacimiento": "",
            "correo": "",
            "cedula": "",
            "telefono": "",
            "foto_url": "",  # Campo añadido para la foto de perfil
            "credenciales": {},
            "esta_activo": True,  # Campo para controlar si el usuario está activo o dado de baja
            "settings": {
                'languagePreference': 'en',
                "layout": {
                    "type": "menu-light",  # Valores posibles: "menu-dark", "menu-light", "dark"
                    "headerColor": "header-blue",  # Valores posibles: "header-blue", "header-red", "header-purple", "header-info", "header-dark", "header-orenge", "header-green", "header-yellow", "header-orchidgreen", "header-indigogreen", "header-darkgreen", "header-darkblue"
                    "rtlEnabled": False,  # true/False para RTL
                    "menuFixed": True,   # true/False para Sidebar Fixed
                    "headerFixed": False, # true/False para Header Fixed
                    "boxLayout": False,  # true/False para Box Layouts
                    "breadcrumbSticky": False  # true/False para Breadcrumb sticky
                },
            }
        }

    def get_id(self):
        """Método requerido por Flask-Login"""
        return str(self.__datos.get('uid'))

    def __getattr__(self, name: str):
        if name in self.__datos:
            return self.__datos[name]
        raise AttributeError(f"❌​ ​'{type(self).__name__}' no tiene el atributo '{name}'")

    def __setattr__(self, name: str, value: any):
        if name.startswith("_Usuario__") or name in ("__datos",):
            super().__setattr__(name, value)
        elif name in self.__datos:
            self.__datos[name] = value
        else:
            raise AttributeError(f"❌​ ​'{type(self).__name__}' no tiene el atributo '{name}'")

    @staticmethod
    def from_dict(data: dict) -> object:
        """{{ _('Crear instancia de usuario según su rol') }}"""
        from apps.controls.models.estudiante import Estudiante
        from apps.controls.models.docente import Docente
        from apps.controls.models.administrador import Administrador

        # Determinar la clase correcta basada en el rol
        rol = data.get('rol', '')
        UserClass = {
            'estudiante': Estudiante,
            'docente': Docente,
            'administrador': Administrador
        }.get(rol, Usuario)

        # Crear instancia de la clase correspondiente
        instance = UserClass()
        
        # Actualizar datos base
        instance._Usuario__datos.update({
            "uid": data.get('uid', ''),
            "rol": rol,
            "segundo_apellido": data.get('segundo_apellido', ''),
            "primer_apellido": data.get('primer_apellido', ''),
            "segundo_nombre": data.get('segundo_nombre', ''),
            "primer_nombre": data.get('primer_nombre', ''),
            "fecha_nacimiento": data.get('fecha_nacimiento', ''),
            "correo": data.get('correo', ''),
            "cedula": data.get('cedula', ''),
            "telefono": data.get('telefono', ''),
            "foto_url": data.get('foto_url', ''),  # Añadido para la foto de perfil
            "credenciales": data.get('credenciales', {}),
            "esta_activo": data.get('esta_activo', True),  # Por defecto el usuario está activo
        })

        # Actualizar configuraciones
        default_settings = instance._Usuario__datos['settings']
        instance._Usuario__datos['settings'] = {**default_settings, **data.get('settings', {})}

        # Actualizar datos específicos del rol
        if rol == 'estudiante':
            instance._Usuario__datos.update({
                "actividades": data.get('actividades', []),
                "docentes": data.get('docentes', []),
                "test_estres": data.get('test_estres', [])
            })
        elif rol == 'docente':
            instance._Usuario__datos.update({
                "estudiantes": data.get('estudiantes', []),
                "actividades": data.get('actividades', []),
                "test_estres": data.get('test_estres', [])
            })
        elif rol == 'administrador':
            # instance._Usuario__datos.update({
            #     "permisos": data.get('permisos', [])
            # })
            pass

        return instance

    @property
    def to_dict(self) -> Dict[str, Any]:
        return self.__datos
