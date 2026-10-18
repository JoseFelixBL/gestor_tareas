"""Tests de integración del CLI."""

from pathlib import Path

import pytest

from gestor_tareas.cli import main


@pytest.fixture
def archivo(tmp_path: Path) -> Path:
    return tmp_path / "tareas.json"


def test_agregar_y_listar(archivo: Path, capsys: pytest.CaptureFixture) -> None:
    assert main(["--archivo", str(archivo), "agregar", "Comprar pan"]) == 0
    assert main(["--archivo", str(archivo), "listar"]) == 0
    salida = capsys.readouterr().out
    assert "Comprar pan" in salida


def test_completar_y_filtrar(archivo: Path, capsys: pytest.CaptureFixture) -> None:
    main(["--archivo", str(archivo), "agregar", "Comprar pan"])
    main(["--archivo", str(archivo), "agregar", "Llamar al médico"])
    main(["--archivo", str(archivo), "completar", "1"])

    capsys.readouterr()  # Descartar salida de los comandos anteriores

    main(["--archivo", str(archivo), "listar", "--pendientes"])
    salida = capsys.readouterr().out
    assert "Llamar al médico" in salida
    assert "Comprar pan" not in salida


def test_completar_inexistente_devuelve_1(
    archivo: Path, capsys: pytest.CaptureFixture
) -> None:
    codigo = main(["--archivo", str(archivo), "completar", "99"])
    assert codigo == 1
    assert "Error" in capsys.readouterr().err


def test_buscar(archivo: Path, capsys: pytest.CaptureFixture) -> None:
    main(["--archivo", str(archivo), "agregar", "Comprar pan"])
    main(["--archivo", str(archivo), "agregar", "Llamar al médico"])
    main(
        ["--archivo", str(archivo), "agregar", "Ir al mercado", "-d", "Comprar comida"]
    )
    capsys.readouterr()

    main(["--archivo", str(archivo), "buscar", "comprar"])
    salida = capsys.readouterr().out
    assert "Comprar pan" in salida
    assert "Comprar comida" in salida
    assert "Llamar al médico" not in salida
