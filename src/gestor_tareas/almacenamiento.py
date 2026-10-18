"""Persistencia de tareas en archivo JSON."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from gestor_tareas.modelos import EstadoTarea, Tarea


@dataclass
class _EstadoPersistido:
    """Formato del archivo en disco"""

    siguiente_id: int
    tareas: list[Tarea]


class AlmacenTareas:
    """Gestiona la lectura y escritura de tareas en un archivo JSON.

    El archivo tiene el formato:
        {
            "siguiente_id": 4,
            "tareas": [ ... ]
        }

    Attributes:
        ruta: Ruta al archivo JSON donde se persisten las tareas.
    """

    VERSION_ESQUEMA = 1

    def __init__(self, ruta: Path) -> None:
        """Inicializa el almacén.

        Args:
            ruta: Ruta al archivo JSON. No necesita existir.
        """
        self.ruta = ruta

    def cargar(self) -> tuple[int, list[Tarea]]:
        """Carga las tareas desde el archivo.

        Returns:
            Tupla (siguiente_id, tareas). Si el archivo no existe,
            devuelve (1, []).

        Raises:
            ValueError: Si el archivo está corrupto o mal formado.
        """
        if not self.ruta.exists():
            return 1, []

        try:
            contenido = self.ruta.read_text(encoding="utf-8")
            datos = json.loads(contenido)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"El archivo {self.ruta} no contiene JSON válido: {exc}"
            ) from exc

        siguiente_id = datos.get("siguiente_id")
        if not isinstance(siguiente_id, int):
            tipo = type(siguiente_id).__name__
            raise ValueError(
                f"Se esperaba un entero como 'siguiente_id' en {self.ruta}, "
                f"se encontró {tipo}"
            )

        tareas_raw = datos.get("tareas")
        if not isinstance(tareas_raw, list):
            tipo = type(tareas_raw).__name__
            raise ValueError(
                f"Se esperaba una lista como 'tareas' en {self.ruta}, "
                f"se encontró {tipo}"
            )

        siguiente_id = datos["siguiente_id"]
        tareas_raw = datos["tareas"]
        tareas = [self._dict_a_tarea(d) for d in tareas_raw]

        return siguiente_id, tareas

    def guardar(self, siguiente_id: int, tareas: list[Tarea]) -> None:
        """Guarda las tareas en el archivo.

        Args:
            tareas: Lista de tareas a persistir.
        """
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        datos = {
            "siguiente_id": siguiente_id,
            "tareas": [self._tarea_a_dict(t) for t in tareas],
        }
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
