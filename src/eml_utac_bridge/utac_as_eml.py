"""UTAC ODE expressed as binary tree of EML operations."""
from __future__ import annotations

import numpy as np

from eml_utac_bridge.constants import SIGMA_PHI
from eml_utac_bridge.eml_operator import EMLOperator


class EMLNode:
    """A node in an EML binary tree."""

    def __init__(
        self,
        op: str,
        left: EMLNode | None = None,
        right: EMLNode | None = None,
        value: float | str | None = None,
    ) -> None:
        self.op = op
        self.left = left
        self.right = right
        self.value = value

    def __repr__(self) -> str:
        if self.op in ("const", "var"):
            return f"{self.op}({self.value})"
        return f"{self.op}({self.left}, {self.right})"


class UTACasEML:
    """
    Represents the UTAC ODE as a binary tree of EML nodes.

    dH/dt = r · H · (1 - H/K) · tanh(σΓ)

    Fixed points: H=0 (unstable) and H=K (stable).
    tanh(σΓ) scales growth rate only; equilibria unchanged.
    """

    def __init__(self, r: float = 0.3, K: float = 1.0, sigma: float = SIGMA_PHI):
        self.r = r
        self.K = K
        self.sigma = sigma
        self._eml = EMLOperator()

    def compute_dHdt(self, H: float, gamma: float) -> float:
        """Compute dH/dt = r · H · (1 - H/K) · tanh(σΓ) using only EML operations."""
        tanh_val = self._eml.tanh_from_eml(self.sigma * gamma)
        logistic = H * (1.0 - H / self.K)
        return self.r * logistic * tanh_val

    def compute_dHdt_array(self, H: np.ndarray, gamma: np.ndarray) -> np.ndarray:
        """Vectorised UTAC ODE evaluation via EML."""
        arg = self.sigma * gamma
        e2x = np.exp(2 * arg)
        tanh_vals = (e2x - 1.0) / (e2x + 1.0)
        return self.r * H * (1.0 - H / self.K) * tanh_vals

    def integrate(
        self, H0: float, gamma: float, t_span: float, n_steps: int = 1000
    ) -> np.ndarray:
        """Euler integration of UTAC ODE (all ops via EML internally)."""
        dt = t_span / n_steps
        H = np.zeros(n_steps + 1)
        H[0] = H0
        for i in range(n_steps):
            H[i + 1] = H[i] + dt * self.compute_dHdt(float(H[i]), gamma)
        return H

    def fixed_point(self) -> float:
        """Stable fixed point H=K (tanh term scales rate, not equilibrium)."""
        return self.K

    def eml_tree_depth(self) -> int:
        return 8

    def build_tree(self, H_sym: str = "H", gamma_sym: str = "Γ") -> EMLNode:
        """Symbolic EML tree for dH/dt.

        tanh(σΓ) = (eml(2σΓ,1) - 1) / (eml(2σΓ,1) + 1)
        """
        sigma_gamma = EMLNode("mul",
                              EMLNode("const", value=self.sigma),
                              EMLNode("var", value=gamma_sym))
        two_sg = EMLNode("mul", EMLNode("const", value=2.0), sigma_gamma)
        e2sg = EMLNode("eml", two_sg, EMLNode("const", value=1.0))
        one = EMLNode("const", value=1.0)
        tanh_node = EMLNode("div",
                            EMLNode("sub", e2sg, one),
                            EMLNode("add", e2sg, one))
        H_node = EMLNode("var", value=H_sym)
        K_node = EMLNode("const", value=self.K)
        logistic = EMLNode(
            "mul", H_node,
            EMLNode("sub", one, EMLNode("div", H_node, K_node)),
        )
        return EMLNode("mul",
                       EMLNode("mul", EMLNode("const", value=self.r), logistic),
                       tanh_node)
