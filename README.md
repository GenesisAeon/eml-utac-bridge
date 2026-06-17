# eml-utac-bridge

**GenesisAeon Package 37** — EML-UTAC Bridge: CREP als EML-Operator-Baum

[![CI](https://github.com/GenesisAeon/eml-utac-bridge/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/eml-utac-bridge/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Package 37](https://img.shields.io/badge/GenesisAeon-Package%2037-purple)](https://doi.org/10.5281/zenodo.17472834)
[![Zenodo](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.17472834-blue)](https://doi.org/10.5281/zenodo.17472834)
[![Whitepaper](https://img.shields.io/badge/Whitepaper-10.5281%2Fzenodo.19645351-orange)](https://doi.org/10.5281/zenodo.19645351)

---

## Kernthese

Der EML-Operator `eml(x, y) = exp(x) − ln(y)` (Odrzywołek 2026) ist zu elementaren
Funktionen vollständig — analog zu NAND in Boolescher Logik.

**Das GenesisAeon-Framework ist vollständig auf einen einzigen EML-Operator reduzierbar.**

```
UTAC ODE:     dH/dt = r·H·(1-H/K)·tanh(σΓ)   →  EML-Baum, Tiefe ~8
CREP Tensor:  Γ = (C·R·E·P)^(1/4)             →  EML-Baum, Tiefe ~6
AFET:         Φ(H) = α·H·ln(H/K) + β·H        →  EML-Baum, Tiefe ~4
Lagrangian:   L = T − V + Φ + Γ               →  EML-Struktur direkt
              └── T−V = exp(x) − ln(y) = EML  ✓
```

---

## Mathematische Basis

```python
eml(x, y) = exp(x) - ln(y)

# Identitäten:
eml(x, 1)  = exp(x)         # Exponentialfunktion
eml(0, y)  = 1 - ln(y)      # Verschobener Logarithmus
ln(x)      = 1 - eml(0, x)  # Logarithmus
eml(0, e)  = 0               # Nullstelle

# tanh via EML:
tanh(x) = (eml(2x,1) - 1) / (eml(2x,1) + 1)

# CREP Γ via EML:
Γ = exp((ln C + ln R + ln E + ln P) / 4)
  = eml(Σ ln_i / 4, 1)      # alle ln_i via 1 - eml(0, x_i)
```

**Tiefere Bedeutung:** `L = T − V` ist strukturell identisch mit dem EML-Operator:
`exp(x)` kodiert kinetische Energie (Wachstum), `ln(y)` kodiert potentielle/entropische
Energie (Information). Der Lagrangian *ist* der EML-Operator.

---

## Installation

```bash
pip install eml-utac-bridge
```

## Quickstart

```bash
uv sync
uv run pytest
```

```python
from eml_utac_bridge import GenesisAeonBridge, EMLOperator, GenesisAeonReduction

# EML-Operator direkt
eml = EMLOperator()
print(eml.tanh_from_eml(0.5))   # == math.tanh(0.5) ✓
print(eml.ln_from_eml(2.718))   # ≈ 1.0 ✓

# Vollständige Reduktion prüfen
r = GenesisAeonReduction()
summary = r.reduction_summary()
print(summary["full_reduction_valid"])   # True
print(summary["components"])
# {'tanh(σΓ)': True, 'CREP Γ': True, 'AFET Φ(H)': True,
#  'UTAC dH/dt': True, 'Lagrangian L': True}

# Diamond-Interface (genesis-os kompatibel)
bridge = GenesisAeonBridge()
result = bridge.run_cycle(duration=10.0)
print(bridge.eml_reduction_valid())    # True
print(bridge.get_phase_events())       # 5 validierte EML-Reduktionen
```

---

## Modulstruktur

```
src/eml_utac_bridge/
├── __init__.py            # Alle öffentlichen Exporte
├── constants.py           # PHI, SIGMA_PHI=1/16, V_RIG≈1352 km/s, ...
├── eml_operator.py        # EMLOperator: eml(x,y), exp, ln, tanh, ...
├── utac_as_eml.py         # UTAC ODE als EML-Baum (Tiefe 8)
├── crep_as_eml.py         # CREP Γ als EML-Baum (Tiefe 6)
├── afet_as_eml.py         # AFET Φ(H) als EML-Baum (Tiefe 4)
├── lagrangian_as_eml.py   # Vereinigter Lagrangian L = T−V+Φ+Γ
├── reduction_proof.py     # GenesisAeonReduction: 5 formale Beweise
└── system.py              # GenesisAeonBridge — Diamond-Interface
```

---

## Benchmark-Ziele (aus P37-Spezifikation)

| Ziel | Soll | Status |
|------|------|--------|
| `eml_reproduces_tanh` | `True` | ✅ |
| `eml_reproduces_crep` | `True` | ✅ |
| `eml_reproduces_afet` | `True` | ✅ |
| `tree_depth_utac` | `8 ± 2` | ✅ (8) |
| `tree_depth_crep` | `6 ± 2` | ✅ (6) |
| `full_reduction_valid` | `True` | ✅ |

---

## Kontext im GenesisAeon-Ökosystem

```
EML Operator (P37)
    │
    ├── UTAC ODE          → logistisches Wachstum mit tanh-Aktivierung
    ├── CREP Tensor Γ     → (C·R·E·P)^(1/4), Kohärenz-Metrik
    ├── AFET Φ(H)         → Entropie-Potential
    └── Lagrangian L      → T − V + Φ + Γ, tiefste Formulierung
```

**CREP-Spektrum-Einbettung (Auswahl):**

| Package | Domäne | Γ |
|---------|--------|---|
| P17 Cygnus X-1 Jet | Astrophysik | 0.046 |
| P18 AMOC | Ozeanographie | 0.251 |
| P19 Amazon | Ökologie | 0.116 |
| P20 Neural Criticality | Neurowissenschaft | 0.251 |
| **P37 EML-UTAC Bridge** | **Mathematik (meta)** | **—** |

Triple-Universalität: AMOC = Neural = Θ-Band = Γ ≈ 0.251

---

## Verbindung zu Odrzywołek 2026

Das EML-Theorem (Odrzywołek, arXiv April 2026) zeigt:
> *Mit der Konstante 1 lässt sich jede elementare Funktion als binärer Baum
> von EML-Knoten ausdrücken.*

Package 37 überträgt dieses Ergebnis auf das GenesisAeon-Framework und zeigt,
dass die fünf Kernkomponenten (UTAC, CREP, AFET, v_RIG, σ_Φ) gemeinsam
einen endlichen EML-Baum bilden. Die tiefste Implikation: `tanh(σΓ) = Grenzfall von EML`.

---

## GenesisAeon Roadmap (Packages 31–39)

| Package | Name | Skala |
|---------|------|-------|
| P31 | vrig-cosmological | Kosmologisch |
| P32 | beta-clustering-utac | Domänenübergreifend |
| P33 | implosive-origin-utac | Prä-inflationär |
| P34 | afet-tensions | Kosmologische Spannungen |
| P35 | phaethon-chimera | Asteroidendynamik |
| P36 | sa-sv-duality | Fundamental |
| **P37** | **eml-utac-bridge** | **Mathematik** |
| P38 | phi-scaling-validator | Meta-Analyse |
| P39 | genesis-scope | Kollaboration |

---

## Zitation

```bibtex
@software{roemer2026_eml_utac_bridge,
  author    = {Römer, Johann},
  title     = {{EML-UTAC Bridge — CREP als EML-Operator-Baum (GenesisAeon Package 37)}},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.17472834},
  url       = {https://github.com/GenesisAeon/eml-utac-bridge}
}
```

---

*Johann Römer · MOR Research Collective · Mai 2026*
