from flask import request, redirect, url_for
from flask_login import current_user
from functools import wraps
from typing import List
HOME_URL: str = 'home_blueprint.index'

def property_attributes(*attributes: str):
    """
    Decorador para generar automáticamente getters y setters para atributos.
    
    Args:
        *attributes: Lista de nombres de atributos para los que se generarán properties
    
    Ejemplo:
        @property_attributes('uid', 'nombre', 'descripcion')
        class Materia:
            def __init__(self):
                self.__uid = ""
                self.__nombre = ""
                self.__descripcion = ""
    """
    def decorator(cls):
        for attr in attributes:
            # Crear el nombre del atributo privado
            private_attr = f"_{cls.__name__}__{attr}"
            
            # Crear el getter
            def getter(self, attr_name=private_attr):
                return getattr(self, attr_name, None)
            
            # Crear el setter
            def setter(self, value, attr_name=private_attr):
                setattr(self, attr_name, value)
            
            # Agregar el property a la clase
            setattr(cls, attr, property(
                fget=getter,
                fset=setter,
                doc=f"Property para {attr}"
            ))
        
        return cls
    return decorator

def solo_permitido_a(administrador: bool = False, 
                     docente: bool = False, 
                     estudiante: bool = False):
    def wrapper(funcion):
        @wraps(funcion)
        def decorated_view(*args, **kwargs):
            if current_user.rol == 'administrador' and administrador or current_user.rol == 'docente' and docente or current_user.rol == 'estudiante' and estudiante:
                return funcion(*args, **kwargs)
            else:
                return redirect(url_for(HOME_URL))
        return decorated_view
    return wrapper


def getter_setter():
    """
    Decorador para agregar manejo dinámico de atributos privados.
    """
    def decorator(cls):
        # Guardar el constructor original
        orig_init = cls.__init__

        def new_init(self, *args, **kwargs):
            # Llamar al constructor original primero
            orig_init(self, *args, **kwargs)
            
            # Detectar atributos privados creados en __init__
            private_prefix = f"_{cls.__name__}__"
            private_attrs = [attr for attr in dir(self) if attr.startswith(private_prefix)]
            
            # Crear properties para cada atributo privado
            for private_attr in private_attrs:
                # Obtener el nombre público (sin los guiones bajos)
                public_name = private_attr.replace(private_prefix, '')
                
                # Solo crear la property si no existe ya
                if not hasattr(cls, public_name):
                    # Crear el getter
                    def make_getter(attr_name=private_attr):
                        def getter(self):
                            return getattr(self, attr_name)
                        return getter
                    
                    # Crear el setter
                    def make_setter(attr_name=private_attr):
                        def setter(self, value):
                            setattr(self, attr_name, value)
                        return setter
                    
                    # Agregar la property a la clase
                    setattr(cls, public_name, property(
                        fget=make_getter(),
                        fset=make_setter(),
                        doc=f"Property para {public_name}"
                    ))

        # Reemplazar el constructor
        cls.__init__ = new_init
        return cls
    return decorator



def from_to_dict():
    """
    Decorador para agregar métodos 'from_dict' y 'to_dict' a una clase.
    """
    def decorator(cls):
        @staticmethod
        def from_dict(data):
            """
            Crea una instancia de la clase decorada a partir de un diccionario.
            """
            instancia = cls()
            private_prefix = f"_{cls.__name__}__"
            
            # Obtener los atributos privados existentes
            private_attrs = [attr for attr in dir(instancia) if attr.startswith(private_prefix)]
            private_names = {attr.replace(private_prefix, ''): attr for attr in private_attrs}
            
            for key, value in data.items():
                if key in private_names:
                    setattr(instancia, private_names[key], value)
                else:
                    raise AttributeError(f"❌ '{cls.__name__}' no tiene el atributo '{key}'")
            return instancia
        
        def to_dict(self):
            """
            Devuelve un diccionario con los datos de la instancia.
            """
            private_prefix = f"_{cls.__name__}__"
            result = {}
            
            # Obtener los atributos privados existentes
            private_attrs = [attr for attr in dir(self) if attr.startswith(private_prefix)]
            
            for attr in private_attrs:
                # Convertir nombre privado a público
                public_name = attr.replace(private_prefix, '')
                result[public_name] = getattr(self, attr)
            
            return result
        
        # Reemplazar métodos en la clase decorada
        cls.from_dict = from_dict
        cls.to_dict = property(to_dict)

        return cls
    return decorator
