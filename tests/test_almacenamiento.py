"""Tests para el módulo de persistencia."""

from pathlib import Path

import pytest

from gestor_tareas.almacenamiento import AlmacenTareas
from gestor_tareas.modelos import Tarea


@pytest.fixture
def ruta_temporal(tmp_path: Path) -> Path:
    """Devuelve una ruta a un archivo JSON en un directorio temporal."""
    return tmp_path / "tareas.json"


@pytest.fixture
def almacen(ruta_temporal: Path) -> AlmacenTareas:
    """Almacén apuntando a una ruta temporal."""
    return AlmacenTareas(ruta_temporal)


class TestCargar:
    """Tests de carga desde disco."""

    def test_archivo_inexistente_devuelve_estado_inicial(
        self, almacen: AlmacenTareas
    ) -> None:
        siguiente_id, tareas = almacen.cargar()
        assert siguiente_id == 1
        assert tareas == []

    def test_cargar_tareas_guardadas(
        self, almacen: AlmacenTareas, ruta_temporal: Path
    ) -> None:
        tareas = [Tarea(id=1, titulo="A"), Tarea(id=2, titulo="B")]
        siguiente_id = 3
        almacen.guardar(siguiente_id, tareas)

        _, recuperadas = almacen.cargar()
        assert len(recuperadas) == 2
        assert recuperadas[0].titulo == "A"
        assert recuperadas[1].titulo == "B"

    def test_archivo_corrupto_lanza_error(
        self, almacen: AlmacenTareas, ruta_temporal: Path
    ) -> None:
        ruta_temporal.write_text("esto no es json", encoding="utf-8")
        with pytest.raises(ValueError, match="JSON válido"):
            almacen.cargar()

    def test_json_no_entero_lanza_error(
        self, almacen: AlmacenTareas, ruta_temporal: Path
    ) -> None:
        ruta_temporal.write_text(
            '{"siguiente_id": "1", "tareas": "no es lista"}', encoding="utf-8"
        )
        with pytest.raises(ValueError, match="entero"):
            almacen.cargar()

    def test_json_no_lista_lanza_error(
        self, almacen: AlmacenTareas, ruta_temporal: Path
    ) -> None:
        ruta_temporal.write_text(
            '{"siguiente_id": 2, "tareas": "no es lista"}', encoding="utf-8"
        )
        with pytest.raises(ValueError, match="lista"):
            almacen.cargar()

    def test_json_sin_siguiente_id(
        self, almacen: AlmacenTareas, ruta_temporal: Path
    ) -> None:
        ruta_temporal.write_text(
            '{"tareas": [{"id": 1, "titulo": "A"}]}', encoding="utf-8"
        )
        with pytest.raises(ValueError, match="siguiente_id"):
            almacen.cargar()


class TestGuardar:
    """Tests de escritura a disco."""

    def test_guardar_crea_archivo(
        self, almacen: AlmacenTareas, ruta_temporal: Path
    ) -> None:
        assert not ruta_temporal.exists()
        siguiente_id = 2
        almacen.guardar(siguiente_id, [Tarea(id=1, titulo="A")])
        assert ruta_temporal.exists()

    def test_roundtrip_preserva_datos(self, almacen: AlmacenTareas) -> None:
        original = Tarea(id=5, titulo="Test", descripcion="detalle")
        siguiente_id = 6
        almacen.guardar(siguiente_id, [original])

        recuperado_id, recuperadas_tareas = almacen.cargar()
        assert recuperado_id == siguiente_id
        recuperada = recuperadas_tareas[0]
        assert recuperada.id == original.id
        assert recuperada.titulo == original.titulo
        assert recuperada.descripcion == original.descripcion
        assert recuperada.estado is original.estado

    def test_roundtrip_tarea_completada(self, almacen: AlmacenTareas) -> None:
        tarea = Tarea(id=1, titulo="A")
        tarea.completar()
        siguiente_id = 2
        almacen.guardar(siguiente_id, [tarea])

        _, recuperadas_tareas = almacen.cargar()
        recuperada = recuperadas_tareas[0]
        assert recuperada.esta_completada is True
        assert recuperada.completada_en is not None
