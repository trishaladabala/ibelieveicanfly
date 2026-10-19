# "I Believe I Can Fly" — Fly-Brain Connectomics Preliminary Tests

A reproducible, memory-conscious, scientifically rigorous preliminary analysis pipeline for Drosophila connectomics data, optimized for resource-constrained development environments.

---

## 1. Project Background & System Constraints

This project establishes the computational foundation for research in computational biology, neuroscience, and graph theory using recently published fly-brain connectivity datasets (e.g. FlyWire adult whole-brain connectome, Janelia hemibrain).

### Target Hardware Environment
- **Machine**: Dell Inspiron 5558
- **OS**: Ubuntu 24.04.5 LTS (x86_64)
- **Processor**: Intel Core i5-4210U (2 cores / 4 threads @ 1.70GHz)
- **Installed Memory**: 8 GB DDR3 RAM (~2.8 GiB available at baseline, ~2 GiB swap)
- **Primary Storage**: 1 TB 5400 RPM Mechanical HDD (~752 GB free, SMART health passed)

### Engineering Constraints
- Zero reliance on dedicated GPUs or external paid cloud APIs.
- Streaming and chunked processing to keep additional RAM usage strictly below **2.5 GiB**.
- Sparse adjacency structures avoiding dense $O(V^2)$ memory allocations.
- Preservation of 64-bit integer IDs (preventing IEEE 754 precision loss).
- Pure standard-library core pipeline with zero heavy framework startup overhead on mechanical disks.

---

## 2. Directory Structure

```
ibelieveicanfly/
├── README.md                   # Project overview, architecture, and instructions
├── .gitignore                  # Protection against committing large datasets or caches
├── environment.txt             # Automated audit of system hardware, RAM, and Python runtime
│
├── data/
│   ├── README.md               # Storage rules and raw data placement instructions
│   ├── synthetic_connectivity_test.csv      # Tracked synthetic test fixture (SOFTWARE TEST ONLY)
│   └── synthetic_connectivity_malformed.csv # Corrupt fixture for testing validation guards
│
├── docs/
│   ├── data_provenance.md      # FlyWire vs Janelia provenance, licensing, and weight definitions
│   ├── data_dictionary.md      # Column schemas, 64-bit ID rules, and semantic types
│   └── experiment_plan.md      # Multiphase research roadmap and hardware guardrails
│
├── scripts/
│   ├── inspect_environment.py  # System hardware and package audit script
│   ├── inspect_dataset.py      # Streaming dataset auditor, validator, and memory profiler
│   └── run_preliminary_analysis.py # Graph metric pipeline (in/out degree, strength, reciprocity, WCC)
│
├── tests/
│   └── test_preliminary_analysis.py # Unit tests covering ground truth, duplicates, and edge cases
│
└── results/
    ├── pilot_report.md         # Comprehensive report of benchmark run, metrics, and limits
    ├── summary.json            # Machine-readable output summary of latest run
    ├── out_degree_distribution.svg     # Vector histogram of out-degree distribution
    └── synapse_weight_distribution.svg # Vector histogram of connection weights
```

---

## 3. Quickstart & Pipeline Execution

All scripts run directly with standard Python 3:

```bash
# 1. Audit system hardware and environment
python3 scripts/inspect_environment.py

# 2. Execute unit tests
python3 -m unittest discover tests

# 3. Audit dataset schema and detect anomalies
python3 scripts/inspect_dataset.py --file data/synthetic_connectivity_test.csv --max-rows 0

# 4. Run connectivity analysis pipeline with resource measurement
/usr/bin/time -v python3 scripts/run_preliminary_analysis.py --file data/synthetic_connectivity_test.csv --max-records 0
```

---

## 4. Current Pipeline Benchmark Results (Software Test)

| Metric | Result on Dell Inspiron 5558 |
|---|---|
| **Pipeline Status** | **SOFTWARE TEST PASSED (7/7 Unit Tests)** |
| **Peak Memory Consumption** | **14.12 MB** (Limit: 2.5 GiB; utilized < 1%) |
| **Execution Wall Time** | **0.16 seconds** |
| **Major Page Faults (I/O)** | **0** |
| **Swapping Occurrences** | **0** |

Detailed benchmark metrics, degree distributions, and scientific limitations are documented in [`results/pilot_report.md`](results/pilot_report.md).

---

## 5. Next Steps
- Review [`docs/data_provenance.md`](docs/data_provenance.md) for official FlyWire v783 aggregated connection files.
- Authorize download of the official sample table (50,000 edges) to begin genuine biological analysis.
