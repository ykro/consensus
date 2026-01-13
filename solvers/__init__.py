"""Solvers algoritmicos para consenso."""

from .base import BaseSolver, ComplexityScore, SolverResult
from .reunion import ReunionSolver
from .viaje import ViajeSolver
from .proyecto import ProyectoSolver
from .compra import CompraSolver


def get_solver(
    decision_type: str,
    voting_method: str = "plurality",
    budget_method: str = "minimum",
    matching_method: str = "greedy"
) -> BaseSolver:
    """
    Obtiene el solver para un tipo de decision con configuracion especifica.

    Args:
        decision_type: Tipo de decision (reunion, viaje, proyecto, compra)
        voting_method: Metodo de votacion ("plurality" o "borda")
        budget_method: Metodo de presupuesto ("minimum" o "median")
        matching_method: Metodo de matching ("greedy" o "gale-shapley")

    Returns:
        Instancia del solver configurado
    """
    if decision_type == "reunion":
        return ReunionSolver(voting_method=voting_method)
    elif decision_type == "viaje":
        return ViajeSolver(voting_method=voting_method, budget_method=budget_method)
    elif decision_type == "proyecto":
        return ProyectoSolver(matching_method=matching_method)
    elif decision_type == "compra":
        return CompraSolver(budget_method=budget_method)
    else:
        raise ValueError(f"No hay solver para tipo: {decision_type}")


__all__ = [
    "BaseSolver",
    "ComplexityScore",
    "SolverResult",
    "ReunionSolver",
    "ViajeSolver",
    "ProyectoSolver",
    "CompraSolver",
    "get_solver",
]
