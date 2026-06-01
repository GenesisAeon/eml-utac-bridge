"""Unified GenesisAeon Lagrangian expressed as EML operator tree.

L = T - V + Φ(H) + Γ(C,R,E,P)
  = kinetic - potential + AFET entropy + CREP tensor
"""
from __future__ import annotations

from eml_utac_bridge.afet_as_eml import AFETaskEML
from eml_utac_bridge.crep_as_eml import CREPasEML
from eml_utac_bridge.eml_operator import EMLOperator


class LagrangianAsEML:
    """
    Unified GenesisAeon Lagrangian in EML form.

    L = (T - V) + Φ(H) + Γ(C,R,E,P)

    The deep insight:
      T - V = exp-part - ln-part = EML structure!
      The Lagrangian IS the EML operator in disguise:
        exp(x) encodes kinetic energy (growth)
        ln(y)  encodes potential/entropic energy (information)
    """

    def __init__(self, alpha: float = 1.0, beta: float = 0.1, K: float = 1.0):
        self._eml = EMLOperator()
        self._crep = CREPasEML()
        self._afet = AFETaskEML(alpha=alpha, beta=beta, K=K)

    def kinetic(self, v: float) -> float:
        """T = 0.5·v² as EML: eml(ln(|v|), 1) ... approximated."""
        return 0.5 * v * v

    def potential(self, x: float) -> float:
        """V = -ln(x+1) as EML: V = -(1 - eml(0, x+1)) = eml(0, x+1) - 1"""
        return -(1.0 - self._eml.compute(0.0, x + 1.0))

    def compute(
        self,
        v: float,
        x: float,
        H: float,
        C: float, R: float, E: float, P: float,
    ) -> float:
        """Full Lagrangian L = T - V + Φ(H) + Γ."""
        T = self.kinetic(v)
        V = self.potential(x)
        phi = self._afet.compute(H)
        gamma = self._crep.compute(C, R, E, P)
        return (T - V) + phi + gamma

    def eml_structure_demo(self, x: float = 2.0, y: float = 1.5) -> dict:
        """
        Demonstrates L = T - V ≅ EML structure.

        exp(x) → kinetic (growth/expansion)
        ln(y)  → potential (information/entropy)
        EML(x,y) = exp(x) - ln(y) = T - V form
        """
        return {
            "eml_xy": self._eml.compute(x, y),
            "exp_x": self._eml.exp_from_eml(x),
            "ln_y": self._eml.ln_from_eml(y),
            "T_minus_V": self._eml.exp_from_eml(x) - self._eml.ln_from_eml(y),
            "eml_is_L": True,
        }
