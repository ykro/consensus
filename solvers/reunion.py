"""Solver algoritmico para reuniones sociales."""

from collections import Counter
from .base import BaseSolver, ComplexityScore, SolverResult


class ReunionSolver(BaseSolver):
    """Resuelve consenso para reuniones sociales."""

    def __init__(self, voting_method: str = "plurality"):
        """
        Args:
            voting_method: "plurality" (default) o "borda"
        """
        self.voting_method = voting_method

    def _borda_count(self, participants: list[dict], field: str, subfield: str = None) -> Counter:
        """Calcula Borda Count para un campo.

        Borda asigna puntos segun posicion en la lista de preferencias:
        - 1ra preferencia = n puntos
        - 2da preferencia = n-1 puntos
        - etc.
        """
        scores = Counter()
        for p in participants:
            if subfield:
                items = p.get(field, {}).get(subfield, [])
            else:
                items = p.get(field, [])

            n = len(items)
            for rank, item in enumerate(items):
                # Primer item = n puntos, segundo = n-1, etc.
                scores[item] += n - rank
        return scores

    def _plurality_count(self, participants: list[dict], field: str, subfield: str = None) -> Counter:
        """Conteo simple de votos (cada mencion = 1 voto)."""
        counter = Counter()
        for p in participants:
            if subfield:
                items = p.get(field, {}).get(subfield, [])
            else:
                items = p.get(field, [])
            for item in items:
                counter[item] += 1
        return counter

    def _count_votes(self, participants: list[dict], field: str, subfield: str = None) -> Counter:
        """Cuenta votos segun el metodo configurado."""
        if self.voting_method == "borda":
            return self._borda_count(participants, field, subfield)
        return self._plurality_count(participants, field, subfield)

    def evaluate_complexity(self, participants: list[dict]) -> ComplexityScore:
        """Evalua complejidad basada en overlap de disponibilidad y diversidad."""
        factors = []
        score = 0.0

        if len(participants) < 2:
            return ComplexityScore(score=0.0, factors=["Menos de 2 participantes"])

        # Fechas comunes
        all_dates = [set(p.get("disponibilidad", {}).get("fechas", [])) for p in participants]
        common_dates = set.intersection(*all_dates) if all_dates else set()

        if len(common_dates) == 0:
            score += 0.35
            factors.append("Sin fechas en comun")
        elif len(common_dates) == 1:
            score += 0.1
            factors.append("Solo 1 fecha en comun")

        # Horas comunes
        all_hours = [set(p.get("disponibilidad", {}).get("horas", [])) for p in participants]
        common_hours = set.intersection(*all_hours) if all_hours else set()

        if len(common_hours) == 0:
            score += 0.25
            factors.append("Sin horas en comun")
        elif len(common_hours) == 1:
            score += 0.1
            factors.append("Solo 1 hora en comun")

        # Diversidad de zonas
        zonas = [p.get("zona", "") for p in participants]
        unique_zonas = len(set(zonas))
        if unique_zonas > 4:
            score += 0.15
            factors.append(f"{unique_zonas} zonas distintas")
        elif unique_zonas > 2:
            score += 0.05

        # Restricciones alimentarias
        all_restrictions = set()
        for p in participants:
            all_restrictions.update(p.get("restricciones_alimentarias", []))
        if len(all_restrictions) > 3:
            score += 0.15
            factors.append(f"{len(all_restrictions)} restricciones alimentarias")
        elif len(all_restrictions) > 1:
            score += 0.05

        # Ajustar por numero de participantes
        if len(participants) > 15:
            score += 0.1
            factors.append(f"{len(participants)} participantes (grupo grande)")

        if not factors:
            factors.append("Problema simple con buen overlap")

        return ComplexityScore(score=min(score, 1.0), factors=factors)

    def solve(self, participants: list[dict]) -> SolverResult:
        """Resuelve el consenso para una reunion."""
        if len(participants) < 2:
            return SolverResult(
                success=False,
                explanation="Se necesitan al menos 2 participantes"
            )

        explanations = []
        method_label = "Borda" if self.voting_method == "borda" else "Pluralidad"
        explanations.append(f"Metodo de votacion: {method_label}")

        # Mejor fecha
        date_scores = self._count_votes(participants, "disponibilidad", "fechas")
        if not date_scores:
            return SolverResult(success=False, explanation="No hay fechas disponibles")

        best_date, date_score = date_scores.most_common(1)[0]
        max_possible = len(participants) if self.voting_method == "plurality" else None
        if self.voting_method == "borda":
            explanations.append(f"Fecha: {best_date} ({date_score} pts Borda)")
        else:
            explanations.append(f"{date_score}/{len(participants)} participantes disponibles en {best_date}")

        # Mejor hora
        hour_scores = self._count_votes(participants, "disponibilidad", "horas")
        if not hour_scores:
            return SolverResult(success=False, explanation="No hay horas disponibles")

        best_hour, hour_score = hour_scores.most_common(1)[0]
        if self.voting_method == "borda":
            explanations.append(f"Hora: {best_hour} ({hour_score} pts Borda)")
        else:
            explanations.append(f"{hour_score}/{len(participants)} participantes disponibles en {best_hour}")

        # Zona mas comun (moda - no aplica Borda porque es single-choice)
        zonas = [p.get("zona", "") for p in participants if p.get("zona")]
        zona_counter = Counter(zonas)
        best_zona = zona_counter.most_common(1)[0][0] if zona_counter else "Sin zona definida"
        zona_count = zona_counter.get(best_zona, 0)
        explanations.append(f"Zona mas conveniente: {best_zona} ({zona_count} personas)")

        # Restricciones alimentarias (union de todas)
        all_restrictions = set()
        for p in participants:
            all_restrictions.update(p.get("restricciones_alimentarias", []))
        if all_restrictions:
            explanations.append(f"Menu debe considerar: {', '.join(all_restrictions)}")

        # Tipo de lugar
        lugar_scores = self._count_votes(participants, "preferencias_lugar")
        if lugar_scores:
            best_lugar, lugar_score = lugar_scores.most_common(1)[0]
            if self.voting_method == "borda":
                explanations.append(f"Tipo de lugar: {best_lugar} ({lugar_score} pts Borda)")
            else:
                explanations.append(f"Tipo mas votado: {best_lugar}")
        else:
            best_lugar = "restaurante"

        # Calcular confianza
        if self.voting_method == "borda":
            # Para Borda, normalizar contra el maximo teorico
            max_dates = sum(len(p.get("disponibilidad", {}).get("fechas", [])) for p in participants)
            max_hours = sum(len(p.get("disponibilidad", {}).get("horas", [])) for p in participants)
            date_ratio = date_score / max_dates if max_dates else 0
            hour_ratio = hour_score / max_hours if max_hours else 0
        else:
            date_ratio = date_score / len(participants)
            hour_ratio = hour_score / len(participants)

        zona_ratio = zona_count / len(participants)
        confidence = (date_ratio + hour_ratio + zona_ratio) / 3

        decision = {
            "Fecha": best_date,
            "Hora": best_hour,
            "Zona": best_zona,
            "Restricciones alimentarias": list(all_restrictions) if all_restrictions else ["ninguna"],
            "Tipo de lugar": best_lugar
        }

        return SolverResult(
            success=True,
            decision=decision,
            confidence=confidence,
            explanation="\n".join(explanations)
        )
