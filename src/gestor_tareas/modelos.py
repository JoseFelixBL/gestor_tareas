"""Modelos de datos del gestor de tareas."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EstadoTarea(str, Enum):
    """Estado posible de una tarea."""

    PENDIENTE = "pendiente"
    COMPLETADA = "completada"


@dataclass
class Tarea:
    """Representa una tarea del gestor.

    Attributes:
        id: Identificador único, entero positivo.
        titulo: Título corto, obligatorio, no vacío.
        descripcion: Texto libre opcional.
        estado: Estado actual de la tarea.
        creada_en: Fecha y hora de creación.
        completada_en: Fecha y hora de finalización, o None.
    """

    id: int
    titulo: str
    descripcion: str = ""
    estado: EstadoTarea = EstadoTarea.PENDIENTE
    creada_en: datetime = field(default_factory=datetime.now)
    completada_en: datetime | None = None

    def __post_init__(self) -> None:
        """Valida los datos después de la inicialización."""
        if self.id <= 0:
            raise ValueError(f"El id debe ser positivo, se recibió {self.id}")
        if not self.titulo.strip():
            raise ValueError("El título no puede estar vacío")
        self.titulo = self.titulo.strip()
        self.descripcion = self.descripcion.strip()

    def completar(self) -> None:
        """Marca la tarea como completada."""
        if self.estado is EstadoTarea.COMPLETADA:
            raise ValueError("La tarea ya estaba completada")
        self.estado = EstadoTarea.COMPLETADA
        self.completada_en = datetime.now()

    def reabrir(self) -> None:
        """Reabre una tarea completada."""
        if self.estado is EstadoTarea.PENDIENTE:
            raise ValueError("La tarea ya estaba pendiente")
        self.estado = EstadoTarea.PENDIENTE
        self.completada_en = None

    @property
    def esta_completada(self) -> bool:
        """Indica si la tarea está completada."""
        return self.estado is EstadoTarea.COMPLETADA
