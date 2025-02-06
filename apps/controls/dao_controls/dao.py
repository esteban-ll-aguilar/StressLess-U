from apps import db
import os, sys
class DAOControl:
    def __init__(self, object: object):
        self.__db = db
        # Obtener el nombre del archivo donde se encuentra la clase
        self.__modulo = sys.modules[object.__module__]
        self.__name_colection = self.get_module_name()

    @property
    def _name_colection(self):
        return self.__name_colection

    @property
    def _db(self):
        return self.__db
    
    def save(self, object: object, uid: str = ''):
        """Guarda un nuevo documento en la colección y actualiza el UID."""
        try:
            # Crear el documento y obtener la referencia
            if uid == '':
                doc_ref = self._db.collection(self._name_colection).document()
                uid = doc_ref.id
            else:
                doc_ref = self._db.collection(self._name_colection).document(uid)

            # Actualizar el UID en el objeto
            object.uid = uid
            print(object.to_dict)
            # Guardar el documento con el UID actualizado
            doc_ref.set(object.to_dict)
            
            return uid
        except Exception as e:
            print(e)
    
    def get(self,uid: str, object: object):
        """Obtiene un documento por su ID."""
        doc = self._db.collection(self._name_colection).document(uid).get()
        if doc.exists:
            return object.from_dict(doc.to_dict())
        return None
    
    def get_all(self, object: object):
        """Obtiene todos los documentos de la colección."""
 
        
        #traer todos los documentos que tengan el campo uid
        docs = self._db.collection(self._name_colection).where('uid', '!=', '').stream()
        list_objects = []
        for doc in docs:
            list_objects.append(object.from_dict(doc.to_dict()))
        return list_objects
    
    def update(self, object: object):
        """Actualiza un documento existente."""
        uid = str(object.uid) if isinstance(object.uid, int) else object.uid
        return self._db.collection(self._name_colection).document(uid).update(object.to_dict)
    
    def delete(self, uid: str):
        """Elimina un documento por su ID."""
        return self._db.collection(self._name_colection).document(uid).delete()
    

    def get_all_documents_by_attribute(self, object: object, attribute: str, condition: str) -> list:
        """
        Obtiene todos los documentos de la colección que cumplan con una condición de igualdad.

        Args:
            object (object): La clase del objeto que se va a instanciar con los datos del documento.
            attribute (str): El nombre del atributo que se va a buscar.
            condition (str): El valor que debe coincidir con el atributo.

        Returns:
            list: Una lista de objetos instanciados con los datos de los documentos que cumplen la condición.
        """
        docs = self._db.collection(self._name_colection).where(attribute, '==', condition).stream()
        list_objects = []
        for doc in docs:
            list_objects.append(object.from_dict(doc.to_dict()))
        return list_objects
    
    
    def get_all_documents_by_attribute_in_array(self, object: object, attribute: str, condition: str) -> list:
        """
            Obtiene todos los documentos de la colección que contienen un valor específico dentro de un array.

            Args:
                object (object): La clase del objeto que se va a instanciar con los datos del documento.
                attribute (str): El nombre del atributo que se va a buscar dentro del array.
                condition (str): El valor que debe estar contenido dentro del array.

            Returns:
                list: Una lista de objetos instanciados con los datos de los documentos que cumplen la condición.
        """
        docs = self._db.collection(self._name_colection).where(attribute, 'array_contains', condition).stream()
        list_objects = []
        for doc in docs:
            list_objects.append(object.from_dict(doc.to_dict()))
        return list_objects

    def get_all_documentes_by_uids_list(self, object: object, attribute: str, listuids: list) -> list: 
        """
        Obtiene todos los documentos de la colección cuyos valores de un atributo están en una lista de valores.

        Args:
            object (object): La clase del objeto que se va a instanciar con los datos del documento.
            attribute (str): El nombre del atributo que se va a buscar.
            listuids (list): Una lista de valores que deben coincidir con los valores del atributo.

        Returns:
            list: Una lista de objetos instanciados con los datos de los documentos que cumplen la condición.
        """
        if not listuids:
            return []
            
        docs = self._db.collection(self._name_colection).where(attribute, 'in', listuids).stream()
        list_objects = []
        for doc in docs:
            list_objects.append(object.from_dict(doc.to_dict()))
        return list_objects
    
    def update_status_of_collection_in_many_documents(self, attribute: str, new_status: str, uid_collections: list) -> bool:
        """Actualiza el estado de un conjunto de documentos en la colección.

        Args:
            new_status (str): El nuevo estado del documento.
            condition (str): La condición para actualizar el estado.
            uid_collections (list): Una lista de IDs de documentos a actualizar.

        Returns:
            None
        """
        if len(uid_collections) == 0:
            return False

        batch = self._db.batch()
        for uid in uid_collections:
            doc = self._db.collection(self._name_colection).document(uid)
            batch.update(doc, {attribute: new_status})
        
        try:
            batch.commit()
            print(f"Documentos actualizados en {self._name_colection}")
            return True
        except Exception as e:
            print(e)
            return False
    


    def get_module_name(self):
    # str(os.path.basename(self.__modulo.__file__)[:-3]) 
        name = str(os.path.basename(self.__modulo.__file__)[:-3]) 
        if name == 'estudiante' or name == 'docente' or name == 'administrador':
            return 'usuario'
        return name
