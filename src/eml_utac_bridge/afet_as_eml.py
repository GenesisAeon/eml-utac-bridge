"""AFET entropy functional Φ(H) expressed via EML operations."""
from __future__ import annotations
import math
from eml_utac_bridge.eml_operator import EMLOperator


class AFETaskEML:
    """
    AFET entropy potential in EML form.

    Φ(H) = α·H·ln(H/K) + β·H
           = α·H·(ln(H) - ln(K)) + β·H

    EML decomposition:
      ln(H)   = 1 - eml(0, H)
      ln(K)   = 1 - eml(0, K)
      ln(H/K) = ln(H) - ln(K)
      Φ(H)    = α·H·(ln_H - ln_K) + β·H
    """

    def __init__(self, alpha: float = 1.0, beta: float = 0.1, K: float = 1.0):
        self.alpha = alpha
        self.beta = beta
        self.K = K
        self._eml = EMLOperator()

    def compute(self, H: float) -> float:
        """Compute Φ(H) using EML operations."""
        if H <= 0:
            raise ValueError("H must be positive for AFET Φ(H)")
        ln_H = self._eml.ln_from_eml(H)
        ln_K = self._eml.ln_from_eml(self.K)
        return self.alpha * H * (ln_H - ln_K) + self.beta * H

    def compute_direct(self, H: float) -> float:
        """Direct computation for verification."""
        return self.alpha * H * math.log(H / self.K) + self.beta * H

    def derivative(self, H: float) -> float:
        """dΦ/dH = α·(ln(H/K) + 1) + β via EML."""
        ln_H = self._eml.ln_from_eml(H)
        ln_K = self._eml.ln_from_eml(self.K)
        return self.alpha * (ln_H - ln_K + 1.0) + self.beta

    def verify_equivalence(self, H: float, tol: float = 1e-10) -> bool:
        return abs(self.compute(H) - self.compute_direct(H)) < tol

    def entropy_production_rate(self, H: float, dHdt: float) -> float:
        """S_A production: σ_s = dΦ/dH · dH/dt"""
        return self.derivative(H) * dHdt
