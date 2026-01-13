"""Schema para reuniones sociales."""

import random

SCHEMA = {
    "tipo": "reunion",
    "campos": ["nombre", "disponibilidad", "zona", "restricciones_alimentarias", "preferencias_lugar"]
}

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
    [], [], [],
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

FECHAS_BASE = ["2026-01-15", "2026-01-16", "2026-01-17", "2026-01-18", "2026-01-19",
               "2026-01-22", "2026-01-23", "2026-01-24", "2026-01-25", "2026-01-26"]

HORAS = ["12:00-14:00", "13:00-15:00", "18:00-21:00", "19:00-22:00", "20:00-23:00"]


def generate(index: int) -> dict:
    """Genera datos de participante para reunion."""
    nombre = NOMBRES[index % len(NOMBRES)]

    num_fechas = random.randint(2, 5)
    fechas = random.sample(FECHAS_BASE, num_fechas)
    fechas.sort()

    num_horas = random.randint(1, 3)
    horas = random.sample(HORAS, num_horas)

    return {
        "tipo": "reunion",
        "nombre": nombre,
        "disponibilidad": {
            "fechas": fechas,
            "horas": horas
        },
        "zona": random.choice(ZONAS),
        "restricciones_alimentarias": random.choice(RESTRICCIONES),
        "preferencias_lugar": random.choice(PREFERENCIAS_LUGAR)
    }
