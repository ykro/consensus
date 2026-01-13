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

# Mapeo de habilidades a tareas
SKILL_TO_TASK = {
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


class ProyectoSolver(BaseSolver):
    """Resuelve asignacion de tareas en proyectos."""

    def __init__(self, matching_method: str = "greedy"):
        """
        Args:
            matching_method: "greedy" (default) o "gale-shapley"
        """
        self.matching_method = matching_method

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

    def _get_participant_preferences(self, participant: dict, all_tasks: list[str]) -> list[str]:
        """Genera lista ordenada de preferencias de tareas para un participante."""
        tareas_evitar = set(participant.get("tareas_evitar", []))
        tareas_interes = participant.get("tareas_interes", [])
        habilidades = set(participant.get("habilidades", []))

        # Calcular score para cada tarea
        task_scores = {}
        for task in all_tasks:
            if task in tareas_evitar:
                continue  # Skip tareas a evitar

            score = 0
            # Bonus por interes
            if task in tareas_interes:
                score += 10 + (len(tareas_interes) - tareas_interes.index(task))

            # Bonus por habilidad relevante
            for skill, tasks in SKILL_TO_TASK.items():
                if task in tasks and skill in habilidades:
                    score += 5
                    break

            task_scores[task] = score

        # Ordenar por score descendente
        return sorted(task_scores.keys(), key=lambda t: task_scores[t], reverse=True)

    def _get_task_preferences(self, task: str, participants: list[dict]) -> list[str]:
        """Genera lista ordenada de preferencias de participantes para una tarea."""
        participant_scores = {}

        for p in participants:
            nombre = p["nombre"]
            if task in p.get("tareas_evitar", []):
                continue  # Skip si evita la tarea

            score = 0
            # Bonus por habilidad relevante
            habilidades = set(p.get("habilidades", []))
            for skill, tasks in SKILL_TO_TASK.items():
                if task in tasks and skill in habilidades:
                    score += 10
                    break

            # Bonus por interes
            if task in p.get("tareas_interes", []):
                score += 5

            # Bonus por disponibilidad
            score += p.get("disponibilidad_horas", 0) / 10

            participant_scores[nombre] = score

        return sorted(participant_scores.keys(), key=lambda n: participant_scores[n], reverse=True)

    def _gale_shapley(self, participants: list[dict], tasks: list[str]) -> dict:
        """
        Implementa Gale-Shapley (Deferred Acceptance) para matching estable.

        En este contexto:
        - Participantes "proponen" a tareas
        - Tareas aceptan/rechazan segun sus preferencias
        - Resultado es un matching estable (nadie quiere intercambiar)
        """
        # Construir preferencias
        participant_prefs = {
            p["nombre"]: self._get_participant_preferences(p, tasks)
            for p in participants
        }
        task_prefs = {
            task: self._get_task_preferences(task, participants)
            for task in tasks
        }

        # Estado inicial
        free_participants = set(p["nombre"] for p in participants)
        task_assignments = {task: None for task in tasks}  # tarea -> participante
        participant_next_proposal = {p["nombre"]: 0 for p in participants}  # indice de siguiente propuesta
        participant_hours = {p["nombre"]: p.get("disponibilidad_horas", 0) for p in participants}
        participant_assigned_hours = {p["nombre"]: 0 for p in participants}

        HOURS_PER_TASK = 5

        while free_participants:
            # Tomar un participante libre
            participant = next(iter(free_participants))

            prefs = participant_prefs.get(participant, [])
            next_idx = participant_next_proposal[participant]

            # Si ya propuso a todas sus preferencias, lo removemos
            if next_idx >= len(prefs):
                free_participants.remove(participant)
                continue

            # Proponer a la siguiente tarea preferida
            task = prefs[next_idx]
            participant_next_proposal[participant] = next_idx + 1

            # Verificar si tiene horas disponibles
            if participant_assigned_hours[participant] + HOURS_PER_TASK > participant_hours[participant]:
                continue

            current_holder = task_assignments[task]

            if current_holder is None:
                # Tarea libre, aceptar
                task_assignments[task] = participant
                participant_assigned_hours[participant] += HOURS_PER_TASK
                # Verificar si puede seguir proponiendo
                if participant_assigned_hours[participant] >= participant_hours[participant]:
                    free_participants.remove(participant)
            else:
                # Comparar con el holder actual
                task_pref_list = task_prefs.get(task, [])
                if participant in task_pref_list and current_holder in task_pref_list:
                    if task_pref_list.index(participant) < task_pref_list.index(current_holder):
                        # Nuevo es mejor, reemplazar
                        task_assignments[task] = participant
                        participant_assigned_hours[current_holder] -= HOURS_PER_TASK
                        participant_assigned_hours[participant] += HOURS_PER_TASK

                        # El holder anterior vuelve a ser libre
                        free_participants.add(current_holder)

                        # Verificar si el nuevo puede seguir
                        if participant_assigned_hours[participant] >= participant_hours[participant]:
                            free_participants.remove(participant)

        # Convertir a formato {tarea: participante}
        return {task: holder for task, holder in task_assignments.items() if holder is not None}

    def _greedy_matching(self, participants: list[dict], tasks: list[str]) -> dict:
        """Matching greedy original."""
        assignments = {}
        participant_hours = {p["nombre"]: p.get("disponibilidad_horas", 0) for p in participants}
        participant_assigned = {p["nombre"]: 0 for p in participants}

        skills_map = {p["nombre"]: set(p.get("habilidades", [])) for p in participants}
        interes_map = {p["nombre"]: set(p.get("tareas_interes", [])) for p in participants}
        evitar_map = {p["nombre"]: set(p.get("tareas_evitar", [])) for p in participants}

        # Ordenar tareas por popularidad
        interes_counter = Counter()
        for p in participants:
            for t in p.get("tareas_interes", []):
                interes_counter[t] += 1

        tareas_ordenadas = [t for t, _ in interes_counter.most_common()] + \
                          [t for t in tasks if t not in interes_counter]

        for tarea in tareas_ordenadas[:len(participants) + 2]:
            best_candidate = None
            best_score = -1

            for nombre in participant_hours:
                if participant_assigned[nombre] >= participant_hours[nombre]:
                    continue
                if tarea in evitar_map.get(nombre, set()):
                    continue

                score = 0
                if tarea in interes_map.get(nombre, set()):
                    score += 3

                for skill, tareas in SKILL_TO_TASK.items():
                    if tarea in tareas and skill in skills_map.get(nombre, set()):
                        score += 2
                        break

                current_tasks = sum(1 for t, n in assignments.items() if n == nombre)
                score -= current_tasks * 0.5

                if score > best_score:
                    best_score = score
                    best_candidate = nombre

            if best_candidate:
                assignments[tarea] = best_candidate
                participant_assigned[best_candidate] += 5

        return assignments

    def solve(self, participants: list[dict]) -> SolverResult:
        """Resuelve la asignacion de tareas."""
        if len(participants) < 2:
            return SolverResult(
                success=False,
                explanation="Se necesitan al menos 2 participantes"
            )

        explanations = []
        method_label = "Gale-Shapley" if self.matching_method == "gale-shapley" else "Greedy"
        explanations.append(f"Metodo de matching: {method_label}")

        # Limitar tareas a asignar
        tasks_to_assign = TAREAS_PROYECTO[:len(participants) + 2]

        # Ejecutar matching segun metodo
        if self.matching_method == "gale-shapley":
            assignments = self._gale_shapley(participants, tasks_to_assign)
            explanations.append("Matching estable (nadie prefiere intercambiar)")
        else:
            assignments = self._greedy_matching(participants, tasks_to_assign)

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
        total_possible = len(tasks_to_assign)
        confidence = assigned_count / total_possible

        decision = {
            "Asignaciones": {tarea: persona for tarea, persona in sorted(assignments.items())},
            "Horas por persona": dict(hours_by_person),
            "Total horas": sum(hours_by_person.values()),
            "Metodo": method_label
        }

        return SolverResult(
            success=True,
            decision=decision,
            confidence=confidence,
            explanation="\n".join(explanations)
        )
