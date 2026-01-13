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

#### Reunion

```
1. FECHA: Contar votos por fecha → elegir la que mas participantes tienen
2. HORA: Contar votos por rango horario → elegir el mas comun
3. ZONA: Calcular moda (zona mas frecuente entre participantes)
4. RESTRICCIONES: Union de todas las restricciones alimentarias
5. TIPO LUGAR: Interseccion de preferencias, o el mas votado si no hay interseccion
6. CONFIANZA: Promedio de (participantes_en_fecha / total, participantes_en_hora / total, participantes_en_zona / total)
```

#### Viaje

```
1. FECHA: Contar disponibilidad por fecha → elegir la mas popular
2. PRESUPUESTO: Minimo de todos los presupuestos (para que todos puedan participar)
3. DESTINO: Contar votos por destino de interes → elegir el mas votado
4. DURACION: Moda de duraciones preferidas
5. ACTIVIDADES: Top 3 actividades mas mencionadas
6. RESTRICCIONES: Union de todas las restricciones
7. CONFIANZA: Promedio de (participantes_en_fecha / total, votos_destino / total)
```

#### Proyecto (Matching Greedy)

```
1. Ordenar tareas por popularidad (mas solicitadas primero)
2. Para cada tarea:
   a. Filtrar candidatos que NO evitan esta tarea
   b. Filtrar candidatos con horas disponibles
   c. Calcular score por candidato:
      - +3 si la tarea esta en sus intereses
      - +2 si tiene habilidad relevante para la tarea
      - -0.5 por cada tarea ya asignada (balancear carga)
   d. Asignar tarea al candidato con mayor score
   e. Restar horas estimadas (5h por tarea)
3. CONFIANZA: tareas_asignadas / tareas_posibles
```

#### Compra

```
1. PRESUPUESTO: Minimo de todos (para que todos puedan participar)
2. PRODUCTOS: Contar votos por producto → top 3 mas votados
3. MARCAS: Contar preferencias (excluyendo "sin preferencia") → top 3
4. PRIORIDAD: Moda del criterio de seleccion (precio, calidad, marca, etc.)
5. CONFIANZA: Promedio de (votos_producto_top / total, votos_prioridad / total)
```

#### Calculo de Complejidad

Cada solver evalua factores que dificultan el consenso (0.0 = trivial, 1.0 = imposible):

```
complejidad = 0.0

# Factores comunes
if sin_fechas_comunes: complejidad += 0.30
if solo_1_fecha_comun: complejidad += 0.10

# Factores especificos por tipo
if presupuestos_difieren_mucho: complejidad += 0.25
if sin_opciones_comunes: complejidad += 0.25
if muchas_restricciones: complejidad += 0.15
if grupo_grande (>15): complejidad += 0.10

# Decision
if complejidad < threshold (0.6):
    usar_algoritmo()
else:
    usar_llm()
```

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
