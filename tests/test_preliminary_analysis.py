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
        summary = run_pipeline(test_file, max_records=0, is_software_test=True, results_dir=self.temp_path)

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
        summary = run_pipeline(test_file, max_records=0, is_software_test=True, results_dir=self.temp_path)

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
        summary = run_pipeline(test_file, max_records=0, is_software_test=True, results_dir=self.temp_path)

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
        summary = run_pipeline(test_file, max_records=0, is_software_test=True, results_dir=self.temp_path)

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

        run1 = run_pipeline(fixture_path, max_records=0, is_software_test=True, results_dir=self.temp_path / "run1")
        run2 = run_pipeline(fixture_path, max_records=0, is_software_test=True, results_dir=self.temp_path / "run2")

        # Exclude dynamic timing and memory fields
        run1["metadata"].pop("execution_time_seconds")
        run1["metadata"].pop("peak_ram_mb")
        run2["metadata"].pop("execution_time_seconds")
        run2["metadata"].pop("peak_ram_mb")

        self.assertEqual(run1, run2)


if __name__ == "__main__":
    unittest.main()
