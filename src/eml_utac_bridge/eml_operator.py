"""EML operator: eml(x, y) = exp(x) - ln(y).

Reference: Odrzywołek (2026) — a single binary operation generates all elementary functions.
"""
from __future__ import annotations
import math
import numpy as np


class EMLOperator:
    """
    Universal elementary function operator: eml(x, y) = exp(x) - ln(y).

    Any elementary function is expressible as a binary tree of EML nodes
    applied to the constant 1.

    Properties:
        eml(x, 1)  = exp(x)         (exponential)
        eml(0, y)  = 1 - ln(y)      (shifted log)
        eml(0, e)  = 0               (zero crossing)
        -eml(0, y) + 1 = ln(y)      (natural log recovery)
    """

    @staticmethod
    def compute(x: float, y: float) -> float:
        return math.exp(x) - math.log(y)

    @staticmethod
    def compute_array(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return np.exp(x) - np.log(y)

    @staticmethod
    def exp_from_eml(x: float) -> float:
        """exp(x) = eml(x, 1)"""
        return EMLOperator.compute(x, 1.0)

    @staticmethod
    def ln_from_eml(x: float) -> float:
        """ln(x) = 1 - eml(0, x)"""
        if x <= 0:
            raise ValueError("ln undefined for x <= 0")
        return 1.0 - EMLOperator.compute(0.0, x)

    @staticmethod
    def tanh_from_eml(x: float) -> float:
        """
        tanh(x) expressed via EML operations.

        tanh(x) = (exp(2x) - 1) / (exp(2x) + 1)
                = (eml(2x,1) - eml(0,1)) / (eml(2x,1) + eml(0,1) + 2)

        Note: eml(0,1) = exp(0) - ln(1) = 1 - 0 = 1
        """
        e2x = EMLOperator.exp_from_eml(2 * x)  # eml(2x, 1) = exp(2x)
        return (e2x - 1.0) / (e2x + 1.0)

    @staticmethod
    def sigmoid_from_eml(x: float) -> float:
        """σ(x) = 1 / (1 + exp(-x)) via EML."""
        neg_exp = EMLOperator.exp_from_eml(-x)  # eml(-x, 1)
        return 1.0 / (1.0 + neg_exp)

    @staticmethod
    def pow_from_eml(base: float, exponent: float) -> float:
        """base^exponent = exp(exponent * ln(base)) via EML."""
        ln_base = EMLOperator.ln_from_eml(base)
        return EMLOperator.exp_from_eml(exponent * ln_base)

    def eml_tree_depth_tanh(self) -> int:
        """Returns the EML binary tree depth for tanh(x)."""
        # eml(2x,1) → 1 node; subtraction/division → 2 more nodes
        return 3

    def eml_tree_depth_crep(self) -> int:
        """Returns the EML binary tree depth for CREP Γ = (C·R·E·P)^(1/4)."""
        # 3 ln nodes + 1 sum + 1 div/4 + 1 exp = 6 nodes
        return 6
