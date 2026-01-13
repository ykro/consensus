"""Solver algoritmico para compras grupales."""

from collections import Counter
from statistics import median
from .base import BaseSolver, ComplexityScore, SolverResult


class CompraSolver(BaseSolver):
    """Resuelve consenso para compras grupales."""

    def __init__(self, budget_method: str = "minimum"):
        """
        Args:
            budget_method: "minimum" (default) o "median"
        """
        self.budget_method = budget_method

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
        """Evalua complejidad basada en disparidad de presupuestos y productos."""
        factors = []
        score = 0.0

        if len(participants) < 2:
            return ComplexityScore(score=0.0, factors=["Menos de 2 participantes"])

        # Disparidad de presupuestos
        presupuestos = [p.get("presupuesto_max", 0) for p in participants if p.get("presupuesto_max")]
        if presupuestos:
            min_p, max_p = min(presupuestos), max(presupuestos)
            if min_p > 0 and max_p / min_p > 5:
                score += 0.3
                factors.append(f"Presupuestos muy dispares (Q{min_p} - Q{max_p})")
            elif min_p > 0 and max_p / min_p > 2:
                score += 0.1

        # Productos en comun
        all_productos = [set(p.get("productos_interes", [])) for p in participants]
        common_productos = set.intersection(*all_productos) if all_productos else set()

        if len(common_productos) == 0:
            score += 0.3
            factors.append("Sin productos en comun")
        elif len(common_productos) == 1:
            score += 0.1
            factors.append("Solo 1 producto en comun")

        # Prioridades conflictivas
        prioridades = [p.get("prioridad", "") for p in participants]
        prioridad_counter = Counter(prioridades)
        if len(prioridad_counter) > 3:
            score += 0.15
            factors.append("Prioridades muy diversas")

        # Marcas sin overlap
        all_marcas = [set(p.get("marcas_preferidas", [])) for p in participants]
        # Filtrar "sin preferencia"
        all_marcas = [m - {"sin preferencia"} for m in all_marcas]
        all_marcas = [m for m in all_marcas if m]

        if all_marcas:
            common_marcas = set.intersection(*all_marcas) if len(all_marcas) > 1 else all_marcas[0]
            if len(common_marcas) == 0:
                score += 0.15
                factors.append("Sin marcas en comun")

        if not factors:
            factors.append("Buena alineacion de preferencias")

        return ComplexityScore(score=min(score, 1.0), factors=factors)

    def solve(self, participants: list[dict]) -> SolverResult:
        """Resuelve el consenso para una compra grupal."""
        if len(participants) < 2:
            return SolverResult(
                success=False,
                explanation="Se necesitan al menos 2 participantes"
            )

        explanations = []
        budget_label = "Mediana" if self.budget_method == "median" else "Minimo"
        explanations.append(f"Metodo de presupuesto: {budget_label}")

        # Presupuesto
        presupuesto, budget_explanation = self._calculate_budget(participants)
        explanations.append(budget_explanation)

        # Productos mas votados
        producto_counter = Counter()
        for p in participants:
            for prod in p.get("productos_interes", []):
                producto_counter[prod] += 1

        if not producto_counter:
            return SolverResult(success=False, explanation="No hay productos de interes")

        # Top productos
        top_productos = producto_counter.most_common(3)
        productos_seleccionados = [p for p, _ in top_productos]
        explanations.append(f"Productos prioritarios: {', '.join(productos_seleccionados)}")

        # Marcas mas comunes (excluyendo "sin preferencia")
        marca_counter = Counter()
        for p in participants:
            for marca in p.get("marcas_preferidas", []):
                if marca != "sin preferencia":
                    marca_counter[marca] += 1

        marcas_sugeridas = [m for m, _ in marca_counter.most_common(3)] if marca_counter else ["sin preferencia"]
        explanations.append(f"Marcas preferidas: {', '.join(marcas_sugeridas)}")

        # Prioridad mas comun
        prioridad_counter = Counter(p.get("prioridad", "") for p in participants)
        best_prioridad, prior_count = prioridad_counter.most_common(1)[0] if prioridad_counter else ("calidad", 0)
        explanations.append(f"Criterio principal: {best_prioridad} ({prior_count} votos)")

        # Calcular confianza
        if top_productos:
            top_count = top_productos[0][1]
            producto_ratio = top_count / len(participants)
        else:
            producto_ratio = 0

        prior_ratio = prior_count / len(participants) if prior_count else 0
        confidence = (producto_ratio + prior_ratio) / 2

        decision = {
            "Presupuesto por persona": f"Q{presupuesto}",
            "Productos prioritarios": productos_seleccionados,
            "Marcas sugeridas": marcas_sugeridas,
            "Criterio de seleccion": best_prioridad
        }

        return SolverResult(
            success=True,
            decision=decision,
            confidence=confidence,
            explanation="\n".join(explanations)
        )
