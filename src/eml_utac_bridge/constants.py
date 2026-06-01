"""Physical and mathematical constants for EML-UTAC bridge."""
import math

PHI = (1 + math.sqrt(5)) / 2          # Golden ratio
SIGMA_PHI = 1 / 16                     # Frame principle
ALPHA = 1 / 137.035999084              # Fine structure constant
C_LIGHT = 299792.458                   # km/s
V_RIG = C_LIGHT * ALPHA / PHI         # ≈ 1352.12 km/s
GAMMA_UNIVERSAL = 0.251                # Triple universality
E = math.e
