# Consensus

Sistema de consenso grupal usando IA para diferentes tipos de decisiones.

## Tipos de decision soportados

| Tipo | Descripcion | Campos principales |
|------|-------------|-------------------|
| **reunion** | Coordinar reuniones sociales | fecha, hora, zona, restricciones alimentarias |
| **viaje** | Planificar viajes grupales | destino, fechas, presupuesto, actividades |
| **proyecto** | Asignar tareas en proyectos | habilidades, horas, tareas de interes |
| **compra** | Organizar compras grupales | presupuesto, productos, marcas, prioridad |

## Requisitos

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes)
- API Key de Google Gemini

## Instalacion

```bash
cd consensus
uv sync
```

## Configuracion

Crea un archivo `.env` con tu API key:

```bash
GEMINI_API_KEY=tu_api_key_aqui
```

Obtener API key: https://aistudio.google.com/apikey

## Uso basico

### 1. Generar datos de participantes

```bash
# Reunion social (default)
uv run python generate_data.py

# Viaje grupal
uv run python generate_data.py --type viaje

# Asignacion de tareas
uv run python generate_data.py --type proyecto

# Compra grupal
uv run python generate_data.py --type compra

# Especificar cantidad
uv run python generate_data.py --type viaje --count 8

# Limpiar datos anteriores
uv run python generate_data.py --type proyecto --clean
```

### 2. Obtener decision

```bash
# Decision directa
uv run python decide.py

# Usar modelo Pro
uv run python decide.py --pro
```

## Modo iterativo (con votacion)

El modo iterativo permite que Gemini proponga opciones, los participantes voten, y luego refinar la decision.

### Flujo completo:

```bash
# Paso 1: Generar datos
uv run python generate_data.py --type viaje --clean

# Paso 2: Proponer opciones (ej: 3 opciones)
uv run python decide.py --rounds 3

# Paso 3: Votar (interactivo)
uv run python vote.py --round 1

# Paso 4: Refinar con votos
uv run python decide.py --continue
```

### Ejemplo de votacion:

```
$ uv run python vote.py --round 1

Propuestas de Ronda 1
Tipo: viaje

╭────────────────── Propuestas ──────────────────╮
│ OPCION 1: Antigua Guatemala...                 │
│ OPCION 2: Lago de Atitlan...                   │
│ OPCION 3: Semuc Champey...                     │
╰────────────────────────────────────────────────╯

Votacion
Para cada participante, indica su opcion preferida (numero)

  Ana Garcia [0]: 1
  Carlos Lopez [0]: 2
  Maria Rodriguez [0]: 1
  ...

Resumen de votos:
  Opcion 1: 4 voto(s)
  Opcion 2: 3 voto(s)
  Opcion 3: 2 voto(s)

Votos guardados en votes/round_1.json
```

## Estructura de datos por tipo

### Reunion
```json
{
  "tipo": "reunion",
  "nombre": "Ana Garcia",
  "disponibilidad": {
    "fechas": ["2026-01-15", "2026-01-16"],
    "horas": ["18:00-21:00", "19:00-22:00"]
  },
  "zona": "Zona 10 - Zona Viva",
  "restricciones_alimentarias": ["vegetariano"],
  "preferencias_lugar": ["restaurante", "cafe"]
}
```

### Viaje
```json
{
  "tipo": "viaje",
  "nombre": "Ana Garcia",
  "fechas_disponibles": ["2026-02-01", "2026-02-15"],
  "duracion_preferida": "3-4 dias",
  "presupuesto_max": 500,
  "destinos_interes": ["Antigua Guatemala", "Semuc Champey"],
  "actividades": ["senderismo", "cultura"],
  "restricciones": ["no vuelos", "vegetariano"]
}
```

### Proyecto
```json
{
  "tipo": "proyecto",
  "nombre": "Ana Garcia",
  "habilidades": ["frontend", "diseno UI/UX"],
  "disponibilidad_horas": 20,
  "tareas_interes": ["interfaz de usuario", "documentacion"],
  "tareas_evitar": ["backend", "devops"]
}
```

### Compra
```json
{
  "tipo": "compra",
  "nombre": "Ana Garcia",
  "presupuesto_max": 200,
  "productos_interes": ["monitor", "teclado mecanico"],
  "marcas_preferidas": ["Logitech", "Samsung"],
  "prioridad": "calidad"
}
```

## Destinos de Guatemala (para viajes)

- Antigua Guatemala
- Semuc Champey
- Lago de Atitlan
- Tikal
- Rio Dulce
- Monterrico
- Chichicastenango
- Quetzaltenango
- Coban
- Flores

## Zonas de Ciudad de Guatemala (para reuniones)

- Zona 1 - Centro Historico
- Zona 4 - Cuatro Grados Norte
- Zona 10 - Zona Viva
- Zona 14 - Oakland
- Zona 15 - Vista Hermosa
- Zona 16 - Cayala

## Estructura del proyecto

```
consensus/
├── data/                    # Datos de participantes (JSON)
├── proposals/               # Propuestas de cada ronda
├── votes/                   # Votos de cada ronda
├── schemas/                 # Definiciones de tipos de decision
│   ├── reunion.py
│   ├── viaje.py
│   ├── proyecto.py
│   └── compra.py
├── generate_data.py         # Genera datos de ejemplo
├── decide.py                # Obtiene decision de Gemini
├── vote.py                  # Sistema de votacion
└── .env                     # API key (no commitear)
```

## Ejemplo completo: planificar viaje

```bash
# 1. Generar 8 participantes para viaje
$ uv run python generate_data.py --type viaje --count 8 --clean

Tipo: viaje - Viaje grupal (destino, fechas, presupuesto)
Generando 8 participantes...
  + participante_01.json: Ana Garcia (Q1500)
  + participante_02.json: Carlos Lopez (Q750)
  ...
Se generaron 8 archivos en data/

# 2. Proponer 3 opciones de viaje
$ uv run python decide.py --rounds 3

Modelo: gemini-3-flash-preview
Tipo: viaje
Participantes: 8
...

╭──────────────── Propuestas ────────────────╮
│ OPCION 1: Ruta Cultural - Antigua...       │
│ OPCION 2: Aventura - Semuc Champey...      │
│ OPCION 3: Relax - Lago Atitlan...          │
╰────────────────────────────────────────────╯

Propuesta guardada en proposals/round_1.json

# 3. Votar
$ uv run python vote.py --round 1
...

# 4. Decision final basada en votos
$ uv run python decide.py --continue

Continuando desde ronda 1 con votos
...

╭──────────── Decision de Consenso ──────────╮
│ Basado en los votos, el destino elegido    │
│ es Antigua Guatemala...                    │
╰────────────────────────────────────────────╯
```

## Personalizar

### Agregar mas destinos/zonas

Editar los archivos en `schemas/` para agregar opciones.

### Crear tipo de decision personalizado

1. Crear `schemas/mi_tipo.py` con la estructura
2. Agregar al `schemas/__init__.py`
3. Agregar prompts en `decide.py`
