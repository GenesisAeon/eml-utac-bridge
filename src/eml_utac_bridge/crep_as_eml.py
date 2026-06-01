"""CREP tensor Γ = (C·R·E·P)^(1/4) expressed as EML operator tree."""
from __future__ import annotations

from eml_utac_bridge.eml_operator import EMLOperator


class CREPasEML:
    """
    CREP tensor in EML form.

    Γ = (C·R·E·P)^(1/4) = exp((ln C + ln R + ln E + ln P) / 4)

    EML decomposition:
      ln(x) = 1 - eml(0, x)
      sum_lns = ln(C) + ln(R) + ln(E) + ln(P)
      Γ = eml(sum_lns / 4, 1)
    """

    def __init__(self) -> None:
        self._eml = EMLOperator()

    def compute(self, C: float, R: float, E: float, P: float) -> float:
        """Compute Γ = (C·R·E·P)^(1/4) using EML operations."""
        ln_C = self._eml.ln_from_eml(C)
        ln_R = self._eml.ln_from_eml(R)
        ln_E = self._eml.ln_from_eml(E)
        ln_P = self._eml.ln_from_eml(P)
        sum_lns = ln_C + ln_R + ln_E + ln_P
        return self._eml.exp_from_eml(sum_lns / 4.0)

    def compute_direct(self, C: float, R: float, E: float, P: float) -> float:
        """Direct computation for numerical verification."""
        return (C * R * E * P) ** 0.25

    def verify_equivalence(
        self, C: float, R: float, E: float, P: float, tol: float = 1e-10
    ) -> bool:
        """Check EML formulation matches direct computation."""
        return abs(self.compute(C, R, E, P) - self.compute_direct(C, R, E, P)) < tol

    def eml_tree_depth(self) -> int:
        """EML tree depth: 4 ln-nodes + 1 sum + 1 div + 1 exp = ~6 nodes."""
        return 6

    def crep_components_as_eml(self, C: float, R: float, E: float, P: float) -> dict:
        """Returns each CREP component expressed as EML value."""
        return {
            "ln_C_eml": self._eml.ln_from_eml(C),
            "ln_R_eml": self._eml.ln_from_eml(R),
            "ln_E_eml": self._eml.ln_from_eml(E),
            "ln_P_eml": self._eml.ln_from_eml(P),
            "gamma_eml": self.compute(C, R, E, P),
            "gamma_direct": self.compute_direct(C, R, E, P),
        }
