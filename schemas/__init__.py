"""Esquemas para diferentes tipos de decisiones."""

from .reunion import SCHEMA as REUNION_SCHEMA, generate as generate_reunion
from .viaje import SCHEMA as VIAJE_SCHEMA, generate as generate_viaje
from .proyecto import SCHEMA as PROYECTO_SCHEMA, generate as generate_proyecto
from .compra import SCHEMA as COMPRA_SCHEMA, generate as generate_compra

SCHEMAS = {
    "reunion": {
        "schema": REUNION_SCHEMA,
        "generate": generate_reunion,
        "description": "Reunion social (fecha, hora, lugar, comida)"
    },
    "viaje": {
        "schema": VIAJE_SCHEMA,
        "generate": generate_viaje,
        "description": "Viaje grupal (destino, fechas, presupuesto)"
    },
    "proyecto": {
        "schema": PROYECTO_SCHEMA,
        "generate": generate_proyecto,
        "description": "Asignacion de tareas en proyecto"
    },
    "compra": {
        "schema": COMPRA_SCHEMA,
        "generate": generate_compra,
        "description": "Compra grupal (productos, presupuesto)"
    }
}

def get_schema(name: str):
    if name not in SCHEMAS:
        raise ValueError(f"Tipo desconocido: {name}. Disponibles: {list(SCHEMAS.keys())}")
    return SCHEMAS[name]
