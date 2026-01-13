"""Schema para compras grupales."""

import random

SCHEMA = {
    "tipo": "compra",
    "campos": ["nombre", "presupuesto_max", "productos_interes", "marcas_preferidas", "prioridad"]
}

NOMBRES = [
    "Ana Garcia", "Carlos Lopez", "Maria Rodriguez", "Jose Martinez",
    "Sofia Hernandez", "Diego Perez", "Lucia Gonzalez", "Fernando Diaz",
    "Valentina Morales", "Andres Castillo"
]

# Productos de oficina/tech
PRODUCTOS = [
    "monitor",
    "teclado mecanico",
    "mouse ergonomico",
    "laptop stand",
    "webcam",
    "audifonos",
    "microfono",
    "hub USB",
    "silla ergonomica",
    "escritorio standing"
]

MARCAS = [
    "Logitech",
    "Apple",
    "Samsung",
    "Dell",
    "HP",
    "Razer",
    "Corsair",
    "Sony",
    "LG",
    "sin preferencia"
]

PRIORIDADES = [
    "precio",
    "calidad",
    "marca",
    "garantia",
    "envio rapido"
]

PRESUPUESTOS = [50, 100, 150, 200, 300, 500]


def generate(index: int) -> dict:
    """Genera datos de participante para compra grupal."""
    nombre = NOMBRES[index % len(NOMBRES)]

    num_productos = random.randint(2, 4)
    productos = random.sample(PRODUCTOS, num_productos)

    num_marcas = random.randint(1, 3)
    marcas = random.sample(MARCAS, num_marcas)

    return {
        "tipo": "compra",
        "nombre": nombre,
        "presupuesto_max": random.choice(PRESUPUESTOS),
        "productos_interes": productos,
        "marcas_preferidas": marcas,
        "prioridad": random.choice(PRIORIDADES)
    }
