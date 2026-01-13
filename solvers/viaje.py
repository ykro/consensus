"""Solver algoritmico para viajes grupales."""

from collections import Counter
from statistics import median
from .base import BaseSolver, ComplexityScore, SolverResult


class ViajeSolver(BaseSolver):
    """Resuelve consenso para viajes grupales."""

    def __init__(self, voting_method: str = "plurality", budget_method: str = "minimum"):
        """
        Args:
            voting_method: "plurality" (default) o "borda"
            budget_method: "minimum" (default) o "median"
        """
        self.voting_method = voting_method
        self.budget_method = budget_method

    def _borda_count(self, participants: list[dict], field: str) -> Counter:
        """Calcula Borda Count para un campo de lista."""
        scores = Counter()
        for p in participants:
            items = p.get(field, [])
            n = len(items)
            for rank, item in enumerate(items):
                scores[item] += n - rank
        return scores

    def _plurality_count(self, participants: list[dict], field: str) -> Counter:
        """Conteo simple de votos."""
        counter = Counter()
        for p in participants:
            for item in p.get(field, []):
                counter[item] += 1
        return counter

    def _count_votes(self, participants: list[dict], field: str) -> Counter:
        """Cuenta votos segun el metodo configurado."""
        if self.voting_method == "borda":
            return self._borda_count(participants, field)
        return self._plurality_count(participants, field)

    def _calculate_budget(self, participants: list[dict]) -> tuple[int, str]:
        """Calcula el presupuesto segun el metodo configurado."""
        presupuestos = [p.get("presupuesto_max", 0) for p in participants if p.get("presupuesto_max")]
        if not presupuestos:
            return 0, "No hay presupuestos"

        if self.budget_method == "median":
            budget = int(median(presupuestos))
            explanation = f"Presupuesto (mediana): Q{budget}"
        else:
            budget = min(presupuestos)
            explanation = f"Presupuesto (minimo): Q{budget}"

        return budget, explanation

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
        method_label = "Borda" if self.voting_method == "borda" else "Pluralidad"
        budget_label = "Mediana" if self.budget_method == "median" else "Minimo"
        explanations.append(f"Metodo: votacion={method_label}, presupuesto={budget_label}")

        # Mejor fecha
        date_scores = self._count_votes(participants, "fechas_disponibles")
        if not date_scores:
            return SolverResult(success=False, explanation="No hay fechas disponibles")

        best_date, date_score = date_scores.most_common(1)[0]
        if self.voting_method == "borda":
            explanations.append(f"Fecha: {best_date} ({date_score} pts Borda)")
        else:
            explanations.append(f"{date_score}/{len(participants)} disponibles para {best_date}")

        # Presupuesto
        presupuesto, budget_explanation = self._calculate_budget(participants)
        explanations.append(budget_explanation)

        # Destino mas votado
        destino_scores = self._count_votes(participants, "destinos_interes")
        if not destino_scores:
            return SolverResult(success=False, explanation="No hay destinos de interes")

        best_destino, destino_score = destino_scores.most_common(1)[0]
        if self.voting_method == "borda":
            explanations.append(f"Destino: {best_destino} ({destino_score} pts Borda)")
        else:
            explanations.append(f"Destino mas popular: {best_destino} ({destino_score} votos)")

        # Duracion mas comun
        duracion_counter = Counter(p.get("duracion_preferida", "") for p in participants)
        best_duracion = duracion_counter.most_common(1)[0][0] if duracion_counter else "3-4 dias"
        explanations.append(f"Duracion preferida: {best_duracion}")

        # Actividades mas populares (top 3)
        actividad_scores = self._count_votes(participants, "actividades")
        top_actividades = [a for a, _ in actividad_scores.most_common(3)]
        explanations.append(f"Actividades sugeridas: {', '.join(top_actividades)}")

        # Restricciones
        all_restrictions = set()
        for p in participants:
            all_restrictions.update(p.get("restricciones", []))

        # Calcular confianza
        if self.voting_method == "borda":
            max_dates = sum(len(p.get("fechas_disponibles", [])) for p in participants)
            max_destinos = sum(len(p.get("destinos_interes", [])) for p in participants)
            date_ratio = date_score / max_dates if max_dates else 0
            destino_ratio = destino_score / max_destinos if max_destinos else 0
        else:
            date_ratio = date_score / len(participants)
            destino_ratio = destino_score / len(participants)

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
