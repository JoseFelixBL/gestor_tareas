"""Persistencia de tareas en archivo JSON."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from gestor_tareas.modelos import EstadoTarea, Tarea


class AlmacenTareas:
    """Gestiona la lectura y escritura de tareas en un archivo JSON.

    Attributes:
        ruta: Ruta al archivo JSON donde se persisten las tareas.
    """

    def __init__(self, ruta: Path) -> None:
        """Inicializa el almacén.

        Args:
            ruta: Ruta al archivo JSON. No necesita existir.
        """
        self.ruta = ruta

    def cargar(self) -> list[Tarea]:
        """Carga las tareas desde el archivo.

        Returns:
            Lista de tareas. Lista vacía si el archivo no existe.

        Raises:
            ValueError: Si el archivo está corrupto o mal formado.
        """
        if not self.ruta.exists():
            return []

        try:
            contenido = self.ruta.read_text(encoding="utf-8")
            datos = json.loads(contenido)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"El archivo {self.ruta} no contiene JSON válido: {exc}"
            ) from exc

        if not isinstance(datos, list):
            tipo_recibido = type(datos).__name__
            raise ValueError(
                f"Se esperaba una lista en {self.ruta}, se encontró {tipo_recibido}"
            )

        return [self._dict_a_tarea(d) for d in datos]

    def guardar(self, tareas: list[Tarea]) -> None:
        """Guarda las tareas en el archivo.

        Args:
            tareas: Lista de tareas a persistir.
        """
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        datos = [self._tarea_a_dict(t) for t in tareas]
        self.ruta.write_text(
            json.dumps(datos, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    @staticmethod
    def _tarea_a_dict(tarea: Tarea) -> dict:
        """Convierte una tarea a diccionario serializable."""
        d = asdict(tarea)
        d["estado"] = tarea.estado.value  # Enum → string
        return d

    @staticmethod
    def _dict_a_tarea(d: dict) -> Tarea:
        """Convierte un diccionario a tarea.

        Raises:
            ValueError: Si faltan campos obligatorios o los tipos son inválidos.
        """
        try:
            return Tarea(
                id=d["id"],
                titulo=d["titulo"],
                descripcion=d.get("descripcion", ""),
                estado=EstadoTarea(d.get("estado", EstadoTarea.PENDIENTE.value)),
                creada_en=datetime.fromisoformat(d["creada_en"]),
                completada_en=(
                    datetime.fromisoformat(d["completada_en"])
                    if d.get("completada_en")
                    else None
                ),
            )
        except KeyError as exc:
            raise ValueError(f"Falta el campo obligatorio {exc} en la tarea") from exc
