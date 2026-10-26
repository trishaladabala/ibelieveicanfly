#!/usr/bin/env python3
"""
test_fb_vector_reciprocity.py

Comprehensive automated test suite for the VectorWing Fan-Shaped Body
reciprocity and layer-column connectomics pipeline.

Verifies:
1. Directed graph reciprocity definitions and mathematical invariants.
2. Degree sequence invariants (in-degree, out-degree, mutual degree sums).
3. Conditional label-permutation invariants (M constant, marginal preservation).
4. Continuous degree k-NN micro-stratification partition invariants.
5. FlyWire v2.1.0 annotation mapping integrity and 100% node coverage.
6. Strict directional chemical polarity in columnar-tangential loops.
7. Benjamini-Hochberg FDR monotonic ordering and edge cases.
"""
from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
import random
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FB_CACHE = PROJECT_ROOT / "fb_vector_reciprocity" / "data" / "fb_node_covariates.json"
FB_ANNOT_MAP = PROJECT_ROOT / "fb_vector_reciprocity" / "data" / "fb_annotation_map.json"
FB_STUDY_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_controlled_study_results.json"
FB_ANATOMY_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_layer_column_anatomy.json"
FB_KNN_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_continuous_degree_results.json"
FB_SIM_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_dynamical_simulation_results.json"


class TestFBGraphInvariants(unittest.TestCase):
    """Verifies graph invariants, reciprocity mathematics, and degree consistency."""

    @classmethod
    def setUpClass(cls):
        with open(FB_CACHE) as f:
            cls.data = json.load(f)
        cls.active_nodes = cls.data["active_nodes"]
        cls.mutual_dyads = cls.data["mutual_dyads"]
        cls.nodes = cls.data["nodes"]
        cls.edges = cls.data["directed_edges"]
        cls.edge_set = set((u, v) for u, v, _ in cls.edges)

    def test_active_node_and_edge_counts(self):
        """Verify exact match with Phase 6 audited baseline."""
        self.assertEqual(len(self.active_nodes), 2465)
        self.assertEqual(len(self.edges), 46903)
        self.assertEqual(len(self.mutual_dyads), 5435)

    def test_reciprocity_mathematical_consistency(self):
        """Verify edge reciprocity R_edge = 2M / E and dyad reciprocity R_dyad = M / (E - M)."""
        E = len(self.edges)
        M = len(self.mutual_dyads)
        r_edge = 2.0 * M / E
        r_dyad = float(M) / (E - M)

        self.assertAlmostEqual(r_edge * 100.0, 23.1755, places=3)
        self.assertAlmostEqual(r_dyad * 100.0, 13.1065, places=3)

    def test_autapse_exclusion_and_distinct_endpoints(self):
        """Verify zero autapses (pre == post) in directed edges and mutual dyads."""
        for u, v, _ in self.edges:
            self.assertNotEqual(u, v, f"Autapse detected in directed edges: {u}")
        for u, v in self.mutual_dyads:
            self.assertNotEqual(u, v, f"Autapse detected in mutual dyads: {u}")
            self.assertLess(u, v, f"Mutual dyad endpoints not canonically ordered (u < v): {u}, {v}")

    def test_bidirectional_existence_of_mutual_dyads(self):
        """Verify that for every mutual dyad (u, v), both (u, v) and (v, u) exist in directed edges."""
        for u, v in self.mutual_dyads:
            self.assertIn((u, v), self.edge_set, f"Edge ({u}, {v}) missing from edge set")
            self.assertIn((v, u), self.edge_set, f"Edge ({v}, {u}) missing from edge set")

    def test_degree_sum_invariants(self):
        """Verify sum(in_deg) == |E|, sum(out_deg) == |E|, and sum(m_deg) == 2*M."""
        E = len(self.edges)
        M = len(self.mutual_dyads)

        sum_in = sum(info["in_deg"] for info in self.nodes.values())
        sum_out = sum(info["out_deg"] for info in self.nodes.values())
        sum_m = sum(info["m_deg"] for info in self.nodes.values())

        self.assertEqual(sum_in, E)
        self.assertEqual(sum_out, E)
        self.assertEqual(sum_m, 2 * M)

    def test_64bit_root_id_precision(self):
        """Verify that root IDs exceed 2^32 and preserve 64-bit precision without floating loss."""
        large_ids = [n for n in self.active_nodes if n > (1 << 32)]
        self.assertEqual(len(large_ids), len(self.active_nodes), "All FlyWire root IDs should be > 2^32")
        for nid in self.active_nodes:
            self.assertIsInstance(nid, int)
            self.assertGreater(nid, 720575940000000000)


class TestConditionalNullModelInvariants(unittest.TestCase):
    """Verifies label-permutation invariants and statistical corrections."""

    @classmethod
    def setUpClass(cls):
        with open(FB_CACHE) as f:
            cls.data = json.load(f)
        cls.active_nodes = cls.data["active_nodes"]
        cls.mutual_dyads = cls.data["mutual_dyads"]
        cls.nodes = cls.data["nodes"]
        with open(FB_STUDY_JSON) as f:
            cls.study = json.load(f)

    def test_topology_conservation_across_permutations(self):
        """Verify that label permutation holds the mutual dyad graph invariant."""
        M = len(self.mutual_dyads)
        # For any permutation, sum of counts across all 21 pairs must equal M
        models = self.study["models"]
        for m_id, m_data in models.items():
            p_stats = m_data["results"]["pair_statistics"]
            null_mean_sum = sum(st["null_mean"] for st in p_stats.values())
            self.assertAlmostEqual(null_mean_sum, float(M), delta=1.0,
                                   msg=f"Model {m_id} sum of null means does not match total M")

    def test_empirical_p_value_bounds(self):
        """Verify finite-sample empirical p-value bounds [1/(B+1), 1.0]."""
        models = self.study["models"]
        B = 2000
        min_p = 1.0 / (B + 1)
        for m_id, m_data in models.items():
            p_stats = m_data["results"]["pair_statistics"]
            for pair_name, st in p_stats.items():
                p = st["empirical_p_value"]
                self.assertGreaterEqual(p, min_p - 1e-9)
                self.assertLessEqual(p, 1.0 + 1e-9)

    def test_benjamini_hochberg_fdr_monotonicity(self):
        """Verify that FDR q-values preserve weak monotonicity with respect to p-values."""
        models = self.study["models"]
        for m_id, m_data in models.items():
            p_stats = m_data["results"]["pair_statistics"]
            sorted_items = sorted(p_stats.values(), key=lambda x: x["empirical_p_value"])
            for i in range(len(sorted_items) - 1):
                p_curr, q_curr = sorted_items[i]["empirical_p_value"], sorted_items[i]["fdr_q_value"]
                p_next, q_next = sorted_items[i + 1]["empirical_p_value"], sorted_items[i + 1]["fdr_q_value"]
                if p_curr < p_next:
                    self.assertLessEqual(q_curr, q_next + 1e-9,
                                         f"FDR non-monotonic in {m_id}: p1={p_curr}, q1={q_curr}, p2={p_next}, q2={q_next}")

    def test_ach_gaba_persistence_across_all_models(self):
        """Verify that ACh <-> GABA is significantly enriched (q < 0.05, Ratio >= 4.5x, Z > 12) across all 4 models."""
        models = self.study["models"]
        for m_id, m_data in models.items():
            st = m_data["results"]["pair_statistics"]["ach_gaba"]
            self.assertEqual(st["observed"], 554)
            self.assertGreater(st["enrichment_ratio"], 4.5, f"Enrichment ratio < 4.5x in {m_id}")
            self.assertGreater(st["z_score"], 12.0, f"Z-score < 12 in {m_id}")
            self.assertTrue(st["fdr_significant"], f"ACh-GABA not FDR significant in {m_id}")


class TestAnnotationMappingAndAnatomyInvariants(unittest.TestCase):
    """Verifies FlyWire v2.1.0 annotation coverage, layer distribution, and polarity invariants."""

    @classmethod
    def setUpClass(cls):
        with open(FB_ANNOT_MAP) as f:
            cls.annot_map = json.load(f)
        with open(FB_ANATOMY_JSON) as f:
            cls.anatomy = json.load(f)
        with open(FB_CACHE) as f:
            cls.data = json.load(f)
        cls.mutual_dyads = cls.data["mutual_dyads"]
        cls.nodes = cls.data["nodes"]

    def test_100_percent_node_annotation_coverage(self):
        """Verify that all 2,465 active FB nodes have matching FlyWire v2.1.0 annotations."""
        self.assertEqual(len(self.annot_map), 2465)

    def test_columnar_tangential_ach_gaba_dominance(self):
        """Verify that over 99% of ACh <-> GABA mutual dyads are formed between columnar and tangential neurons."""
        ach_gaba_broad = self.anatomy["ach_gaba_broad"]
        col_tan = ach_gaba_broad["columnar__tangential"]
        total = sum(ach_gaba_broad.values())
        self.assertEqual(total, 554)
        self.assertGreaterEqual(col_tan / total, 0.99)

    def test_strict_directional_chemical_polarity(self):
        """Verify 100% directional polarity: all Columnar-Tangential ACh-GABA loops have Columnar=ACh and Tangential=GABA."""
        pol = self.anatomy["ach_gaba_polarity"]
        self.assertIn("col_ach__tan_gaba", pol)
        self.assertEqual(pol["col_ach__tan_gaba"], 551)
        self.assertNotIn("col_gaba__tan_ach", pol)

    def test_layer_concentration_in_layers_4_and_5(self):
        """Verify that over 98% (99.1%) of ACh <-> GABA reciprocal loops reside in Layers 4 and 5."""
        layers = self.anatomy["ach_gaba_layers"]
        l4 = layers.get("Layer_4", 0)
        l5 = layers.get("Layer_5", 0)
        total = sum(layers.values())
        self.assertEqual(total, 554)
        pct_4_5 = (l4 + l5) / total
        self.assertGreaterEqual(pct_4_5, 0.98, f"Layers 4&5 percentage {pct_4_5*100:.1f}% < 98%")
        self.assertLessEqual(layers.get("Unassigned_Layer", 0), 5)

    def test_fb5i2_vdeltaf_microcircuit_identification(self):
        """Verify that FB5I2 <-> vDeltaF is correctly identified with 29 dyads, eliminating Unknown."""
        top_pairs = self.anatomy["ach_gaba_top_cell_pairs"]
        self.assertIn("FB5I2 <-> vDeltaF", top_pairs)
        self.assertEqual(top_pairs["FB5I2 <-> vDeltaF"], 29)
        self.assertNotIn("Unknown <-> vDeltaF", top_pairs)


class TestContinuousDegreeKNNInvariants(unittest.TestCase):
    """Verifies continuous degree k-NN micro-stratification and MCMC partition invariants."""

    @classmethod
    def setUpClass(cls):
        with open(FB_KNN_JSON) as f:
            cls.knn_data = json.load(f)

    def test_fb_knn_significance(self):
        """Verify that FB ACh <-> GABA enrichment remains >= 2.0x and p < 0.001 under k=16 and k=8 micro-strata."""
        fb_k16 = self.knn_data["fb_continuous_knn"]["fb_k16"]
        fb_k8 = self.knn_data["fb_continuous_knn"]["fb_k8"]

        self.assertGreaterEqual(fb_k16["enrichment_ratio"], 2.0)
        self.assertGreaterEqual(fb_k8["enrichment_ratio"], 2.0)
        self.assertLessEqual(fb_k16["empirical_p_value"], 0.001)
        self.assertLessEqual(fb_k8["empirical_p_value"], 0.001)

    def test_eb_knn_option_a_persistence(self):
        """Verify that EB GABA <-> GABA excess remains >= 1.15x and p < 0.001 under k=16 and k=8 micro-strata."""
        eb_k16 = self.knn_data["eb_continuous_knn"]["eb_k16"]
        eb_k8 = self.knn_data["eb_continuous_knn"]["eb_k8"]

        self.assertGreaterEqual(eb_k16["enrichment_ratio"], 1.15)
        self.assertGreaterEqual(eb_k8["enrichment_ratio"], 1.15)
        self.assertLessEqual(eb_k16["empirical_p_value"], 0.001)
        self.assertLessEqual(eb_k8["empirical_p_value"], 0.001)

    def test_continuous_mcmc_benchmark(self):
        """Verify that Continuous Metropolis-Hastings MCMC degree penalty preserves statistical significance."""
        fb_mcmc = self.knn_data["fb_continuous_mcmc"]["fb_mcmc_sigma020"]
        eb_mcmc = self.knn_data["eb_continuous_knn"]["eb_mcmc_sigma020"]

        self.assertGreaterEqual(fb_mcmc["enrichment_ratio"], 1.15)
        self.assertGreater(fb_mcmc["z_score"], 2.0)
        self.assertLess(fb_mcmc["empirical_p_value"], 0.05)

        self.assertGreaterEqual(eb_mcmc["enrichment_ratio"], 1.25)
        self.assertGreater(eb_mcmc["z_score"], 3.0)
        self.assertLess(eb_mcmc["empirical_p_value"], 0.05)


class TestVectorSteeringDynamicsInvariants(unittest.TestCase):
    """Verifies rate-based dynamical simulation of FB Layers 4 & 5 divisive gain control."""

    @classmethod
    def setUpClass(cls):
        with open(FB_SIM_JSON) as f:
            cls.sim_data = json.load(f)

    def test_divisive_gain_control_suppression(self):
        """Verify that intact reciprocal feedback provides >= 5.0x peak firing rate suppression under high drive."""
        summary = self.sim_data["summary"]
        self.assertGreaterEqual(summary["peak_suppression_ratio_at_max_drive"], 5.0)

    def test_bump_sharpness_contrast_preservation(self):
        """Verify that intact feedback preserves sharp tuning (FWHM <= 100 deg) while ablated feedback broadens."""
        summary = self.sim_data["summary"]
        intact_range = summary["intact_fwhm_stability_range_deg"]
        ablated_range = summary["ablated_fwhm_stability_range_deg"]

        self.assertLessEqual(intact_range[1], 100.0)
        self.assertGreater(ablated_range[0], intact_range[1])

    def test_steering_vector_decoding_precision(self):
        """Verify that mean steering decoding error remains < 2.0 degrees across all velocity/drive levels."""
        summary = self.sim_data["summary"]
        self.assertLess(summary["mean_decoding_error_intact_deg"], 2.0)


if __name__ == "__main__":
    unittest.main()
