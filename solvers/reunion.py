"""Solver algoritmico para reuniones sociales."""

from collections import Counter
from .base import BaseSolver, ComplexityScore, SolverResult


class ReunionSolver(BaseSolver):
    """Resuelve consenso para reuniones sociales."""

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

        # Mejor fecha (la que mas participantes tienen)
        date_counter = Counter()
        for p in participants:
            for date in p.get("disponibilidad", {}).get("fechas", []):
                date_counter[date] += 1

        if not date_counter:
            return SolverResult(success=False, explanation="No hay fechas disponibles")

        best_date, date_count = date_counter.most_common(1)[0]
        explanations.append(f"{date_count}/{len(participants)} participantes disponibles en {best_date}")

        # Mejor hora (la que mas participantes tienen)
        hour_counter = Counter()
        for p in participants:
            for hour in p.get("disponibilidad", {}).get("horas", []):
                hour_counter[hour] += 1

        if not hour_counter:
            return SolverResult(success=False, explanation="No hay horas disponibles")

        best_hour, hour_count = hour_counter.most_common(1)[0]
        explanations.append(f"{hour_count}/{len(participants)} participantes disponibles en {best_hour}")

        # Zona mas comun (moda)
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

        # Tipo de lugar (interseccion o el mas comun)
        all_prefs = [set(p.get("preferencias_lugar", [])) for p in participants]
        common_prefs = set.intersection(*all_prefs) if all_prefs else set()

        if common_prefs:
            best_lugar = list(common_prefs)[0]
            explanations.append(f"Tipo de lugar en comun: {best_lugar}")
        else:
            lugar_counter = Counter()
            for p in participants:
                for lugar in p.get("preferencias_lugar", []):
                    lugar_counter[lugar] += 1
            best_lugar = lugar_counter.most_common(1)[0][0] if lugar_counter else "restaurante"
            explanations.append(f"Tipo mas votado: {best_lugar}")

        # Calcular confianza
        date_ratio = date_count / len(participants)
        hour_ratio = hour_count / len(participants)
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
