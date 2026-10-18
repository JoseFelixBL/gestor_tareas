"""Capa de dominio: gestiona tareas sobre un almacén persistente."""

from __future__ import annotations

from gestor_tareas.almacenamiento import AlmacenTareas
from gestor_tareas.modelos import Tarea


class RepositorioTareas:
    """Gestiona el ciclo de vida de las tareas.

    Envuelve un AlmacenTareas y añade operaciones de dominio:
    asignación de IDs, búsqueda, filtros.

    Attributes:
        almacen: Almacén subyacente usado para persistir.
    """

    def __init__(self, almacen: AlmacenTareas) -> None:
        self.almacen = almacen

    def agregar(self, titulo: str, descripcion: str = "") -> Tarea:
        """Crea una nueva tarea y la persiste.

        Args:
            titulo: Título de la tarea.
            descripcion: Descripción opcional.

        Returns:
            La tarea creada.
        """
        siguiente_id, tareas = self.almacen.cargar()
        tarea = Tarea(id=siguiente_id, titulo=titulo, descripcion=descripcion)
        tareas.append(tarea)
        self.almacen.guardar(siguiente_id + 1, tareas)
        return tarea

    def listar(self, *, solo_pendientes: bool = False) -> list[Tarea]:
        """Devuelve todas las tareas, opcionalmente solo las pendientes.

        Args:
            solo_pendientes: Si es True, omite las completadas.

        Returns:
            Lista de tareas, ordenadas por id.
        """
        _, tareas = self.almacen.cargar()
        if solo_pendientes:
            tareas = [t for t in tareas if not t.esta_completada]
        return sorted(tareas, key=lambda t: t.id)

    def obtener(self, id_tarea: int) -> Tarea:
        """Devuelve la tarea con el id indicado.

        Args:
            id_tarea: Identificador de la tarea.

        Returns:
            La tarea correspondiente.

        Raises:
            KeyError: Si no existe una tarea con ese id.
        """
        _, tareas = self.almacen.cargar()
        return self._buscar_en_lista(tareas, id_tarea)

    def completar(self, id_tarea: int) -> Tarea:
        """Marca como completada la tarea indicada.

        Args:
            id_tarea: Identificador de la tarea.

        Returns:
            La tarea actualizada.

        Raises:
            KeyError: Si no existe la tarea.
            ValueError: Si ya estaba completada.
        """
        siguiente_id, tareas = self.almacen.cargar()
        tarea = self._buscar_en_lista(tareas, id_tarea)
        tarea.completar()
        self.almacen.guardar(siguiente_id, tareas)
        return tarea

    def reabrir(self, id_tarea: int) -> Tarea:
        """Reabre la tarea indicada.

        Args:
            id_tarea: Identificador de la tarea.

        Returns:
            La tarea actualizada.

        Raises:
            KeyError: Si no existe la tarea.
            ValueError: Si ya estaba pendiente.
        """
        siguiente_id, tareas = self.almacen.cargar()
        tarea = self._buscar_en_lista(tareas, id_tarea)
        tarea.reabrir()
        self.almacen.guardar(siguiente_id, tareas)
        return tarea

    def eliminar(self, id_tarea: int) -> None:
        """Elimina la tarea indicada.

        Args:
            id_tarea: Identificador de la tarea.

        Raises:
            KeyError: Si no existe la tarea.
        """
        siguiente_id, tareas = self.almacen.cargar()
        self._buscar_en_lista(tareas, id_tarea)  # valida existencia
        tareas = [t for t in tareas if t.id != id_tarea]
        self.almacen.guardar(siguiente_id, tareas)

    @staticmethod
    def _buscar_en_lista(tareas: list[Tarea], id_tarea: int) -> Tarea:
        """Busca una tarea por id dentro de una lista.

        Raises:
            KeyError: Si no se encuentra.
        """
        for tarea in tareas:
            if tarea.id == id_tarea:
                return tarea
        raise KeyError(f"No existe la tarea con id {id_tarea}")

    def buscar(self, texto: str) -> list[Tarea]:
        """Busca tareas cuyo título o descripción contengan el texto.

        La búsqueda es case-insensitive.

        Args:
            texto: Substring a buscar. Si está vacío, devuelve todas.

        Returns:
            Lista de tareas coincidentes, ordenadas por id.
        """
        texto = texto.strip().lower()
        _, tareas = self.almacen.cargar()
        if not texto:
            return sorted(tareas, key=lambda t: t.id)
        coincidencias = [
            t
            for t in tareas
            if texto in t.titulo.lower() or texto in t.descripcion.lower()
        ]
        return sorted(coincidencias, key=lambda t: t.id)

    def editar(
        self,
        id_tarea: int,
        *,
        titulo: str | None = None,
        descripcion: str | None = None,
    ) -> Tarea:
        """Edita el título y/o la descripción de una tarea.

        Args:
            id_tarea: Identificador de la tarea.
            titulo: Nuevo título, o None para no cambiarlo.
            descripcion: Nueva descripción, o None para no cambiarla.

        Returns:
            La tarea actualizada.

        Raises:
            KeyError: Si no existe la tarea.
            ValueError: Si no se proporciona ningún cambio, o si el título
                resultante queda vacío.
        """
        if titulo is None and descripcion is None:
            raise ValueError("Debes indicar al menos un campo a editar")

        siguiente_id, tareas = self.almacen.cargar()
        tarea = self._buscar_en_lista(tareas, id_tarea)

        if titulo is not None:
            if not titulo.strip():
                raise ValueError("El título no puede quedar vacío")
            tarea.titulo = titulo.strip()

        if descripcion is not None:
            tarea.descripcion = descripcion.strip()

        self.almacen.guardar(siguiente_id, tareas)
        return tarea
