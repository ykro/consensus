# Consensus

Sistema de consenso grupal hibrido: usa algoritmos deterministas para casos simples y LLM (Gemini) como fallback para casos complejos.

## Tipos de decision soportados

| Tipo | Descripcion | Campos principales |
|------|-------------|-------------------|
| **reunion** | Coordinar reuniones sociales | fecha, hora, zona, restricciones alimentarias |
| **viaje** | Planificar viajes grupales | destino, fechas, presupuesto, actividades |
| **proyecto** | Asignar tareas en proyectos | habilidades, horas, tareas de interes |
| **compra** | Organizar compras grupales | presupuesto, productos, marcas, prioridad |

## Enfoque hibrido: Algoritmo + LLM

El sistema usa un enfoque de dos fases:

```
Participantes → Evaluar Complejidad → Simple? → Solver Algoritmico → Resultado
                                         ↓ No
                                    Gemini (fallback)
```

### Cuando usa algoritmo

- **Complejidad baja** (< 0.6): Fechas en comun, presupuestos similares, preferencias alineadas
- Respuesta instantanea, sin costo de API
- Resultados deterministas y explicables

### Cuando usa LLM

- **Complejidad alta** (>= 0.6): Sin fechas comunes, presupuestos muy dispares, conflictos
- Cuando el algoritmo tiene baja confianza (< 70%)
- Para generar multiples propuestas (`--rounds`)

### Metricas de complejidad por tipo

| Tipo | Factores que aumentan complejidad |
|------|----------------------------------|
| reunion | Sin fechas/horas comunes, muchas zonas distintas, muchas restricciones alimentarias |
| viaje | Sin fechas comunes, presupuestos difieren >3x, sin destinos comunes |
| proyecto | Pocas horas disponibles, habilidades no cubren tareas, conflictos de preferencias |
| compra | Presupuestos difieren >5x, sin productos comunes, prioridades muy diversas |

### Algoritmos utilizados

- **Reunion**: Interseccion de fechas/horas, moda para zona, union de restricciones
- **Viaje**: Fechas mas votadas, presupuesto minimo, destino mas popular
- **Proyecto**: Matching greedy (habilidad + interes + disponibilidad)
- **Compra**: Productos mas votados, presupuesto minimo, prioridad mas comun

## Requisitos

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes)
- API Key de Google Gemini (opcional si usas `--algo-only`)

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
# Decision automatica (algoritmo si es simple, LLM si es complejo)
uv run python decide.py

# Forzar solo algoritmo (sin LLM, sin API key necesaria)
uv run python decide.py --algo-only

# Forzar solo LLM (comportamiento original)
uv run python decide.py --llm-only

# Ver metricas de complejidad
uv run python decide.py --verbose

# Ajustar umbral de complejidad (default: 0.6)
uv run python decide.py --threshold 0.4

# Usar modelo Pro de Gemini
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
├── solvers/                 # Algoritmos de consenso
│   ├── base.py              # Interfaces (SolverResult, ComplexityScore)
│   ├── reunion.py           # Solver para reuniones
│   ├── viaje.py             # Solver para viajes
│   ├── proyecto.py          # Solver para proyectos
│   └── compra.py            # Solver para compras
├── generate_data.py         # Genera datos de ejemplo
├── decide.py                # Decide usando algoritmo o LLM
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
