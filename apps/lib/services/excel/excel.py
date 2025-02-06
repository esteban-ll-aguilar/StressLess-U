from io import BytesIO
import pandas as pd
from flask_babel import gettext
from apps import logger, firebase, db
from apps.controls.dao_controls.estudiante_dao import EstudianteDAO
from apps.controls.dao_controls.docente_dao import DocenteDAO
from typing import List, Dict, Any
from apps.lib.services.excel.usuarios import crear_usuarios_con_coreos_no_existentes


def procesar_excel(file, tipo_usuario):
    """Procesa un archivo Excel para crear usuarios"""
    try:
        # Leer el archivo Excel directamente desde el objeto FileStorage
        df = pd.read_excel(BytesIO(file.read()))

        print(df)
        if df.empty:
            raise ValueError('Error, el archivo Excel esta vacio')
        if tipo_usuario == 'estudiante':
            if not revisar_cabecera(df, ['Nombre', 'Apellido', 'Correo', 'Cedula']):
                raise KeyError('Error, cabeceras del excel para el estudiante no son correctas o no existen')
        elif tipo_usuario == 'docente': 
            if not revisar_cabecera(df, ['Nombre', 'Apellido', 'Correo', 'Materia', 'Ciclo', 'Paralelo', 'Cedula']):
                raise KeyError('Error, cabeceras del excel para el docente  no son correctas o no existen')
        if not revisar_correos(df):
            raise KeyError('Error, correos del excel no son correctos')
        if revisar_si_existen_datos_faltantes(df):
            raise KeyError('❌ Error, existen datos faltantes en el excel')
        
        
        creados = crear_usuarios_con_coreos_no_existentes(df, tipo_usuario)

        return True > 0, creados
        
    except Exception as e:
        logger.error(f"❌​ ​Error al procesar archivo Excel: {str(e)}")
        return False, str(e)



def revisar_cabecera(df, cabeceras: List[str]) -> bool:
    """Revisa si la cabecera del archivo Excel es correcta"""
    return all(cabecera in df.columns for cabecera in cabeceras) \
           and len(df.columns) == len(cabeceras)

def revisar_correos(df):
    """Revisa que los correos rengan el formato @unl.edu.ec"""
    df_correos = df['Correo'].tolist()
    return all(correo.endswith('@unl.edu.ec') for correo in df_correos)

def revisar_si_existen_datos_faltantes(df):
    """Revisa si existen datos faltantes en el archivo Excel"""
    return df.isnull().values.any()


        






    