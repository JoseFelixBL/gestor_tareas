"""Punto de entrada del gestor de tareas."""

from __future__ import annotations


def saludar(nombre: str) -> str:
    """Devuelve un saludo personalizado.

    Args:
        nombre: Nombre de la persona a saludar.

    Returns:
        Cadena con el saludo.

    Raises:
        ValueError: Si el nombre está vacío.
    """
    if not nombre.strip():
        raise ValueError("El nombre no puede estar vacío")
    return f"Hola, {nombre.strip()}"
