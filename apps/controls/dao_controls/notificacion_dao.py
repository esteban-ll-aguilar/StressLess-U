from apps.controls.dao_controls.dao import DAOControl
from apps.controls.models.notificacion import Notificacion
from datetime import datetime

class NotificacionDAO(DAOControl):
    def __init__(self):
        super().__init__(Notificacion())
        self._notificacion = Notificacion()
        self._collection_name = "notificaciones"

    @property
    def notificacion(self):
        return self._notificacion

    @notificacion.setter
    def notificacion(self, notificacion):
        self._notificacion = notificacion

    def save(self):
        """Guardar notificación en la base de datos"""
        return super().save(self._notificacion)

    def update(self):
        """Actualizar notificación en la base de datos"""
        return super().update(self._notificacion)

    def delete(self, uid):
        """Eliminar notificación de la base de datos"""
        return super().delete(uid, Notificacion)

    def get(self, uid):
        """Obtener notificación por ID"""
        return self._get_document(uid, Notificacion)

    def get_all(self):
        """Obtener todas las notificaciones"""
        return self._get_all_documents(Notificacion)

    def get_by_docente(self, docente_uid):
        """Obtener todas las notificaciones de un docente"""
        return super().get_all_documents_by_attribute(attribute="docente_uid",condition=docente_uid,object= Notificacion)

    def get_no_leidas_by_docente(self, docente_uid):
        """Obtener notificaciones no leídas de un docente"""
        return self._get_all_documents_by_multiple_attributes({
            "docente_uid": docente_uid,
            "leida": False
        }, Notificacion)

    def crear_notificacion_nivel_critico(self, docente_uid, estudiante_uid, resultado_test_uid, nivel_estres):
        """Crear una notificación de nivel crítico de estrés"""
        self._notificacion = Notificacion()
        self._notificacion.tipo = "nivel_critico"
        self._notificacion.mensaje = f"Nivel de estrés crítico detectado ({nivel_estres}%)"
        self._notificacion.fecha = datetime.now()
        self._notificacion.leida = False
        self._notificacion.docente_uid = docente_uid
        self._notificacion.estudiante_uid = estudiante_uid
        self._notificacion.resultado_test_uid = resultado_test_uid
        return self.save()

    def marcar_como_leida(self, uid):
        """Marcar una notificación como leída"""
        notificacion = self.get(uid)
        if notificacion:
            self._notificacion = notificacion
            self._notificacion.leida = True
            return self.update()
        return False

    def marcar_todas_como_leidas(self, docente_uid):
        """Marcar todas las notificaciones de un docente como leídas"""
        notificaciones = self.get_no_leidas_by_docente(docente_uid)
        for notificacion in notificaciones:
            self._notificacion = notificacion
            self._notificacion.leida = True
            self.update()
        return True
