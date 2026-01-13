#!/usr/bin/env python3
"""Permite votar sobre las propuestas generadas."""

import argparse
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt

console = Console()


def load_proposal(round_num: int) -> dict | None:
    """Carga propuesta de una ronda."""
    filepath = Path(f"proposals/round_{round_num}.json")
    if not filepath.exists():
        return None
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def save_votes(round_num: int, votes: dict):
    """Guarda votos de una ronda."""
    votes_dir = Path("votes")
    votes_dir.mkdir(exist_ok=True)

    filepath = votes_dir / f"round_{round_num}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)

    console.print(f"\n[green]Votos guardados en {filepath}[/green]")


def main():
    parser = argparse.ArgumentParser(description="Votar sobre propuestas")
    parser.add_argument("--round", "-r", type=int, required=True, help="Numero de ronda a votar")
    args = parser.parse_args()

    # Cargar propuesta
    proposal = load_proposal(args.round)
    if not proposal:
        console.print(f"[red]Error: No existe propuesta para ronda {args.round}[/red]")
        console.print("[dim]Primero ejecuta: uv run python decide.py --rounds N[/dim]")
        return

    # Mostrar propuesta
    console.print(f"\n[cyan]Propuestas de Ronda {args.round}[/cyan]")
    console.print(f"[dim]Tipo: {proposal['type']}[/dim]\n")
    console.print(Panel(Markdown(proposal["content"]), title="Propuestas", border_style="blue"))

    # Recoger votos
    console.print("\n[cyan]Votacion[/cyan]")
    console.print("[dim]Ingresa los votos de cada participante[/dim]\n")

    votes = {
        "round": args.round,
        "votes": [],
        "comments": []
    }

    # Cargar participantes para obtener nombres
    data_dir = Path("data")
    participants = []
    if data_dir.exists():
        for filepath in sorted(data_dir.glob("*.json")):
            with open(filepath, encoding="utf-8") as f:
                p = json.load(f)
                participants.append(p.get("nombre", filepath.stem))

    if not participants:
        participants = [f"Participante {i+1}" for i in range(5)]

    console.print("Para cada participante, indica su opcion preferida (numero)")
    console.print("Ingresa 0 para saltar, o 'q' cuando termines\n")

    for nombre in participants:
        try:
            choice = Prompt.ask(f"  {nombre}", default="0")
            if choice.lower() == 'q':
                break

            choice_num = int(choice)
            if choice_num > 0:
                votes["votes"].append({
                    "participant": nombre,
                    "choice": choice_num
                })
        except (ValueError, KeyboardInterrupt):
            break

    # Comentarios adicionales
    console.print("\n[dim]Comentarios adicionales (Enter para omitir):[/dim]")
    comment = Prompt.ask("  Comentario", default="")
    if comment:
        votes["comments"].append(comment)

    # Mostrar resumen
    console.print("\n[cyan]Resumen de votos:[/cyan]")

    vote_counts = {}
    for v in votes["votes"]:
        choice = v["choice"]
        vote_counts[choice] = vote_counts.get(choice, 0) + 1

    if vote_counts:
        for choice, count in sorted(vote_counts.items()):
            console.print(f"  Opcion {choice}: {count} voto(s)")
    else:
        console.print("  [dim]No se registraron votos[/dim]")

    # Guardar
    if votes["votes"]:
        save_votes(args.round, votes)
        console.print(f"\n[dim]Para continuar: uv run python decide.py --continue[/dim]")
    else:
        console.print("\n[yellow]No se guardaron votos (lista vacia)[/yellow]")


if __name__ == "__main__":
    main()
