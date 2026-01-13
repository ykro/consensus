#!/usr/bin/env python3
"""Genera archivos JSON con datos de participantes segun el tipo de decision."""

import argparse
import json
import shutil
from pathlib import Path
from rich.console import Console

from schemas import SCHEMAS, get_schema

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Genera datos de participantes")
    parser.add_argument(
        "--type", "-t",
        choices=list(SCHEMAS.keys()),
        default="reunion",
        help="Tipo de decision (default: reunion)"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=10,
        help="Numero de participantes (default: 10)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Limpiar directorio data antes de generar"
    )
    args = parser.parse_args()

    schema_info = get_schema(args.type)
    generate_func = schema_info["generate"]

    # Crear/limpiar directorio data
    data_dir = Path("data")
    if args.clean and data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(exist_ok=True)

    console.print(f"[cyan]Tipo:[/cyan] {args.type} - {schema_info['description']}")
    console.print(f"[cyan]Generando {args.count} participantes...[/cyan]")

    for i in range(args.count):
        participante = generate_func(i)

        filename = f"participante_{i+1:02d}.json"
        filepath = data_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(participante, f, ensure_ascii=False, indent=2)

        # Mostrar info relevante segun tipo
        nombre = participante.get("nombre", f"Participante {i+1}")
        if args.type == "reunion":
            extra = participante.get("zona", "")
        elif args.type == "viaje":
            extra = f"Q{participante.get('presupuesto_max', 0)}"
        elif args.type == "proyecto":
            extra = f"{participante.get('disponibilidad_horas', 0)}h"
        elif args.type == "compra":
            extra = f"Q{participante.get('presupuesto_max', 0)}"
        else:
            extra = ""

        console.print(f"  [green]+[/green] {filename}: {nombre} ({extra})")

    console.print(f"\n[green]Se generaron {args.count} archivos en {data_dir}/[/green]")


if __name__ == "__main__":
    main()
