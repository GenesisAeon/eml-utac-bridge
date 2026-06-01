"""GenesisAeonBridge — Diamond interface for Package 37."""
from __future__ import annotations

from dataclasses import dataclass, field

from eml_utac_bridge.constants import GAMMA_UNIVERSAL, SIGMA_PHI
from eml_utac_bridge.crep_as_eml import CREPasEML
from eml_utac_bridge.reduction_proof import GenesisAeonReduction
from eml_utac_bridge.utac_as_eml import UTACasEML


@dataclass
class GenesisAeonBridge:
    """
    Diamond interface for EML-UTAC Bridge (Package 37).

    Implements the standard GenesisAeon Diamond contract:
      run_cycle(), get_crep_state(), get_utac_state(),
      get_phase_events(), to_zenodo_record()
    """

    sigma: float = SIGMA_PHI
    gamma: float = GAMMA_UNIVERSAL
    H0: float = 0.1
    r: float = 0.3
    K: float = 1.0
    _history: list = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._reduction = GenesisAeonReduction()
        self._utac = UTACasEML(r=self.r, K=self.K, sigma=self.sigma)
        self._crep = CREPasEML()

    def run_cycle(self, duration: float = 10.0, n_steps: int = 1000) -> dict:
        """Run UTAC integration via EML and record phase events."""
        H_traj = self._utac.integrate(self.H0, self.gamma, duration, n_steps)
        summary = self._reduction.reduction_summary()
        self._history.append({
            "H_final": float(H_traj[-1]),
            # True fixed points of dH/dt = r*H*(1-H/K)*tanh(σΓ) are H=0 and H=K
            "H_fixed_point": self.K,
            "reduction": summary,
        })
        return self._history[-1]

    def get_crep_state(self) -> dict:
        """Current CREP state with equal components that recover self.gamma exactly."""
        # (g, g, g, g)^(1/4) = g  — consistent with the bridge's configured gamma
        g = self.gamma
        gamma_computed = self._crep.compute(g, g, g, g)
        return {
            "gamma": gamma_computed,
            "C": g, "R": g, "E": g, "P": g,
            "sigma": self.sigma,
        }

    def get_utac_state(self) -> dict:
        """Current UTAC state."""
        return {
            "H": self.H0,
            "r": self.r,
            "K": self.K,
            "sigma": self.sigma,
            # Fixed points are H=0 (unstable) and H=K (stable)
            "fixed_point": self.K,
            "dHdt": self._utac.compute_dHdt(self.H0, self.gamma),
        }

    def get_phase_events(self) -> list:
        """Phase events: EML reduction validations that passed."""
        results = self._reduction.run_full_reduction()
        return [
            {"component": r.component, "valid": r.eml_valid, "tree_depth": r.tree_depth}
            for r in results if r.eml_valid
        ]

    def to_zenodo_record(self) -> dict:
        """Zenodo-compatible metadata record."""
        summary = self._reduction.reduction_summary()
        keywords = ["EML", "UTAC", "CREP", "GenesisAeon", "elementary functions", "operator tree"]
        return {
            "title": "EML-UTAC Bridge — CREP as EML Operator Tree",
            "package": 37,
            "description": (
                "GenesisAeon Package 37: Mathematical bridge showing that all "
                "GenesisAeon components (UTAC, CREP, AFET, Lagrangian) are "
                "expressible as binary trees of the EML operator eml(x,y)=exp(x)-ln(y). "
                "Reference: Odrzywołek (2026)."
            ),
            "creators": [{"name": "Römer, Johann", "affiliation": "MOR Research Collective"}],
            "keywords": keywords,
            "related_identifiers": [
                {"identifier": "10.5281/zenodo.17472834", "relation": "isPartOf"},
            ],
            "version": "0.1.0",
            "reduction_summary": summary,
        }

    def eml_reduction_valid(self) -> bool:
        """True if all five GenesisAeon components reduce to EML."""
        return self._reduction.reduction_summary()["full_reduction_valid"]
