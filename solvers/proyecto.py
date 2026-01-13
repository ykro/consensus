"""Solver algoritmico para asignacion de tareas en proyectos."""

from collections import Counter
from .base import BaseSolver, ComplexityScore, SolverResult


# Tareas predefinidas que esperamos asignar
TAREAS_PROYECTO = [
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


class ProyectoSolver(BaseSolver):
    """Resuelve asignacion de tareas en proyectos."""

    def evaluate_complexity(self, participants: list[dict]) -> ComplexityScore:
        """Evalua complejidad basada en cobertura de habilidades y disponibilidad."""
        factors = []
        score = 0.0

        if len(participants) < 2:
            return ComplexityScore(score=0.0, factors=["Menos de 2 participantes"])

        # Habilidades cubiertas
        all_skills = set()
        for p in participants:
            all_skills.update(p.get("habilidades", []))

        # Necesitamos al menos habilidades basicas
        required_skills = {"frontend", "backend", "base de datos"}
        missing = required_skills - all_skills
        if missing:
            score += 0.2
            factors.append(f"Faltan habilidades clave: {', '.join(missing)}")

        # Disponibilidad total
        total_hours = sum(p.get("disponibilidad_horas", 0) for p in participants)
        if total_hours < 40:
            score += 0.25
            factors.append(f"Poca disponibilidad total ({total_hours}h)")
        elif total_hours < 80:
            score += 0.1
            factors.append(f"Disponibilidad moderada ({total_hours}h)")

        # Conflictos de preferencias (muchos evitando las mismas tareas)
        evitar_counter = Counter()
        for p in participants:
            for t in p.get("tareas_evitar", []):
                evitar_counter[t] += 1

        # Si mas del 50% evita una tarea critica
        for tarea, count in evitar_counter.items():
            if count > len(participants) / 2:
                score += 0.15
                factors.append(f"Muchos evitan '{tarea}'")
                break

        # Tareas de interes muy concentradas
        interes_counter = Counter()
        for p in participants:
            for t in p.get("tareas_interes", []):
                interes_counter[t] += 1

        # Si una tarea tiene demasiado interes vs otras
        if interes_counter:
            max_interes = max(interes_counter.values())
            min_interes = min(interes_counter.values())
            if max_interes > 3 * min_interes:
                score += 0.1
                factors.append("Interes muy concentrado en pocas tareas")

        if not factors:
            factors.append("Buena distribucion de habilidades e intereses")

        return ComplexityScore(score=min(score, 1.0), factors=factors)

    def solve(self, participants: list[dict]) -> SolverResult:
        """Resuelve la asignacion de tareas usando matching greedy."""
        if len(participants) < 2:
            return SolverResult(
                success=False,
                explanation="Se necesitan al menos 2 participantes"
            )

        explanations = []
        assignments = {}
        participant_hours = {p["nombre"]: p.get("disponibilidad_horas", 0) for p in participants}
        participant_assigned = {p["nombre"]: 0 for p in participants}

        # Crear indice de habilidades e intereses
        skills_map = {p["nombre"]: set(p.get("habilidades", [])) for p in participants}
        interes_map = {p["nombre"]: set(p.get("tareas_interes", [])) for p in participants}
        evitar_map = {p["nombre"]: set(p.get("tareas_evitar", [])) for p in participants}

        # Mapeo de habilidades a tareas
        skill_to_task = {
            "frontend": ["interfaz de usuario"],
            "backend": ["desarrollo de API", "integracion de servicios"],
            "base de datos": ["base de datos"],
            "devops": ["deployment"],
            "testing": ["testing automatizado"],
            "documentacion": ["documentacion tecnica"],
            "diseno UI/UX": ["interfaz de usuario"],
            "seguridad": ["seguridad"],
            "gestion de proyecto": ["code review"],
        }

        # Tareas a asignar (priorizando las de interes)
        interes_counter = Counter()
        for p in participants:
            for t in p.get("tareas_interes", []):
                interes_counter[t] += 1

        tareas_ordenadas = [t for t, _ in interes_counter.most_common()] + \
                          [t for t in TAREAS_PROYECTO if t not in interes_counter]

        # Asignacion greedy
        for tarea in tareas_ordenadas[:len(participants) + 2]:  # Limitar tareas
            best_candidate = None
            best_score = -1

            for nombre in participant_hours:
                # Skip si ya tiene muchas horas asignadas
                if participant_assigned[nombre] >= participant_hours[nombre]:
                    continue

                # Skip si evita esta tarea
                if tarea in evitar_map.get(nombre, set()):
                    continue

                # Calcular score
                score = 0
                if tarea in interes_map.get(nombre, set()):
                    score += 3

                # Bonus por habilidad relevante
                for skill, tareas in skill_to_task.items():
                    if tarea in tareas and skill in skills_map.get(nombre, set()):
                        score += 2
                        break

                # Penalizar si ya tiene muchas tareas
                current_tasks = sum(1 for t, n in assignments.items() if n == nombre)
                score -= current_tasks * 0.5

                if score > best_score:
                    best_score = score
                    best_candidate = nombre

            if best_candidate:
                assignments[tarea] = best_candidate
                participant_assigned[best_candidate] += 5  # Estimar 5h por tarea

        if not assignments:
            return SolverResult(
                success=False,
                explanation="No se pudieron asignar tareas"
            )

        # Calcular horas por persona
        hours_by_person = Counter()
        for tarea, nombre in assignments.items():
            hours_by_person[nombre] += 5

        # Generar explicaciones
        for nombre in sorted(hours_by_person.keys()):
            tareas_asignadas = [t for t, n in assignments.items() if n == nombre]
            explanations.append(f"{nombre}: {', '.join(tareas_asignadas)} ({hours_by_person[nombre]}h)")

        # Calcular confianza
        assigned_count = len(assignments)
        total_possible = min(len(participants) + 2, len(TAREAS_PROYECTO))
        confidence = assigned_count / total_possible

        decision = {
            "Asignaciones": {tarea: persona for tarea, persona in sorted(assignments.items())},
            "Horas por persona": dict(hours_by_person),
            "Total horas": sum(hours_by_person.values())
        }

        return SolverResult(
            success=True,
            decision=decision,
            confidence=confidence,
            explanation="\n".join(explanations)
        )
