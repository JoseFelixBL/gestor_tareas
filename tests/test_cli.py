"""Tests para el módulo cli."""

import pytest

from gestor_tareas.cli import saludar


def test_saludar_devuelve_saludo_correcto() -> None:
    assert saludar("Ana") == "Hola, Ana"


def test_saludar_elimina_espacios() -> None:
    assert saludar("  Ana  ") == "Hola, Ana"


def test_saludar_con_nombre_vacio_lanza_error() -> None:
    with pytest.raises(ValueError, match="vacío"):
        saludar("")
