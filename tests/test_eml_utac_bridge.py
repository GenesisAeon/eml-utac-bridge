"""Tests for EML-UTAC Bridge (Package 37)."""
import math
import pytest
from eml_utac_bridge import (
    EMLOperator,
    UTACasEML,
    CREPasEML,
    AFETaskEML,
    LagrangianAsEML,
    GenesisAeonReduction,
    GenesisAeonBridge,
)
from eml_utac_bridge.constants import PHI, SIGMA_PHI, V_RIG, GAMMA_UNIVERSAL


class TestEMLOperator:
    def test_exp_from_eml(self):
        eml = EMLOperator()
        for x in [0.0, 1.0, -1.0, 2.5]:
            assert abs(eml.exp_from_eml(x) - math.exp(x)) < 1e-12

    def test_ln_from_eml(self):
        eml = EMLOperator()
        for x in [0.5, 1.0, 2.0, math.e]:
            assert abs(eml.ln_from_eml(x) - math.log(x)) < 1e-12

    def test_tanh_from_eml(self):
        eml = EMLOperator()
        for x in [-2.0, -0.5, 0.0, 0.5, 2.0]:
            assert abs(eml.tanh_from_eml(x) - math.tanh(x)) < 1e-12

    def test_eml_zero_crossing(self):
        eml = EMLOperator()
        assert abs(eml.compute(0.0, math.e)) < 1e-12

    def test_tanh_range(self):
        eml = EMLOperator()
        for x in [-10.0, -1.0, 0.0, 1.0, 10.0]:
            val = eml.tanh_from_eml(x)
            assert -1.0 <= val <= 1.0


class TestCREPasEML:
    def test_equivalence(self):
        crep = CREPasEML()
        for vals in [(0.8, 0.7, 0.6, 0.5), (1.0, 1.0, 1.0, 1.0), (0.3, 0.4, 0.5, 0.6)]:
            assert crep.verify_equivalence(*vals)

    def test_gamma_universal(self):
        crep = CREPasEML()
        # CREP with equal components each equal to GAMMA_UNIVERSAL
        # (g,g,g,g)^(1/4) = g
        g = GAMMA_UNIVERSAL
        gamma = crep.compute(g, g, g, g)
        assert abs(gamma - GAMMA_UNIVERSAL) < 1e-10

    def test_tree_depth(self):
        crep = CREPasEML()
        assert crep.eml_tree_depth() == 6


class TestUTACasEML:
    def test_fixed_point(self):
        utac = UTACasEML(K=1.0, sigma=SIGMA_PHI)
        fp = utac.fixed_point(GAMMA_UNIVERSAL)
        # fixed_point returns K * tanh(sigma*Gamma), should be in (0, K)
        assert 0 < fp < 1.0

    def test_dHdt_zero_at_zero(self):
        utac = UTACasEML()
        assert abs(utac.compute_dHdt(0.0, 0.5)) < 1e-12

    def test_integration_converges(self):
        utac = UTACasEML(r=1.0, K=1.0, sigma=SIGMA_PHI)
        H = utac.integrate(0.01, GAMMA_UNIVERSAL, 50.0, 5000)
        fp = utac.fixed_point(GAMMA_UNIVERSAL)
        assert abs(H[-1] - fp) < 0.01

    def test_tree_depth(self):
        utac = UTACasEML()
        assert utac.eml_tree_depth() == 8


class TestAFETaskEML:
    def test_equivalence(self):
        afet = AFETaskEML()
        for H in [0.1, 0.5, 1.0, 2.0]:
            assert afet.verify_equivalence(H)

    def test_derivative_numerical(self):
        afet = AFETaskEML()
        H = 0.5
        eps = 1e-6
        numerical = (afet.compute(H + eps) - afet.compute(H - eps)) / (2 * eps)
        analytical = afet.derivative(H)
        assert abs(numerical - analytical) < 1e-5


class TestGenesisAeonReduction:
    def test_prove_tanh(self):
        r = GenesisAeonReduction()
        result = r.prove_tanh()
        assert result.eml_valid
        assert result.error < 1e-12
        assert result.tree_depth == 3

    def test_prove_crep(self):
        r = GenesisAeonReduction()
        result = r.prove_crep()
        assert result.eml_valid
        assert result.error < 1e-10

    def test_prove_afet(self):
        r = GenesisAeonReduction()
        result = r.prove_afet()
        assert result.eml_valid

    def test_prove_utac(self):
        r = GenesisAeonReduction()
        result = r.prove_utac()
        assert result.eml_valid
        assert result.error < 1e-12

    def test_full_reduction(self):
        r = GenesisAeonReduction()
        summary = r.reduction_summary()
        assert summary["full_reduction_valid"]
        assert summary["n_components"] == 5
        assert all(summary["components"].values())

    def test_tree_depths(self):
        r = GenesisAeonReduction()
        summary = r.reduction_summary()
        depths = summary["tree_depths"]
        assert depths["tanh(sigma*Gamma)"] == 3
        assert depths["CREP Gamma"] == 6
        assert depths["UTAC dH/dt"] == 8


class TestGenesisAeonBridge:
    def test_diamond_interface(self):
        bridge = GenesisAeonBridge()
        result = bridge.run_cycle(duration=5.0, n_steps=500)
        assert "H_final" in result
        assert "reduction" in result
        assert result["reduction"]["full_reduction_valid"]

    def test_get_crep_state(self):
        bridge = GenesisAeonBridge()
        state = bridge.get_crep_state()
        assert "gamma" in state
        # gamma computed from balanced CREP components derived from GAMMA_UNIVERSAL
        assert state["gamma"] > 0

    def test_get_utac_state(self):
        bridge = GenesisAeonBridge()
        state = bridge.get_utac_state()
        assert "fixed_point" in state
        assert "dHdt" in state

    def test_get_phase_events(self):
        bridge = GenesisAeonBridge()
        events = bridge.get_phase_events()
        assert len(events) == 5
        assert all(e["valid"] for e in events)

    def test_zenodo_record(self):
        bridge = GenesisAeonBridge()
        record = bridge.to_zenodo_record()
        assert record["package"] == 37
        assert record["reduction_summary"]["full_reduction_valid"]

    def test_eml_reduction_valid(self):
        bridge = GenesisAeonBridge()
        assert bridge.eml_reduction_valid()


class TestConstants:
    def test_phi(self):
        assert abs(PHI - 1.6180339887) < 1e-9

    def test_sigma_phi(self):
        assert SIGMA_PHI == 1 / 16

    def test_v_rig(self):
        assert abs(V_RIG - 1352.0) < 5.0  # approx 1352 km/s

    def test_benchmark_targets(self):
        # EML_TARGETS from spec
        r = GenesisAeonReduction()
        summary = r.reduction_summary()
        assert summary["full_reduction_valid"]  # full_reduction_valid: True
        depths = summary["tree_depths"]
        assert abs(depths["UTAC dH/dt"] - 8) <= 2   # tree_depth_utac: (8, 2)
        assert abs(depths["CREP Gamma"] - 6) <= 2        # tree_depth_crep: (6, 2)
