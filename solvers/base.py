"""Interfaces base para los solvers algoritmicos."""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class ComplexityScore:
    """Resultado de evaluar la complejidad de un problema."""
    score: float  # 0.0 (trivial) - 1.0 (muy complejo)
    factors: list[str] = field(default_factory=list)

    def is_simple(self, threshold: float = 0.6) -> bool:
        return self.score < threshold


@dataclass
class SolverResult:
    """Resultado de intentar resolver un problema."""
    success: bool
    decision: dict = field(default_factory=dict)
    confidence: float = 0.0  # 0.0 - 1.0
    explanation: str = ""

    def format_output(self) -> str:
        """Formatea el resultado para mostrar al usuario."""
        if not self.success:
            return "No se pudo resolver algoritmicamente."

        lines = ["DECISION"]
        for key, value in self.decision.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value) if value else "ninguna"
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("JUSTIFICACION")
        for line in self.explanation.split("\n"):
            if line.strip():
                lines.append(f"- {line.strip()}")

        lines.append("")
        lines.append(f"CONFIANZA: {int(self.confidence * 100)}%")
        lines.append("METODO: Algoritmico")

        return "\n".join(lines)


class BaseSolver(ABC):
    """Clase base para todos los solvers."""

    @abstractmethod
    def evaluate_complexity(self, participants: list[dict]) -> ComplexityScore:
        """Evalua la complejidad del problema."""
        pass

    @abstractmethod
    def solve(self, participants: list[dict]) -> SolverResult:
        """Intenta resolver el problema."""
        pass
