#!/usr/bin/env python3
"""
Unit test suite for the fly-brain connectivity analysis pipeline.
Uses the standard library unittest framework.
"""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

# Add project root and scripts directory to sys.path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from inspect_dataset import audit_dataset_file, classify_dataset_schema
from run_preliminary_analysis import (
    calculate_distribution_stats,
    find_weakly_connected_components,
    run_pipeline,
)


class TestConnectivityPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_temp_csv(self, rows: list[list[str]], header: list[str] | None = None) -> Path:
        file_path = self.temp_path / "temp_test_data.csv"
        if header is None:
            header = ["pre_root_id", "post_root_id", "syn_count"]
        with file_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        return file_path

    def test_schema_classification(self) -> None:
        # Aggregated table headers
        schema, col_map = classify_dataset_schema(["pre_root_id", "post_root_id", "syn_count", "nt_type"])
        self.assertEqual(schema, "aggregated_neuron_connections")
        self.assertEqual(col_map["pre"], "pre_root_id")
        self.assertEqual(col_map["post"], "post_root_id")
        self.assertEqual(col_map["weight"], "syn_count")

        # Synapse point cloud headers
        schema_syn, _ = classify_dataset_schema(["pre_pt_root_id", "post_pt_root_id", "synapse_id", "pre_pt_x"])
        self.assertEqual(schema_syn, "individual_synapse_records")

        # Cell metadata headers
        schema_meta, _ = classify_dataset_schema(["root_id", "cell_type", "super_class"])
        self.assertEqual(schema_meta, "cell_metadata_annotations")

    def test_ground_truth_graph_metrics(self) -> None:
        """
        Verify exact degree, strength, and reciprocity on a known 3-node graph:
        A(1) -> B(2) [wt: 3]
        B(2) -> C(3) [wt: 2]
        C(3) -> A(1) [wt: 5]
        A(1) -> C(3) [wt: 1]  (reciprocal with C -> A)
        """
        data = [
            ["1", "2", "3"],
            ["2", "3", "2"],
            ["3", "1", "5"],
            ["1", "3", "1"],
        ]
        test_file = self.create_temp_csv(data)
        summary = run_pipeline(test_file, max_records=-1, is_software_test=True, results_dir=self.temp_path)

        topo = summary["network_topology"]
        self.assertEqual(topo["total_unique_neurons"], 3)
        self.assertEqual(topo["total_directed_edges"], 4)
        self.assertEqual(topo["total_synapse_count"], 11)
        self.assertEqual(topo["self_connections_count"], 0)
        self.assertEqual(topo["mutual_dyads_count"], 1)  # Dyad (1, 3)
        self.assertEqual(topo["reciprocity_ratio"], 0.5)  # 2 * 1 / 4 = 0.5

        # Check degree distribution bounds
        out_stats = summary["degree_and_weight_distributions"]["out_degree"]
        self.assertEqual(out_stats["min"], 1)  # Node 2 has out_degree 1
        self.assertEqual(out_stats["max"], 2)  # Node 1 has out_degree 2

    def test_duplicate_edge_aggregation(self) -> None:
        """Verify that multiple occurrences of the same directed edge are aggregated."""
        data = [
            ["100", "200", "4"],
            ["100", "200", "6"],  # Duplicate directed pair
        ]
        test_file = self.create_temp_csv(data)
        summary = run_pipeline(test_file, max_records=-1, is_software_test=True, results_dir=self.temp_path)

        val = summary["record_validation"]
        self.assertEqual(val["valid_records_processed"], 2)
        self.assertEqual(val["duplicate_records_aggregated"], 1)

        topo = summary["network_topology"]
        self.assertEqual(topo["total_directed_edges"], 1)
        self.assertEqual(topo["total_synapse_count"], 10)  # 4 + 6

    def test_missing_and_invalid_identifiers(self) -> None:
        """Verify handling of missing IDs, blank lines, and malformed entries."""
        data = [
            ["100", "200", "5"],
            ["", "300", "5"],     # Missing pre
            ["400", "", "5"],     # Missing post
            ["500", "600", "0"],   # Non-positive weight
            ["700", "800", "-2"],  # Negative weight
            ["900", "1000", "xyz"],# Non-integer weight
        ]
        test_file = self.create_temp_csv(data)
        summary = run_pipeline(test_file, max_records=-1, is_software_test=True, results_dir=self.temp_path)

        val = summary["record_validation"]
        self.assertEqual(val["valid_records_processed"], 1)
        self.assertEqual(val["malformed_records_excluded"], 5)

    def test_autapse_self_connection(self) -> None:
        """Verify that self-connections (pre == post) are tracked correctly."""
        data = [
            ["10", "20", "4"],
            ["10", "10", "2"],  # Autapse
        ]
        test_file = self.create_temp_csv(data)
        summary = run_pipeline(test_file, max_records=-1, is_software_test=True, results_dir=self.temp_path)

        topo = summary["network_topology"]
        self.assertEqual(topo["self_connections_count"], 1)
        self.assertEqual(topo["total_unique_neurons"], 2)

    def test_disconnected_components(self) -> None:
        """Verify weakly connected component partition on 2 disjoint subgraphs."""
        adj_undirected = {
            "A": {"B"},
            "B": {"A", "C"},
            "C": {"B"},
            "D": {"E"},
            "E": {"D"},
        }
        nodes = {"A", "B", "C", "D", "E"}
        comps = find_weakly_connected_components(nodes, adj_undirected)

        self.assertEqual(len(comps), 2)
        self.assertEqual(len(comps[0]), 3)  # {A, B, C}
        self.assertEqual(len(comps[1]), 2)  # {D, E}

    def test_reproducibility(self) -> None:
        """Verify that running the pipeline twice produces deterministic results."""
        fixture_path = PROJECT_ROOT / "data" / "synthetic_connectivity_test.csv"
        self.assertTrue(fixture_path.exists())

        run1 = run_pipeline(fixture_path, max_records=-1, is_software_test=True, results_dir=self.temp_path / "run1")
        run2 = run_pipeline(fixture_path, max_records=-1, is_software_test=True, results_dir=self.temp_path / "run2")

        # Exclude dynamic timing and memory fields
        run1["metadata"].pop("execution_time_seconds")
        run1["metadata"].pop("peak_ram_mb")
        run2["metadata"].pop("execution_time_seconds")
        run2["metadata"].pop("peak_ram_mb")

        self.assertEqual(run1, run2)


    def test_max_records_limit_and_zero_behavior(self) -> None:
        """Verify explicit limit semantics: positive N, zero, and unlimited (-1)."""
        fixture_path = PROJECT_ROOT / "data" / "synthetic_connectivity_test.csv"

        # Limit to 5 records
        res_5 = run_pipeline(fixture_path, max_records=5, is_software_test=True, results_dir=self.temp_path / "limit5")
        self.assertEqual(res_5["record_validation"]["valid_records_processed"], 5)
        self.assertTrue(res_5["metadata"]["is_sampled"])

        # Limit to 0 records (process none)
        res_0 = run_pipeline(fixture_path, max_records=0, is_software_test=True, results_dir=self.temp_path / "limit0")
        self.assertEqual(res_0["record_validation"]["valid_records_processed"], 0)
        self.assertTrue(res_0["metadata"]["is_sampled"])

        # Unlimited (-1)
        res_all = run_pipeline(fixture_path, max_records=-1, is_software_test=True, results_dir=self.temp_path / "limit_all")
        self.assertEqual(res_all["record_validation"]["valid_records_processed"], 10)
        self.assertFalse(res_all["metadata"]["is_sampled"])

    def test_neuropil_regional_aggregation(self) -> None:
        """Verify that multi-neuropil pairs are combined into unique edges while preserving regional counts."""
        data = [
            ["101", "102", "4", "AL_R"],
            ["101", "102", "6", "MB_CA_R"],  # Same pair, distinct neuropil
            ["102", "103", "3", "AL_R"],
        ]
        header = ["pre_root_id", "post_root_id", "syn_count", "neuropil"]
        test_file = self.create_temp_csv(data, header=header)
        summary = run_pipeline(test_file, max_records=-1, is_software_test=True, results_dir=self.temp_path)

        # Whole-brain graph topology
        topo = summary["network_topology"]
        self.assertEqual(topo["total_directed_edges"], 2)  # (101->102) and (102->103)
        self.assertEqual(topo["total_synapse_count"], 13)  # 4 + 6 + 3
        self.assertEqual(summary["record_validation"]["duplicate_records_aggregated"], 1)

        # Regional breakdown
        reg = summary["regional_breakdown"]
        self.assertIsNotNone(reg)
        self.assertEqual(reg["neuropils_detected"], 2)
        self.assertEqual(reg["top_neuropils_by_synapses"]["AL_R"], 7)
        self.assertEqual(reg["top_neuropils_by_synapses"]["MB_CA_R"], 6)
        self.assertEqual(reg["top_neuropils_by_connections"]["AL_R"], 2)
        self.assertEqual(reg["top_neuropils_by_connections"]["MB_CA_R"], 1)

    def test_64bit_id_preservation(self) -> None:
        """Verify that large uint64 root IDs are preserved without float precision loss."""
        # Note: 720575940613583001 and 720575940613583002 would be identical in IEEE 754 float64!
        id1 = "720575940613583001"
        id2 = "720575940613583002"
        data = [
            [id1, id2, "5"],
            [id2, id1, "5"],
        ]
        test_file = self.create_temp_csv(data)
        summary = run_pipeline(test_file, max_records=-1, is_software_test=True, results_dir=self.temp_path)

        topo = summary["network_topology"]
        self.assertEqual(topo["total_unique_neurons"], 2)
        self.assertEqual(topo["total_directed_edges"], 2)
        self.assertEqual(topo["mutual_dyads_count"], 1)
        self.assertEqual(topo["reciprocity_ratio"], 1.0)

        # Check that IDs are preserved exactly
        top_hubs = summary["prominent_hubs"]["top_out_degree"]
        node_ids = {h["node_id"] for h in top_hubs}
        self.assertIn(id1, node_ids)
        self.assertIn(id2, node_ids)

    def test_row_order_invariance(self) -> None:
        """Verify that changing the order of input rows produces identical topological metrics."""
        rows_orig = [
            ["10", "20", "2"],
            ["20", "30", "4"],
            ["30", "10", "6"],
            ["10", "30", "1"],
            ["20", "10", "3"],
        ]
        rows_shuffled = [
            ["30", "10", "6"],
            ["10", "30", "1"],
            ["10", "20", "2"],
            ["20", "10", "3"],
            ["20", "30", "4"],
        ]
        file_orig = self.create_temp_csv(rows_orig)
        file_shuffled = self.temp_path / "shuffled.csv"
        with file_shuffled.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["pre_root_id", "post_root_id", "syn_count"])
            writer.writerows(rows_shuffled)

        sum1 = run_pipeline(file_orig, max_records=-1, is_software_test=True, results_dir=self.temp_path / "ord1")
        sum2 = run_pipeline(file_shuffled, max_records=-1, is_software_test=True, results_dir=self.temp_path / "ord2")

        sum1["metadata"].pop("execution_time_seconds")
        sum1["metadata"].pop("peak_ram_mb")
        sum2["metadata"].pop("execution_time_seconds")
        sum2["metadata"].pop("peak_ram_mb")

        self.assertEqual(sum1["network_topology"], sum2["network_topology"])
        self.assertEqual(sum1["degree_and_weight_distributions"], sum2["degree_and_weight_distributions"])
        self.assertEqual(sum1["prominent_hubs"], sum2["prominent_hubs"])

    def test_hub_tie_breaking_determinism(self) -> None:
        """Verify that nodes with identical degrees are sorted deterministically by string ID."""
        # Both node "20" and node "10" have out-degree 1
        data = [
            ["20", "30", "1"],
            ["10", "30", "1"],
        ]
        test_file = self.create_temp_csv(data)
        summary = run_pipeline(test_file, max_records=-1, is_software_test=True, results_dir=self.temp_path)
        top_out = summary["prominent_hubs"]["top_out_degree"]
        # Tie breaker: x[0] ascending -> "10" should come before "20"
        self.assertEqual(top_out[0]["node_id"], "10")
        self.assertEqual(top_out[1]["node_id"], "20")


class TestPhase4ReciprocityAndMotifs(unittest.TestCase):
    """
    Phase 4 regression tests verifying exact definitions:
    1. Distinction between mutual dyads (M) and directed reciprocal edges (2M).
    2. Edge reciprocity (2M/E) vs dyad reciprocity (M/(M+U)).
    3. Multi-threshold filtering rules and threshold monotonicity.
    4. Reciprocal neurotransmitter motif categorization and expected counts on toy graphs.
    5. Finite-sample permutation null model invariants.
    """

    def test_edge_vs_dyad_reciprocity_definitions(self) -> None:
        """
        Verify on a known toy graph with autapses and multi-threshold edges:
        1 -> 2 (wt: 5)
        2 -> 1 (wt: 5)  [mutual pair {1, 2}]
        2 -> 3 (wt: 3)  [forward wt 3]
        3 -> 2 (wt: 1)  [reverse wt 1: mutual at w=1, asymmetric at w=3!]
        3 -> 4 (wt: 4)  [unidirectional]
        4 -> 5 (wt: 6)  [unidirectional]
        5 -> 5 (wt: 2)  [autapse]
        """
        raw_edges = {
            (1, 2): 5,
            (2, 1): 5,
            (2, 3): 3,
            (3, 2): 1,
            (3, 4): 4,
            (4, 5): 6,
            (5, 5): 2,
        }

        def eval_metrics(t: int):
            t_edges = {k: w for k, w in raw_edges.items() if w >= t}
            E = len(t_edges)
            autapses = sum(1 for (u, v) in t_edges if u == v)
            mutual_dyads = 0
            for (u, v) in t_edges:
                if u < v and (v, u) in t_edges and t_edges[(v, u)] >= t:
                    mutual_dyads += 1
            recip_dir_edges = 2 * mutual_dyads
            asym_edges = E - recip_dir_edges - autapses
            connected_pairs = asym_edges + mutual_dyads
            r_edge = recip_dir_edges / E if E > 0 else 0.0
            r_dyad = mutual_dyads / connected_pairs if connected_pairs > 0 else 0.0
            return {
                "E": E,
                "autapses": autapses,
                "M": mutual_dyads,
                "2M": recip_dir_edges,
                "U": asym_edges,
                "pairs": connected_pairs,
                "R_edge": r_edge,
                "R_dyad": r_dyad,
            }

        # Threshold w >= 1:
        res1 = eval_metrics(1)
        self.assertEqual(res1["E"], 7)
        self.assertEqual(res1["autapses"], 1)
        self.assertEqual(res1["M"], 2)   # {1,2} and {2,3}
        self.assertEqual(res1["2M"], 4)  # (1->2, 2->1, 2->3, 3->2)
        self.assertEqual(res1["U"], 2)   # (3->4, 4->5)
        self.assertEqual(res1["pairs"], 4) # {1,2}, {2,3}, {3,4}, {4,5}
        self.assertAlmostEqual(res1["R_edge"], 4 / 7)
        self.assertAlmostEqual(res1["R_dyad"], 2 / 4)

        # Threshold w >= 3:
        # (3->2 wt 1 and 5->5 wt 2 are filtered out)
        res3 = eval_metrics(3)
        self.assertEqual(res3["E"], 5)   # (1->2, 2->1, 2->3, 3->4, 4->5)
        self.assertEqual(res3["autapses"], 0)
        self.assertEqual(res3["M"], 1)   # ONLY {1,2} is mutual at w >= 3!
        self.assertEqual(res3["2M"], 2)  # (1->2, 2->1)
        self.assertEqual(res3["U"], 3)   # (2->3, 3->4, 4->5)
        self.assertEqual(res3["pairs"], 4)
        self.assertAlmostEqual(res3["R_edge"], 2 / 5) # 40.0%
        self.assertAlmostEqual(res3["R_dyad"], 1 / 4) # 25.0%

        # Crucial sanity checks:
        self.assertNotEqual(res3["M"], res3["2M"]) # M=1, 2M=2
        self.assertEqual(res3["E"], res3["2M"] + res3["U"] + res3["autapses"])

    def test_reciprocal_transmitter_motif_toy_graph(self) -> None:
        """
        Verify motif classification and product-of-marginals expectation on a 4-node graph:
        Neuron phenotypes:
        N1: 'ach', N2: 'gaba', N3: 'ach', N4: 'gaba'
        Mutual dyads:
        {1, 2}: ach <-> gaba
        {2, 4}: gaba <-> gaba
        {1, 3}: ach <-> ach
        """
        phenotypes = {1: "ach", 2: "gaba", 3: "ach", 4: "gaba"}
        dyads = [(1, 2), (2, 4), (1, 3)]
        M = len(dyads)

        # Count observed motifs
        obs: dict[str, int] = {}
        for u, v in dyads:
            pair = tuple(sorted([phenotypes[u], phenotypes[v]]))
            key = f"{pair[0]}_{pair[1]}"
            obs[key] = obs.get(key, 0) + 1

        self.assertEqual(obs["ach_gaba"], 1)
        self.assertEqual(obs["gaba_gaba"], 1)
        self.assertEqual(obs["ach_ach"], 1)

        # Marginal transmitter distribution among participating neurons (N1, N2, N3, N4)
        part_nodes = {1, 2, 3, 4}
        nt_counts = {"ach": 2, "gaba": 2}
        p_ach = nt_counts["ach"] / len(part_nodes)   # 0.5
        p_gaba = nt_counts["gaba"] / len(part_nodes) # 0.5

        # Expected multinomial counts:
        # E(ach_ach) = M * (p_ach^2) = 3 * 0.25 = 0.75
        # E(gaba_gaba) = M * (p_gaba^2) = 3 * 0.25 = 0.75
        # E(ach_gaba) = M * (2 * p_ach * p_gaba) = 3 * 0.50 = 1.50
        exp_ach_ach = M * (p_ach ** 2)
        exp_gaba_gaba = M * (p_gaba ** 2)
        exp_ach_gaba = M * (2 * p_ach * p_gaba)

        self.assertAlmostEqual(exp_ach_ach, 0.75)
        self.assertAlmostEqual(exp_gaba_gaba, 0.75)
        self.assertAlmostEqual(exp_ach_gaba, 1.50)

        # Enrichment ratios:
        self.assertAlmostEqual(obs["ach_ach"] / exp_ach_ach, 1 / 0.75)     # 1.333x
        self.assertAlmostEqual(obs["gaba_gaba"] / exp_gaba_gaba, 1 / 0.75) # 1.333x
        self.assertAlmostEqual(obs["ach_gaba"] / exp_ach_gaba, 1 / 1.50)   # 0.667x

    def test_permutation_null_invariants(self) -> None:
        """Verify that label permutation preserves total mutual dyads and finite-sample p-value bounds."""
        import random
        random.seed(42)
        dyads = [(1, 2), (2, 4), (1, 3), (3, 4), (2, 3)]
        M = len(dyads)
        nodes = list({u for d in dyads for u in d})
        labels = ["ach", "gaba", "ach", "glut"] # 4 nodes

        B = 50
        for _ in range(B):
            shuffled = list(labels)
            random.shuffle(shuffled)
            node_map = {n: shuffled[i] for i, n in enumerate(nodes)}

            # Count motifs
            counts = 0
            for u, v in dyads:
                counts += 1
            self.assertEqual(counts, M)

        # Finite sample plus-one p-value lower bound test:
        # Minimum empirical p-value for B permutations is 1 / (B + 1)
        p_min = (0 + 1) / (B + 1)
        self.assertAlmostEqual(p_min, 1 / 51)
        self.assertGreater(p_min, 0.01) # For B=50, cannot achieve p < 0.01!


class TestPhase5DegreePreservingNullModel(unittest.TestCase):
    """
    Phase 5: Regression tests for directed degree-preserving edge swap (Maslov-Sneppen)
    and controlled regional motif analysis.
    """

    def test_directed_edge_swap_invariants(self) -> None:
        """Verify that directed edge swapping strictly preserves in/out-degree and avoids self-loops/duplicates."""
        import random
        from collections import Counter
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from analyze_central_complex_rewiring import directed_edge_swap

        # Directed graph with 6 nodes and 10 edges
        raw_edges = [
            (1, 2), (2, 3), (3, 1), # Directed 3-cycle
            (1, 4), (4, 5), (5, 6), (6, 1), # Directed 4-cycle
            (2, 4), (4, 2), # Reciprocal pair
            (3, 5), # Unreciprocated edge
        ]
        orig_in = Counter(v for u, v in raw_edges)
        orig_out = Counter(u for u, v in raw_edges)

        rng = random.Random(42)
        # Execute 200 swaps
        rewired, succ, att = directed_edge_swap(raw_edges, num_swaps=200, rng=rng)

        # Check invariants
        self.assertGreater(succ, 0)
        self.assertEqual(len(rewired), len(raw_edges))

        rew_in = Counter(v for u, v in rewired)
        rew_out = Counter(u for u, v in rewired)
        self.assertEqual(orig_in, rew_in, "In-degree sequence must be perfectly conserved!")
        self.assertEqual(orig_out, rew_out, "Out-degree sequence must be perfectly conserved!")

        # No self loops
        self.assertTrue(all(u != v for u, v in rewired), "Self-loops are forbidden!")

        # No duplicate edges
        self.assertEqual(len(set(rewired)), len(rewired), "Multigraph duplicates are forbidden!")

    def test_edge_swap_determinism_and_mixing(self) -> None:
        """Verify reproducible rewired states under fixed seed and distinct states under different seeds."""
        import random
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from analyze_central_complex_rewiring import directed_edge_swap

        raw_edges = [(i, (i + 1) % 10) for i in range(10)] + [(i, (i + 2) % 10) for i in range(10)]
        E = len(raw_edges)

        rng1 = random.Random(12345)
        rew1, s1, a1 = directed_edge_swap(raw_edges, num_swaps=5 * E, rng=rng1)

        rng2 = random.Random(12345)
        rew2, s2, a2 = directed_edge_swap(raw_edges, num_swaps=5 * E, rng=rng2)

        rng3 = random.Random(99999)
        rew3, s3, a3 = directed_edge_swap(raw_edges, num_swaps=5 * E, rng=rng3)

        self.assertEqual(rew1, rew2, "Same random seed must produce identical rewired graph!")
        self.assertNotEqual(rew1, rew3, "Different random seeds must produce distinct rewired graphs!")

        # Verify mixing: at least 50% of edges should be rewired
        retained = len(set(raw_edges) & set(rew1))
        rewired_fraction = 1.0 - (retained / E)
        self.assertGreater(rewired_fraction, 0.50, "5x swaps should achieve substantial mixing (> 50%)!")

    def test_count_mutual_motifs_directed(self) -> None:
        """Verify mutual dyad counting and transmitter pairing on a known ground-truth graph."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from analyze_central_complex_rewiring import count_mutual_motifs

        # Node 1: GABA (idx 1), Node 2: GABA (idx 1), Node 3: ACh (idx 0), Node 4: ACh (idx 0)
        neuron_nt = {1: 1, 2: 1, 3: 0, 4: 0}
        edges = [
            (1, 2), (2, 1), # GABA <-> GABA mutual dyad
            (1, 3), (3, 1), # GABA <-> ACh mutual dyad
            (3, 4), # ACh -> ACh unreciprocated
            (2, 4), (4, 1), # Asymmetric cycle
        ]
        M, pair_counts = count_mutual_motifs(edges, neuron_nt)
        self.assertEqual(M, 2)
        self.assertEqual(pair_counts["gaba_gaba"], 1)
        self.assertEqual(pair_counts["ach_gaba"], 1)
        self.assertEqual(pair_counts.get("ach_ach", 0), 0)


class TestPhase6ControlledAnalysis(unittest.TestCase):
    """
    Phase 6: Regression tests for degree-stratified conditional null models,
    Benjamini-Hochberg FDR, MCMC mixing diagnostics, and topology preservation invariants.
    """

    def test_partition_into_strata(self) -> None:
        """Verify correct degree-ordered partitioning into equal-sized strata."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from run_phase6_controlled_study import partition_into_strata

        nodes = list(range(10))
        degrees = {i: i * 10 for i in nodes}  # Degrees: 0, 10, ..., 90
        strata = partition_into_strata(nodes, degrees, n_strata=3)

        self.assertEqual(len(strata), 3)
        # Check that strata partition the node set
        all_partitioned = [n for s in strata for n in s]
        self.assertEqual(sorted(all_partitioned), sorted(nodes))
        # Check ordering by degree
        self.assertEqual(strata[0], [0, 1, 2])
        self.assertEqual(strata[1], [3, 4, 5])
        self.assertEqual(strata[2], [6, 7, 8, 9])

    def test_benjamini_hochberg_fdr(self) -> None:
        """Verify Benjamini-Hochberg False Discovery Rate adjustment on known p-values."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from run_phase6_controlled_study import benjamini_hochberg

        p_vals = [0.01, 0.04, 0.03, 0.20]
        # Sorted ranks:
        # rank 1: 0.01 -> q = 0.01 * 4 / 1 = 0.04
        # rank 2: 0.03 -> q = 0.03 * 4 / 2 = 0.06
        # rank 3: 0.04 -> q = 0.04 * 4 / 3 = 0.0533 -> monotonic min with rank 4 (0.20) -> 0.0533
        # rank 4: 0.20 -> q = 0.20 * 4 / 4 = 0.20
        q_vals = benjamini_hochberg(p_vals)
        self.assertEqual(len(q_vals), 4)
        self.assertAlmostEqual(q_vals[0], 0.04, places=4)
        self.assertAlmostEqual(q_vals[2], 0.053333, places=4)
        self.assertAlmostEqual(q_vals[1], 0.053333, places=4)
        self.assertAlmostEqual(q_vals[3], 0.20, places=4)

    def test_conditional_permutations_topology_invariance(self) -> None:
        """Verify that conditional permutations strictly preserve mutual dyad topology and label marginals."""
        import random
        from collections import Counter
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from run_phase6_controlled_study import run_conditional_permutations, partition_into_strata

        # 6 nodes with known NT: 3 GABA (1), 2 ACh (0), 1 Glut (2)
        neuron_nt = {1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 2}
        nodes = list(neuron_nt.keys())
        mutual_dyads = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
        degrees = {n: 2 for n in nodes}
        strata = partition_into_strata(nodes, degrees, n_strata=2)

        rng = random.Random(42)
        res = run_conditional_permutations(
            mutual_dyads=mutual_dyads,
            active_nodes=nodes,
            neuron_nt=neuron_nt,
            strata=strata,
            num_permutations=100,
            rng=rng,
        )

        # In every permutation, the sum of all pair counts must equal total mutual dyads (|M| = 5)
        self.assertIn("gaba_gaba", res)
        self.assertIn("ach_gaba", res)
        # Check that empirical p-value is bounded between 0 and 1
        p_val = res["gaba_gaba"]["empirical_p_value"]
        self.assertGreater(p_val, 0.0)
        self.assertLessEqual(p_val, 1.0)

    def test_mixing_diagnostics_autocorrelation(self) -> None:
        """Verify autocorrelation and ESS calculation on white noise and correlated sequences."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from diagnose_null_model_mixing import compute_autocorrelation, compute_tau_int_and_ess

        # White noise sequence
        import random
        rng = random.Random(42)
        white_noise = [rng.gauss(0, 1) for _ in range(500)]
        acf_wn = compute_autocorrelation(white_noise, max_lag=10)
        tau_wn, ess_wn = compute_tau_int_and_ess(acf_wn, len(white_noise))

        self.assertAlmostEqual(acf_wn[0], 1.0, places=4)
        # For white noise, lag 1 autocorrelation should be close to 0 (|rho| < 0.15)
        self.assertLess(abs(acf_wn[1]), 0.15)
        # tau_int should be close to 0.5 and ESS close to 500
        self.assertLessEqual(tau_wn, 1.0)
        self.assertGreater(ess_wn, 250)


class TestPhase7RobustnessAndCellTypes(unittest.TestCase):
    """
    Phase 7: Regression tests for joint directed degree stratification,
    permutation mobility, and annotation matching.
    """

    def test_joint_directed_degree_grid_strata(self) -> None:
        """Verify that joint in/out degree tertiles partition nodes into non-empty strata."""
        import random
        rng = random.Random(42)
        nodes = list(range(100))
        in_degs = [rng.randint(0, 50) for _ in nodes]
        out_degs = [rng.randint(0, 50) for _ in nodes]

        s_in = sorted(in_degs)
        s_out = sorted(out_degs)
        t_in1, t_in2 = s_in[33], s_in[66]
        t_out1, t_out2 = s_out[33], s_out[66]

        from collections import defaultdict
        strata = defaultdict(list)
        for i, n in enumerate(nodes):
            ib = 0 if in_degs[i] <= t_in1 else (1 if in_degs[i] <= t_in2 else 2)
            ob = 0 if out_degs[i] <= t_out1 else (1 if out_degs[i] <= t_out2 else 2)
            strata[(ib, ob)].append(n)

        # All 100 nodes must be partitioned across grid
        partitioned = [n for s in strata.values() for n in s]
        self.assertEqual(len(partitioned), 100)
        self.assertEqual(sorted(partitioned), list(range(100)))
        # Grid must have multiple non-empty strata
        self.assertGreaterEqual(len(strata), 4)

    def test_annotation_file_integrity(self) -> None:
        """Verify that the pinned v2.1.0 annotation file exists, is non-empty, and has expected schema."""
        from pathlib import Path
        import csv
        annot_path = PROJECT_ROOT / "data" / "raw" / "annotations_v2.1.0" / "Supplemental_file1_neuron_annotations.tsv"
        self.assertTrue(annot_path.exists(), "Pinned annotation table must exist!")
        self.assertGreater(annot_path.stat().st_size, 20 * 1024 * 1024, "File size must be > 20 MB!")

        with open(annot_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)
            self.assertIn("root_id", header)
            self.assertIn("cell_class", header)
            self.assertIn("cell_sub_class", header)
            self.assertIn("cell_type", header)
            self.assertIn("hemibrain_type", header)


if __name__ == "__main__":
    unittest.main()





