
from apps.lib.services.usuarios.usuarios import obtener_correo_usuarios
from apps.controls.dao_controls.usuario_dao import UsuarioDAO
from typing import List

def crear_usuarios_con_coreos_no_existentes(df, tipo_usuario):
    correos_no_exist = correos_no_existentes(df)

    
    for correo in correos_no_exist:
        correo = correo.lower()
        data = df[df['Correo'] == correo].to_dict('records')[0]
        usuario = UsuarioDAO()
        
        nombres = data['Nombre'].strip().split(' ')
        apellidos = data['Apellido'].strip().split(' ')
        usuario._usuario.primer_nombre = nombres[0]
        usuario._usuario.segundo_nombre = " ".join(nombres[1:]) if len(nombres) > 1 else ''
        usuario._usuario.primer_apellido = apellidos[0]
        usuario._usuario.segundo_apellido = " ".join(apellidos[1:]) if len(apellidos) > 1 else ''
        usuario._usuario.cedula = data['Cedula']
        usuario._usuario.correo = data['Correo']
        usuario._usuario.rol = tipo_usuario

        usuario.registrar_usuario(usuario, 
                                  es_estudiante=True if tipo_usuario == 'estudiante' else False, 
                                  es_docente=True if tipo_usuario == 'docente' else False)
        

    return len(correos_no_exist)
        
    

def correos_no_existentes(df) -> List[str]:
    """Revisa si los correos ya existen en la base de datos"""
    correos = obtener_correo_usuarios()
    df_correos = df['Correo'].tolist()
    aux = []
    for correo in df_correos:
        if correo not in correos:
            aux.append(correo)
    return aux
