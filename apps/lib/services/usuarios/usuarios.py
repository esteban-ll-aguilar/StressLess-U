from firebase_admin import auth

def obtener_correo_usuarios():
    usuarios = []
    pagina = auth.list_users()

    while pagina:
        for usuario in pagina.users:
            usuarios.append(usuario.email)
        pagina = pagina.get_next_page()

    return usuarios


def validar_correo(email: str) -> bool:
    try:
        if email.endswith('@unl.edu.ec'):
            raise ValueError('Error el correo debe ser @unl.edu.ec')
        else:
            return True
    except Exception as e:
        print(e)
        raise e