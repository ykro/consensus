#!/usr/bin/env python3
"""Usa Gemini para decidir parametros de reunion basado en inputs de participantes."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Cargar variables de entorno desde .env
load_dotenv()

console = Console()

def load_participants(data_dir: Path) -> list[dict]:
    """Carga todos los archivos JSON de participantes."""
    participants = []
    for filepath in sorted(data_dir.glob("*.json")):
        with open(filepath, encoding="utf-8") as f:
            participants.append(json.load(f))
    return participants

def build_prompt(participants: list[dict]) -> str:
    """Construye el prompt para Gemini."""
    participants_json = json.dumps(participants, ensure_ascii=False, indent=2)

    return f"""Eres un asistente que ayuda a coordinar reuniones sociales en Ciudad de Guatemala.

Tienes los datos de {len(participants)} participantes que quieren reunirse. Cada participante tiene:
- Disponibilidad de fechas y horas
- Zona donde vive/trabaja
- Restricciones alimentarias
- Preferencias de tipo de lugar

DATOS DE PARTICIPANTES:
{participants_json}

TAREA:
Analiza la informacion y decide:
1. **Fecha**: La fecha que maximiza la asistencia
2. **Hora**: El rango de hora que funciona para la mayoria
3. **Zona**: La zona mas conveniente considerando donde viven los participantes
4. **Tipo de lugar**: Restaurante, cafe o bar segun preferencias
5. **Consideraciones alimentarias**: Resume las restricciones a considerar

FORMATO DE RESPUESTA:
Responde en espanol con:
- Una seccion de DECISION con los parametros acordados
- Una seccion de JUSTIFICACION explicando por que elegiste cada parametro
- Una seccion de NOTAS con cualquier conflicto o consideracion importante

Se conciso pero informativo."""

def main():
    parser = argparse.ArgumentParser(description="Decide parametros de reunion usando Gemini")
    parser.add_argument("--pro", action="store_true", help="Usar gemini-3-pro-preview en lugar de flash")
    args = parser.parse_args()

    # Verificar API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[red]Error: No se encontro GEMINI_API_KEY[/red]")
        console.print("[dim]Crea un archivo .env con: GEMINI_API_KEY=tu_api_key[/dim]")
        sys.exit(1)

    # Seleccionar modelo
    model_name = "gemini-3-pro-preview" if args.pro else "gemini-3-flash-preview"

    console.print(f"[cyan]Modelo:[/cyan] {model_name}")

    # Cargar participantes
    data_dir = Path("data")
    if not data_dir.exists():
        console.print("[red]Error: No existe el directorio 'data/'[/red]")
        console.print("[dim]Ejecuta primero: python generate_data.py[/dim]")
        return

    participants = load_participants(data_dir)
    if not participants:
        console.print("[red]Error: No hay archivos JSON en 'data/'[/red]")
        return

    console.print(f"[cyan]Participantes cargados:[/cyan] {len(participants)}")

    # Mostrar resumen de participantes
    console.print("\n[dim]Participantes:[/dim]")
    for p in participants:
        restricciones = ", ".join(p["restricciones_alimentarias"]) or "ninguna"
        console.print(f"  - {p['nombre']} ({p['zona']}) - Restricciones: {restricciones}")

    console.print("\n[cyan]Consultando a Gemini...[/cyan]\n")

    # Llamar a Gemini
    client = genai.Client()
    prompt = build_prompt(participants)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    # Mostrar resultado
    console.print(Panel(Markdown(response.text), title="Decision de Consenso", border_style="green"))

if __name__ == "__main__":
    main()
