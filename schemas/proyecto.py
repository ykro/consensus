"""Schema para asignacion de tareas en proyectos."""

import random

SCHEMA = {
    "tipo": "proyecto",
    "campos": ["nombre", "habilidades", "disponibilidad_horas", "tareas_interes", "tareas_evitar"]
}

NOMBRES = [
    "Ana Garcia", "Carlos Lopez", "Maria Rodriguez", "Jose Martinez",
    "Sofia Hernandez", "Diego Perez", "Lucia Gonzalez", "Fernando Diaz",
    "Valentina Morales", "Andres Castillo"
]

HABILIDADES = [
    "frontend",
    "backend",
    "base de datos",
    "devops",
    "diseno UI/UX",
    "testing",
    "documentacion",
    "gestion de proyecto",
    "mobile",
    "machine learning"
]

TAREAS = [
    "desarrollo de API",
    "interfaz de usuario",
    "base de datos",
    "deployment",
    "testing automatizado",
    "documentacion tecnica",
    "integracion de servicios",
    "optimizacion de rendimiento",
    "seguridad",
    "code review"
]

HORAS_DISPONIBLES = [5, 10, 15, 20, 25, 30, 40]


def generate(index: int) -> dict:
    """Genera datos de participante para proyecto."""
    nombre = NOMBRES[index % len(NOMBRES)]

    num_habilidades = random.randint(2, 4)
    habilidades = random.sample(HABILIDADES, num_habilidades)

    num_interes = random.randint(2, 4)
    tareas_interes = random.sample(TAREAS, num_interes)

    # Tareas a evitar (diferentes a las de interes)
    tareas_restantes = [t for t in TAREAS if t not in tareas_interes]
    num_evitar = random.randint(1, 3)
    tareas_evitar = random.sample(tareas_restantes, min(num_evitar, len(tareas_restantes)))

    return {
        "tipo": "proyecto",
        "nombre": nombre,
        "habilidades": habilidades,
        "disponibilidad_horas": random.choice(HORAS_DISPONIBLES),
        "tareas_interes": tareas_interes,
        "tareas_evitar": tareas_evitar
    }
