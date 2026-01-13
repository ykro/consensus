# Consensus

Sistema de consenso para acordar parametros de reuniones sociales usando IA.

## Requisitos

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes)
- API Key de Google Gemini

## Instalacion

```bash
# Clonar o navegar al directorio
cd consensus

# Instalar dependencias
uv sync
```

## Configuracion

Crea un archivo `.env` en el directorio raiz con tu API key:

```bash
GEMINI_API_KEY=tu_api_key_aqui
```

Puedes obtener una API key en: https://aistudio.google.com/apikey

## Uso

### 1. Generar datos de ejemplo

Genera 10 archivos JSON con datos ficticios de participantes:

```bash
uv run python generate_data.py
```

Salida esperada:
```
Generando datos de participantes...
  + participante_01.json: Ana Garcia (Zona 10 - Zona Viva)
  + participante_02.json: Carlos Lopez (Zona 1 - Centro Historico)
  ...
Se generaron 10 archivos en data/
```

### 2. Ejecutar el consenso

Usa Gemini para analizar los datos y decidir:

```bash
# Usar gemini-3-flash-preview (rapido, por defecto)
uv run python decide.py

# Usar gemini-3-pro-preview (mas capacidad)
uv run python decide.py --pro
```

## Estructura de datos

Cada participante tiene el siguiente formato JSON:

```json
{
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

### Zonas disponibles

- Zona 1 - Centro Historico
- Zona 4 - Cuatro Grados Norte
- Zona 10 - Zona Viva
- Zona 14 - Oakland
- Zona 15 - Vista Hermosa
- Zona 16 - Cayala

### Restricciones alimentarias

- vegetariano
- vegano
- sin gluten
- sin lactosa
- kosher
- sin mariscos

## Ejemplo de salida

```
Modelo: gemini-3-flash-preview
Participantes cargados: 10

Participantes:
  - Ana Garcia (Zona 10 - Zona Viva) - Restricciones: vegetariano
  - Carlos Lopez (Zona 1 - Centro Historico) - Restricciones: ninguna
  ...

Consultando a Gemini...

╭─────────────── Decision de Consenso ───────────────╮
│                     DECISION                       │
│                                                    │
│ • Fecha: 25 de enero de 2026                       │
│ • Hora: 19:00 - 21:00                              │
│ • Zona: Zona 10 (Zona Viva)                        │
│ • Tipo de lugar: Restaurante                       │
│ • Consideraciones: Opciones vegetarianas y kosher  │
│                                                    │
│                   JUSTIFICACION                    │
│ ...                                                │
╰────────────────────────────────────────────────────╯
```

## Personalizar datos

Puedes crear tus propios archivos JSON en `data/` siguiendo la estructura indicada, o modificar `generate_data.py` para ajustar los datos generados.
