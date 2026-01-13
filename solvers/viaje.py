"""Solver algoritmico para viajes grupales."""

from collections import Counter
from .base import BaseSolver, ComplexityScore, SolverResult


class ViajeSolver(BaseSolver):
    """Resuelve consenso para viajes grupales."""

    def evaluate_complexity(self, participants: list[dict]) -> ComplexityScore:
        """Evalua complejidad basada en overlap de fechas, presupuestos y destinos."""
        factors = []
        score = 0.0

        if len(participants) < 2:
            return ComplexityScore(score=0.0, factors=["Menos de 2 participantes"])

        # Fechas comunes
        all_dates = [set(p.get("fechas_disponibles", [])) for p in participants]
        common_dates = set.intersection(*all_dates) if all_dates else set()

        if len(common_dates) == 0:
            score += 0.3
            factors.append("Sin fechas en comun")
        elif len(common_dates) == 1:
            score += 0.1
            factors.append("Solo 1 fecha en comun")

        # Disparidad de presupuestos
        presupuestos = [p.get("presupuesto_max", 0) for p in participants if p.get("presupuesto_max")]
        if presupuestos:
            min_p, max_p = min(presupuestos), max(presupuestos)
            if min_p > 0 and max_p / min_p > 3:
                score += 0.25
                factors.append(f"Presupuestos muy dispares (Q{min_p} - Q{max_p})")

        # Destinos en comun
        all_destinos = [set(p.get("destinos_interes", [])) for p in participants]
        common_destinos = set.intersection(*all_destinos) if all_destinos else set()

        if len(common_destinos) == 0:
            score += 0.25
            factors.append("Sin destinos en comun")
        elif len(common_destinos) == 1:
            score += 0.05

        # Restricciones
        all_restrictions = set()
        for p in participants:
            all_restrictions.update(p.get("restricciones", []))
        if len(all_restrictions) > 3:
            score += 0.15
            factors.append(f"{len(all_restrictions)} restricciones a considerar")

        if not factors:
            factors.append("Buena alineacion de preferencias")

        return ComplexityScore(score=min(score, 1.0), factors=factors)

    def solve(self, participants: list[dict]) -> SolverResult:
        """Resuelve el consenso para un viaje."""
        if len(participants) < 2:
            return SolverResult(
                success=False,
                explanation="Se necesitan al menos 2 participantes"
            )

        explanations = []

        # Mejor fecha
        date_counter = Counter()
        for p in participants:
            for date in p.get("fechas_disponibles", []):
                date_counter[date] += 1

        if not date_counter:
            return SolverResult(success=False, explanation="No hay fechas disponibles")

        best_date, date_count = date_counter.most_common(1)[0]
        explanations.append(f"{date_count}/{len(participants)} disponibles para {best_date}")

        # Presupuesto (minimo del grupo)
        presupuestos = [p.get("presupuesto_max", float('inf')) for p in participants]
        presupuesto = min(presupuestos) if presupuestos else 0
        explanations.append(f"Presupuesto limitado por participante con Q{presupuesto}")

        # Destino mas votado
        destino_counter = Counter()
        for p in participants:
            for destino in p.get("destinos_interes", []):
                destino_counter[destino] += 1

        if not destino_counter:
            return SolverResult(success=False, explanation="No hay destinos de interes")

        best_destino, destino_count = destino_counter.most_common(1)[0]
        explanations.append(f"Destino mas popular: {best_destino} ({destino_count} votos)")

        # Duracion mas comun
        duracion_counter = Counter(p.get("duracion_preferida", "") for p in participants)
        best_duracion = duracion_counter.most_common(1)[0][0] if duracion_counter else "3-4 dias"
        explanations.append(f"Duracion preferida: {best_duracion}")

        # Actividades mas populares (top 3)
        actividad_counter = Counter()
        for p in participants:
            for act in p.get("actividades", []):
                actividad_counter[act] += 1

        top_actividades = [a for a, _ in actividad_counter.most_common(3)]
        explanations.append(f"Actividades sugeridas: {', '.join(top_actividades)}")

        # Restricciones
        all_restrictions = set()
        for p in participants:
            all_restrictions.update(p.get("restricciones", []))

        # Calcular confianza
        date_ratio = date_count / len(participants)
        destino_ratio = destino_count / len(participants)
        confidence = (date_ratio + destino_ratio) / 2

        decision = {
            "Destino": best_destino,
            "Fecha de inicio": best_date,
            "Duracion": best_duracion,
            "Presupuesto maximo": f"Q{presupuesto}",
            "Actividades": top_actividades,
            "Restricciones a considerar": list(all_restrictions) if all_restrictions else ["ninguna"]
        }

        return SolverResult(
            success=True,
            decision=decision,
            confidence=confidence,
            explanation="\n".join(explanations)
        )
