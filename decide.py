#!/usr/bin/env python3
"""Usa Gemini para decidir parametros basado en inputs de participantes."""

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

load_dotenv()

console = Console()

PROMPTS = {
    "reunion": """Eres un asistente que ayuda a coordinar reuniones sociales en Ciudad de Guatemala.

Tienes los datos de {count} participantes. Cada participante tiene:
- Disponibilidad de fechas y horas
- Zona donde vive/trabaja
- Restricciones alimentarias
- Preferencias de tipo de lugar

DATOS DE PARTICIPANTES:
{data}

{extra_context}

TAREA:
{task}

FORMATO DE RESPUESTA:
Responde en espanol con formato estructurado.""",

    "viaje": """Eres un asistente que ayuda a planificar viajes grupales en Guatemala.

Tienes los datos de {count} participantes. Cada participante tiene:
- Fechas disponibles
- Duracion preferida
- Presupuesto maximo
- Destinos de interes
- Actividades preferidas
- Restricciones

DATOS DE PARTICIPANTES:
{data}

{extra_context}

TAREA:
{task}

FORMATO DE RESPUESTA:
Responde en espanol con formato estructurado.""",

    "proyecto": """Eres un asistente que ayuda a asignar tareas en proyectos de software.

Tienes los datos de {count} participantes. Cada participante tiene:
- Habilidades
- Disponibilidad en horas
- Tareas de interes
- Tareas a evitar

DATOS DE PARTICIPANTES:
{data}

{extra_context}

TAREA:
{task}

FORMATO DE RESPUESTA:
Responde en espanol con formato estructurado.""",

    "compra": """Eres un asistente que ayuda a organizar compras grupales.

Tienes los datos de {count} participantes. Cada participante tiene:
- Presupuesto maximo
- Productos de interes
- Marcas preferidas
- Prioridad (precio, calidad, etc.)

DATOS DE PARTICIPANTES:
{data}

{extra_context}

TAREA:
{task}

FORMATO DE RESPUESTA:
Responde en espanol con formato estructurado."""
}

TASKS = {
    "reunion": {
        "decide": """Analiza y decide:
1. Fecha que maximiza asistencia
2. Rango de hora optimo
3. Zona mas conveniente
4. Tipo de lugar
5. Consideraciones alimentarias

Incluye DECISION, JUSTIFICACION y NOTAS.""",
        "propose": """Propone {num_options} opciones diferentes para la reunion.
Para cada opcion incluye: fecha, hora, zona, tipo de lugar.
Explica pros y contras de cada opcion.
Formatea como OPCION 1, OPCION 2, etc."""
    },
    "viaje": {
        "decide": """Analiza y decide:
1. Destino optimo
2. Fechas del viaje
3. Duracion
4. Presupuesto grupal
5. Actividades principales

Incluye DECISION, JUSTIFICACION y NOTAS.""",
        "propose": """Propone {num_options} opciones diferentes de viaje.
Para cada opcion incluye: destino, fechas, duracion, presupuesto estimado, actividades.
Explica pros y contras de cada opcion.
Formatea como OPCION 1, OPCION 2, etc."""
    },
    "proyecto": {
        "decide": """Analiza y asigna tareas:
1. Lista de tareas identificadas
2. Asignacion de cada tarea a un participante
3. Horas estimadas por persona
4. Dependencias entre tareas

Incluye ASIGNACION, JUSTIFICACION y NOTAS.""",
        "propose": """Propone {num_options} formas diferentes de organizar el proyecto.
Para cada opcion incluye: distribucion de tareas, timeline sugerido.
Explica pros y contras de cada organizacion.
Formatea como OPCION 1, OPCION 2, etc."""
    },
    "compra": {
        "decide": """Analiza y decide:
1. Productos prioritarios a comprar
2. Marcas/modelos recomendados
3. Presupuesto total
4. Distribucion de costos

Incluye DECISION, JUSTIFICACION y NOTAS.""",
        "propose": """Propone {num_options} opciones diferentes de compra.
Para cada opcion incluye: productos, marcas, costo total, distribucion.
Explica pros y contras de cada opcion.
Formatea como OPCION 1, OPCION 2, etc."""
    }
}


def load_participants(data_dir: Path) -> list[dict]:
    """Carga todos los archivos JSON de participantes."""
    participants = []
    for filepath in sorted(data_dir.glob("*.json")):
        with open(filepath, encoding="utf-8") as f:
            participants.append(json.load(f))
    return participants


def detect_type(participants: list[dict]) -> str:
    """Detecta el tipo de decision basado en los datos."""
    if not participants:
        return "reunion"
    first = participants[0]
    return first.get("tipo", "reunion")


def load_votes(round_num: int) -> dict | None:
    """Carga votos de una ronda si existen."""
    votes_file = Path(f"votes/round_{round_num}.json")
    if votes_file.exists():
        with open(votes_file, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_proposal(round_num: int, response: str, decision_type: str):
    """Guarda propuesta de una ronda."""
    proposals_dir = Path("proposals")
    proposals_dir.mkdir(exist_ok=True)

    proposal = {
        "round": round_num,
        "type": decision_type,
        "content": response
    }

    filepath = proposals_dir / f"round_{round_num}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(proposal, f, ensure_ascii=False, indent=2)

    console.print(f"[dim]Propuesta guardada en {filepath}[/dim]")


def get_current_round() -> int:
    """Determina la ronda actual basado en propuestas existentes."""
    proposals_dir = Path("proposals")
    if not proposals_dir.exists():
        return 1

    existing = list(proposals_dir.glob("round_*.json"))
    if not existing:
        return 1

    rounds = [int(f.stem.split("_")[1]) for f in existing]
    return max(rounds) + 1


def main():
    parser = argparse.ArgumentParser(description="Decide parametros usando Gemini")
    parser.add_argument("--pro", action="store_true", help="Usar gemini-3-pro-preview")
    parser.add_argument("--rounds", "-r", type=int, help="Numero de opciones a proponer (modo iterativo)")
    parser.add_argument("--continue", "-c", dest="continue_round", action="store_true",
                        help="Continuar desde la ultima ronda")
    args = parser.parse_args()

    # Verificar API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        console.print("[red]Error: No se encontro GEMINI_API_KEY[/red]")
        console.print("[dim]Crea un archivo .env con: GEMINI_API_KEY=tu_api_key[/dim]")
        sys.exit(1)

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

    decision_type = detect_type(participants)
    console.print(f"[cyan]Tipo:[/cyan] {decision_type}")
    console.print(f"[cyan]Participantes:[/cyan] {len(participants)}")

    # Mostrar resumen
    console.print("\n[dim]Participantes:[/dim]")
    for p in participants:
        nombre = p.get("nombre", "Anonimo")
        if decision_type == "reunion":
            extra = p.get("zona", "")
        elif decision_type == "viaje":
            extra = f"Q{p.get('presupuesto_max', 0)}"
        elif decision_type == "proyecto":
            extra = f"{p.get('disponibilidad_horas', 0)}h"
        elif decision_type == "compra":
            extra = f"Q{p.get('presupuesto_max', 0)}"
        else:
            extra = ""
        console.print(f"  - {nombre} ({extra})")

    # Construir prompt
    data_json = json.dumps(participants, ensure_ascii=False, indent=2)
    extra_context = ""

    # Modo iterativo: continuar con votos
    if args.continue_round:
        current_round = get_current_round()
        prev_round = current_round - 1
        votes = load_votes(prev_round)

        if votes:
            extra_context = f"""
VOTOS DE LA RONDA ANTERIOR:
{json.dumps(votes, ensure_ascii=False, indent=2)}

Considera estos votos para refinar tu decision."""
            console.print(f"[cyan]Continuando desde ronda {prev_round} con votos[/cyan]")

    # Determinar tarea
    if args.rounds:
        task = TASKS[decision_type]["propose"].format(num_options=args.rounds)
        current_round = get_current_round()
        console.print(f"[cyan]Ronda {current_round}: Proponiendo {args.rounds} opciones[/cyan]")
    else:
        task = TASKS[decision_type]["decide"]

    prompt_template = PROMPTS[decision_type]
    prompt = prompt_template.format(
        count=len(participants),
        data=data_json,
        extra_context=extra_context,
        task=task
    )

    console.print("\n[cyan]Consultando a Gemini...[/cyan]\n")

    # Llamar a Gemini
    client = genai.Client()
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    # Mostrar resultado
    title = "Propuestas" if args.rounds else "Decision de Consenso"
    console.print(Panel(Markdown(response.text), title=title, border_style="green"))

    # Guardar propuesta si es modo iterativo
    if args.rounds:
        current_round = get_current_round()
        save_proposal(current_round, response.text, decision_type)
        console.print(f"\n[dim]Para votar: uv run python vote.py --round {current_round}[/dim]")


if __name__ == "__main__":
    main()
