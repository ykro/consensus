#!/usr/bin/env python3
"""Genera 10 archivos JSON con datos de participantes para reunion."""

import json
import os
import random
from pathlib import Path
from rich.console import Console

console = Console()

# Datos para generar participantes realistas
NOMBRES = [
    "Ana Garcia", "Carlos Lopez", "Maria Rodriguez", "Jose Martinez",
    "Sofia Hernandez", "Diego Perez", "Lucia Gonzalez", "Fernando Diaz",
    "Valentina Morales", "Andres Castillo"
]

ZONAS = [
    "Zona 1 - Centro Historico",
    "Zona 4 - Cuatro Grados Norte",
    "Zona 10 - Zona Viva",
    "Zona 14 - Oakland",
    "Zona 15 - Vista Hermosa",
    "Zona 16 - Cayala"
]

RESTRICCIONES = [
    [], [], [],  # mayoría sin restricciones
    ["vegetariano"],
    ["vegano"],
    ["sin gluten"],
    ["sin lactosa"],
    ["kosher"],
    ["sin mariscos"],
    ["vegetariano", "sin gluten"]
]

PREFERENCIAS_LUGAR = [
    ["restaurante"],
    ["cafe"],
    ["bar"],
    ["restaurante", "cafe"],
    ["restaurante", "bar"],
    ["cafe", "bar"],
    ["restaurante", "cafe", "bar"]
]

# Fechas posibles (proximas 2 semanas)
FECHAS_BASE = ["2026-01-15", "2026-01-16", "2026-01-17", "2026-01-18", "2026-01-19",
               "2026-01-22", "2026-01-23", "2026-01-24", "2026-01-25", "2026-01-26"]

HORAS = [
    "12:00-14:00", "13:00-15:00",  # almuerzo
    "18:00-21:00", "19:00-22:00", "20:00-23:00"  # cena
]

def generate_participant(nombre: str) -> dict:
    """Genera datos aleatorios para un participante."""
    # Seleccionar 2-5 fechas disponibles
    num_fechas = random.randint(2, 5)
    fechas = random.sample(FECHAS_BASE, num_fechas)
    fechas.sort()

    # Seleccionar 1-3 rangos de hora
    num_horas = random.randint(1, 3)
    horas = random.sample(HORAS, num_horas)

    return {
        "nombre": nombre,
        "disponibilidad": {
            "fechas": fechas,
            "horas": horas
        },
        "zona": random.choice(ZONAS),
        "restricciones_alimentarias": random.choice(RESTRICCIONES),
        "preferencias_lugar": random.choice(PREFERENCIAS_LUGAR)
    }

def main():
    # Crear directorio data si no existe
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    console.print("[cyan]Generando datos de participantes...[/cyan]")

    for i, nombre in enumerate(NOMBRES, 1):
        participante = generate_participant(nombre)

        # Nombre de archivo basado en nombre
        filename = f"participante_{i:02d}.json"
        filepath = data_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(participante, f, ensure_ascii=False, indent=2)

        console.print(f"  [green]+[/green] {filename}: {nombre} ({participante['zona']})")

    console.print(f"\n[green]Se generaron {len(NOMBRES)} archivos en {data_dir}/[/green]")

if __name__ == "__main__":
    main()
