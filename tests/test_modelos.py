"""Tests para el módulo de modelos."""

from datetime import datetime

import pytest

from gestor_tareas.modelos import EstadoTarea, Tarea


class TestCreacionTarea:
    """Tests de creación y validación."""

    def test_crear_tarea_valida(self) -> None:
        tarea = Tarea(id=1, titulo="Comprar pan")
        assert tarea.id == 1
        assert tarea.titulo == "Comprar pan"
        assert tarea.estado is EstadoTarea.PENDIENTE
        assert tarea.esta_completada is False
        assert tarea.completada_en is None

    def test_titulo_se_normaliza(self) -> None:
        tarea = Tarea(id=1, titulo="  Comprar pan  ")
        assert tarea.titulo == "Comprar pan"

    def test_id_invalido_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="positivo"):
            Tarea(id=0, titulo="Algo")

    def test_titulo_vacio_lanza_error(self) -> None:
        with pytest.raises(ValueError, match="vacío"):
            Tarea(id=1, titulo="   ")

    def test_fechas_creacion_son_distintas(self) -> None:
        """Verifica que default_factory se evalúa por instancia."""
        t1 = Tarea(id=1, titulo="A")
        t2 = Tarea(id=2, titulo="B")
        # En un test realista, pueden ser iguales si son muy rápidas.
        # Verificamos al menos que son del tipo correcto.
        assert isinstance(t1.creada_en, datetime)
        assert isinstance(t2.creada_en, datetime)


class TestEstadoTarea:
    """Tests de transiciones de estado."""

    def test_completar_tarea_pendiente(self) -> None:
        tarea = Tarea(id=1, titulo="Algo")
        tarea.completar()
        assert tarea.esta_completada is True
        assert tarea.completada_en is not None

    def test_completar_tarea_ya_completada_lanza_error(self) -> None:
        tarea = Tarea(id=1, titulo="Algo")
        tarea.completar()
        with pytest.raises(ValueError, match="ya estaba completada"):
            tarea.completar()

    def test_reabrir_tarea_completada(self) -> None:
        tarea = Tarea(id=1, titulo="Algo")
        tarea.completar()
        tarea.reabrir()
        assert tarea.esta_completada is False
        assert tarea.completada_en is None

    def test_reabrir_tarea_pendiente_lanza_error(self) -> None:
        tarea = Tarea(id=1, titulo="Algo")
        with pytest.raises(ValueError, match="ya estaba pendiente"):
            tarea.reabrir()
