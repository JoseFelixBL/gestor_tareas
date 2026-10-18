"""Tests para el repositorio de tareas."""

from pathlib import Path

import pytest

from gestor_tareas.almacenamiento import AlmacenTareas
from gestor_tareas.repositorio import RepositorioTareas


@pytest.fixture
def repo(tmp_path: Path) -> RepositorioTareas:
    """Repositorio con almacén en directorio temporal."""
    return RepositorioTareas(AlmacenTareas(tmp_path / "tareas.json"))


class TestAgregar:
    def test_agregar_asigna_id_secuencial(self, repo: RepositorioTareas) -> None:
        t1 = repo.agregar("Primera")
        t2 = repo.agregar("Segunda")
        t3 = repo.agregar("Tercera")
        assert (t1.id, t2.id, t3.id) == (1, 2, 3)

    def test_agregar_persiste(self, repo: RepositorioTareas) -> None:
        repo.agregar("Algo")
        assert len(repo.listar()) == 1

    def test_ids_no_se_reutilizan_tras_eliminar(self, repo: RepositorioTareas) -> None:
        repo.agregar("A")  # id 1
        repo.agregar("B")  # id 2
        repo.eliminar(2)
        t3 = repo.agregar("C")  # debe ser id 3, no 2
        assert t3.id == 3


class TestListar:
    def test_listar_vacio(self, repo: RepositorioTareas) -> None:
        assert repo.listar() == []

    def test_listar_ordenado_por_id(self, repo: RepositorioTareas) -> None:
        repo.agregar("B")
        repo.agregar("A")
        ids = [t.id for t in repo.listar()]
        assert ids == [1, 2]

    def test_listar_solo_pendientes(self, repo: RepositorioTareas) -> None:
        repo.agregar("Pendiente")
        repo.agregar("Completada")
        repo.completar(2)
        pendientes = repo.listar(solo_pendientes=True)
        assert [t.titulo for t in pendientes] == ["Pendiente"]


class TestCompletar:
    def test_completar_cambia_estado(self, repo: RepositorioTareas) -> None:
        repo.agregar("Algo")
        tarea = repo.completar(1)
        assert tarea.esta_completada

    def test_completar_persiste(self, repo: RepositorioTareas) -> None:
        repo.agregar("Algo")
        repo.completar(1)
        assert repo.listar()[0].esta_completada

    def test_completar_inexistente_lanza_keyerror(
        self, repo: RepositorioTareas
    ) -> None:
        with pytest.raises(KeyError, match="id 99"):
            repo.completar(99)


class TestEliminar:
    def test_eliminar_quita_tarea(self, repo: RepositorioTareas) -> None:
        repo.agregar("A")
        repo.agregar("B")
        repo.eliminar(1)
        assert [t.titulo for t in repo.listar()] == ["B"]

    def test_eliminar_inexistente_lanza_keyerror(self, repo: RepositorioTareas) -> None:
        with pytest.raises(KeyError):
            repo.eliminar(99)

    def test_contador_persistente(self, repo: RepositorioTareas) -> None:
        # crear tareas,
        repo.agregar("A")
        repo.agregar("B")
        repo.agregar("C")
        # eliminarlas todas,
        repo.eliminar(1)
        repo.eliminar(2)
        repo.eliminar(3)
        # crear una nueva,
        repo.agregar("D")
        # verificar que el ID continúa.
        tareas = repo.listar()
        assert tareas[0].id == 4


class TestBuscar:
    def test_buscar_sin_texto_devuelve_todas(self, repo: RepositorioTareas) -> None:
        repo.agregar("A")
        repo.agregar("B")
        assert len(repo.buscar("")) == 2

    def test_buscar_por_titulo(self, repo: RepositorioTareas) -> None:
        repo.agregar("Comprar pan")
        repo.agregar("Llamar al médico")
        resultados = repo.buscar("pan")
        assert [t.titulo for t in resultados] == ["Comprar pan"]

    def test_buscar_es_case_insensitive(self, repo: RepositorioTareas) -> None:
        repo.agregar("Comprar PAN")
        assert len(repo.buscar("pan")) == 1

    def test_buscar_por_descripcion(self, repo: RepositorioTareas) -> None:
        repo.agregar("Tarea", descripcion="algo urgente")
        assert len(repo.buscar("urgente")) == 1

    def test_buscar_sin_resultados(self, repo: RepositorioTareas) -> None:
        repo.agregar("A")
        assert repo.buscar("xyz") == []


class TestEditar:
    def test_editar_titulo(self, repo: RepositorioTareas) -> None:
        repo.agregar("Original")
        tarea = repo.editar(1, titulo="Nuevo")
        assert tarea.titulo == "Nuevo"

    def test_editar_descripcion(self, repo: RepositorioTareas) -> None:
        repo.agregar("Tarea")
        tarea = repo.editar(1, descripcion="Detalle")
        assert tarea.descripcion == "Detalle"

    def test_editar_ambos(self, repo: RepositorioTareas) -> None:
        repo.agregar("Original")
        tarea = repo.editar(1, titulo="Nuevo", descripcion="Detalle")
        assert tarea.titulo == "Nuevo"
        assert tarea.descripcion == "Detalle"

    def test_editar_persiste(self, repo: RepositorioTareas) -> None:
        repo.agregar("Original")
        repo.editar(1, titulo="Nuevo")
        assert repo.listar()[0].titulo == "Nuevo"

    def test_editar_sin_cambios_lanza_error(self, repo: RepositorioTareas) -> None:
        repo.agregar("A")
        with pytest.raises(ValueError, match="al menos un campo"):
            repo.editar(1)

    def test_editar_titulo_vacio_lanza_error(self, repo: RepositorioTareas) -> None:
        repo.agregar("A")
        with pytest.raises(ValueError, match="vacío"):
            repo.editar(1, titulo="   ")

    def test_editar_inexistente_lanza_keyerror(self, repo: RepositorioTareas) -> None:
        with pytest.raises(KeyError):
            repo.editar(99, titulo="X")
