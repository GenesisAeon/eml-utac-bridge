"""Tests for EML-UTAC Bridge (Package 37)."""
import math

from eml_utac_bridge import (
    AFETaskEML,
    CREPasEML,
    EMLOperator,
    GenesisAeonBridge,
    GenesisAeonReduction,
    UTACasEML,
)
from eml_utac_bridge.constants import GAMMA_UNIVERSAL, PHI, PHI_CUBEROOT, SIGMA_PHI, V_RIG


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
        # (g, g, g, g)^(1/4) == g exactly
        g = GAMMA_UNIVERSAL
        gamma = crep.compute(g, g, g, g)
        assert abs(gamma - GAMMA_UNIVERSAL) < 1e-10

    def test_tree_depth(self):
        crep = CREPasEML()
        assert crep.eml_tree_depth() == 6


class TestUTACasEML:
    def test_fixed_point_is_K(self):
        utac = UTACasEML(K=1.0, sigma=SIGMA_PHI)
        # dH/dt = r*H*(1-H/K)*tanh(σΓ) → fixed points H=0 and H=K
        assert utac.fixed_point() == 1.0

    def test_dHdt_zero_at_zero(self):
        utac = UTACasEML()
        assert abs(utac.compute_dHdt(0.0, 0.5)) < 1e-12

    def test_dHdt_zero_at_K(self):
        utac = UTACasEML(K=1.0)
        assert abs(utac.compute_dHdt(1.0, 0.5)) < 1e-12

    def test_integration_converges_to_K(self):
        # Use sigma=2.0 so tanh(σΓ) ≈ 0.46 gives a meaningful growth rate
        utac = UTACasEML(r=1.0, K=1.0, sigma=2.0)
        H = utac.integrate(0.01, GAMMA_UNIVERSAL, 50.0, 5000)
        assert abs(H[-1] - 1.0) < 0.01  # converges to K=1

    def test_tree_depth(self):
        utac = UTACasEML()
        assert utac.eml_tree_depth() == 8

    def test_tree_denominator_correct(self):
        # Verify build_tree denominator matches numerical formula
        # tanh(x) = (exp(2x)-1)/(exp(2x)+1) — denominator is exp(2x)+1
        # In build_tree: EMLNode("add", e2sg, one) — correct (+1, not +2)
        utac = UTACasEML()
        tree = utac.build_tree()
        # tanh_node = tree.right: div(sub(e2sg,1), add(e2sg,1))
        tanh_node = tree.right
        denom = tanh_node.right
        assert denom.op == "add"
        assert denom.right.value == 1.0  # +1, not +2


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

    def test_get_crep_state_consistent(self):
        bridge = GenesisAeonBridge()
        state = bridge.get_crep_state()
        # Equal components (g,g,g,g) must recover bridge.gamma exactly
        assert abs(state["gamma"] - bridge.gamma) < 1e-10
        assert state["C"] == bridge.gamma

    def test_get_utac_state(self):
        bridge = GenesisAeonBridge()
        state = bridge.get_utac_state()
        assert state["fixed_point"] == bridge.K  # fixed point is K, not K*tanh(...)
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

    def test_phi_cuberoot(self):
        assert abs(PHI_CUBEROOT - 1.17398499670) < 1e-10
        assert abs(PHI_CUBEROOT**3 - PHI) < 1e-12

    def test_sigma_phi(self):
        assert SIGMA_PHI == 1 / 16

    def test_v_rig(self):
        assert abs(V_RIG - 1352.0) < 5.0

    def test_benchmark_targets(self):
        r = GenesisAeonReduction()
        summary = r.reduction_summary()
        assert summary["full_reduction_valid"]
        depths = summary["tree_depths"]
        assert abs(depths["UTAC dH/dt"] - 8) <= 2
        assert abs(depths["CREP Gamma"] - 6) <= 2
