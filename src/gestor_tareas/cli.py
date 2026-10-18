"""Punto de entrada del gestor de tareas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gestor_tareas.almacenamiento import AlmacenTareas
from gestor_tareas.modelos import Tarea
from gestor_tareas.repositorio import RepositorioTareas


def ruta_por_defecto() -> Path:
    """Ruta por defecto del archivo de tareas."""
    return Path.home() / ".gestor_tareas" / "tareas.json"


def construir_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos del CLI.

    Returns:
        Parser configurado con todos los subcomandos.
    """
    parser = argparse.ArgumentParser(
        prog="gestor-tareas",
        description="Gestor de tareas simple en línea de comandos.",
    )
    parser.add_argument(
        "--archivo",
        type=Path,
        default=ruta_por_defecto(),
        help="Ruta al archivo de tareas (por defecto: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="comando", required=True)

    # subcomando: agregar
    p_add = subparsers.add_parser("agregar", help="Agrega una nueva tarea")
    p_add.add_argument("titulo", help="Título de la tarea")
    p_add.add_argument("-d", "--descripcion", default="", help="Descripción opcional")
    p_add.set_defaults(func=cmd_agregar)

    # subcomando: listar
    p_list = subparsers.add_parser("listar", help="Lista las tareas")
    p_list.add_argument(
        "-p",
        "--pendientes",
        action="store_true",
        help="Muestra solo las tareas pendientes",
    )
    p_list.set_defaults(func=cmd_listar)

    # subcomando: completar
    p_done = subparsers.add_parser("completar", help="Marca una tarea como completada")
    p_done.add_argument("id", type=int, help="ID de la tarea")
    p_done.set_defaults(func=cmd_completar)

    # subcomando: reabrir
    p_reopen = subparsers.add_parser("reabrir", help="Reabre una tarea completada")
    p_reopen.add_argument("id", type=int, help="ID de la tarea")
    p_reopen.set_defaults(func=cmd_reabrir)

    # subcomando: eliminar
    p_del = subparsers.add_parser("eliminar", help="Elimina una tarea")
    p_del.add_argument("id", type=int, help="ID de la tarea")
    p_del.set_defaults(func=cmd_eliminar)

    # subcomando: buscar
    p_done = subparsers.add_parser("buscar", help="Buscar tareas que contengan texto")
    p_done.add_argument("texto", type=str, help="Texto a buscar")
    p_done.set_defaults(func=cmd_buscar)

    return parser


def _formatear_tarea(tarea: Tarea) -> str:
    """Devuelve una representación legible de una tarea."""
    marca = "✓" if tarea.esta_completada else " "
    return f"[{marca}] {tarea.id:3d}  {tarea.titulo}"


def _formatear_tarea_con_descripcion(tarea: Tarea) -> str:
    """Devuelve la representación de la tarea con la descripción"""
    return _formatear_tarea(tarea) + " - " + tarea.descripcion


def cmd_agregar(args: argparse.Namespace, repo: RepositorioTareas) -> int:
    tarea = repo.agregar(args.titulo, args.descripcion)
    print(f"Tarea creada con id {tarea.id}: {tarea.titulo}")
    return 0


def cmd_listar(args: argparse.Namespace, repo: RepositorioTareas) -> int:
    tareas = repo.listar(solo_pendientes=args.pendientes)
    if not tareas:
        print("No hay tareas.")
        return 0
    for tarea in tareas:
        print(_formatear_tarea(tarea))
    return 0


def cmd_completar(args: argparse.Namespace, repo: RepositorioTareas) -> int:
    tarea = repo.completar(args.id)
    print(f"Tarea {tarea.id} completada: {tarea.titulo}")
    return 0


def cmd_reabrir(args: argparse.Namespace, repo: RepositorioTareas) -> int:
    tarea = repo.reabrir(args.id)
    print(f"Tarea {tarea.id} reabierta: {tarea.titulo}")
    return 0


def cmd_eliminar(args: argparse.Namespace, repo: RepositorioTareas) -> int:
    repo.eliminar(args.id)
    print(f"Tarea {args.id} eliminada.")
    return 0


def cmd_buscar(args: argparse.Namespace, repo: RepositorioTareas) -> int:
    tareas = repo.buscar(args.texto)
    if not tareas:
        print(f"No hay tareas con '{args.texto}'.")
        return 0
    for tarea in tareas:
        print(_formatear_tarea_con_descripcion(tarea))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada del CLI.

    Args:
        argv: Argumentos de línea de comandos. None usa sys.argv.

    Returns:
        Código de salida (0 = éxito, 1 = error controlado).
    """
    parser = construir_parser()
    args = parser.parse_args(argv)

    repo = RepositorioTareas(AlmacenTareas(args.archivo))

    try:
        return args.func(args, repo)
    except (KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
