"""Schema para viajes grupales."""

import random

SCHEMA = {
    "tipo": "viaje",
    "campos": ["nombre", "fechas_disponibles", "duracion_preferida", "presupuesto_max",
               "destinos_interes", "actividades", "restricciones"]
}

NOMBRES = [
    "Ana Garcia", "Carlos Lopez", "Maria Rodriguez", "Jose Martinez",
    "Sofia Hernandez", "Diego Perez", "Lucia Gonzalez", "Fernando Diaz",
    "Valentina Morales", "Andres Castillo"
]

# Destinos en Guatemala
DESTINOS = [
    "Antigua Guatemala",
    "Semuc Champey",
    "Lago de Atitlan",
    "Tikal",
    "Rio Dulce",
    "Monterrico",
    "Chichicastenango",
    "Quetzaltenango",
    "Coban",
    "Flores"
]

ACTIVIDADES = [
    "senderismo",
    "cultura",
    "playa",
    "aventura",
    "gastronomia",
    "naturaleza",
    "arqueologia",
    "fotografia",
    "relax",
    "deportes acuaticos"
]

DURACIONES = [
    "1-2 dias",
    "3-4 dias",
    "5-7 dias",
    "1 semana+",
]

RESTRICCIONES_VIAJE = [
    [],
    ["no vuelos"],
    ["vegetariano"],
    ["accesibilidad requerida"],
    ["no caminar mucho"],
    ["no alturas"],
    ["no vuelos", "vegetariano"],
]

FECHAS_VIAJE = [
    "2026-02-01", "2026-02-08", "2026-02-15", "2026-02-22",
    "2026-03-01", "2026-03-08", "2026-03-15", "2026-03-22",
    "2026-04-01", "2026-04-08"
]

PRESUPUESTOS = [300, 500, 750, 1000, 1500, 2000]


def generate(index: int) -> dict:
    """Genera datos de participante para viaje."""
    nombre = NOMBRES[index % len(NOMBRES)]

    num_fechas = random.randint(2, 4)
    fechas = random.sample(FECHAS_VIAJE, num_fechas)
    fechas.sort()

    num_destinos = random.randint(2, 4)
    destinos = random.sample(DESTINOS, num_destinos)

    num_actividades = random.randint(2, 4)
    actividades = random.sample(ACTIVIDADES, num_actividades)

    return {
        "tipo": "viaje",
        "nombre": nombre,
        "fechas_disponibles": fechas,
        "duracion_preferida": random.choice(DURACIONES),
        "presupuesto_max": random.choice(PRESUPUESTOS),
        "destinos_interes": destinos,
        "actividades": actividades,
        "restricciones": random.choice(RESTRICCIONES_VIAJE)
    }
