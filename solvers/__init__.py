"""Solvers algoritmicos para consenso."""

from .base import BaseSolver, ComplexityScore, SolverResult
from .reunion import ReunionSolver
from .viaje import ViajeSolver
from .proyecto import ProyectoSolver
from .compra import CompraSolver

SOLVERS = {
    "reunion": ReunionSolver(),
    "viaje": ViajeSolver(),
    "proyecto": ProyectoSolver(),
    "compra": CompraSolver(),
}


def get_solver(decision_type: str) -> BaseSolver:
    """Obtiene el solver para un tipo de decision."""
    if decision_type not in SOLVERS:
        raise ValueError(f"No hay solver para tipo: {decision_type}")
    return SOLVERS[decision_type]


__all__ = [
    "BaseSolver",
    "ComplexityScore",
    "SolverResult",
    "ReunionSolver",
    "ViajeSolver",
    "ProyectoSolver",
    "CompraSolver",
    "SOLVERS",
    "get_solver",
]
