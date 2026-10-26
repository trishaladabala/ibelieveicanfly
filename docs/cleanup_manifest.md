# Project Cleanup Manifest: Phase 2 Preparation

**Project**: "I Believe I Can Fly" — Drosophila Connectomics Analysis  
**Date**: 2026-10-19  
**Execution Context**: Phase 2 preparation prior to real biological data acquisition.

---

## 1. Project Structure Reorganization

To prevent any confusion between synthetic software-test results and genuine biological findings from the adult fly brain connectome, the `results/` hierarchy was partitioned into two distinct subdirectories:

1. `results/software_test/`: Dedicated strictly to synthetic test fixtures, unit verification benchmarks, and pipeline validation outputs.
2. `results/real_data_pilot/`: Dedicated strictly to incoming real biological connectome analysis (FlyWire FAFB v783), reports, and network metrics.

---

## 2. Inventory of Files

### A. Files Moved / Reorganized
| Original Path | New Path | Rationale & Safety Justification |
|---|---|---|
| `results/pilot_report.md` | `results/software_test/pilot_report.md` | Preserves the detailed software-validation report while ensuring it cannot be mistaken for biological results. |
| `results/summary.json` | `results/software_test/summary.json` | Retains synthetic baseline metrics for continuous integration and reproducibility. |
| `results/out_degree_distribution.svg` | `results/software_test/out_degree_distribution.svg` | Preserves synthetic degree distribution vector visualization. |
| `results/synapse_weight_distribution.svg` | `results/software_test/synapse_weight_distribution.svg` | Preserves synthetic connection weight vector visualization. |

### B. Files Retained (Core Components)
| File / Directory | Purpose & Retention Rationale |
|---|---|
| `README.md` | Project overview, architecture, and reproduction instructions. |
| `.gitignore` | Enforces strict exclusion of raw datasets, virtual environments, and bytecode caches. |
| `environment.txt` | Hardware and Python environment specification for Dell Inspiron 5558. |
| `data/README.md` | Policy documentation regarding raw data handling and git exclusion. |
| `data/synthetic_connectivity_test.csv` | Core synthetic test fixture used by unit tests to verify graph metrics and edge cases. |
| `data/synthetic_connectivity_malformed.csv` | Malformed test fixture used to verify schema validation and rejection guards. |
| `docs/data_provenance.md` | Scientific provenance, data types, and licensing documentation (updated in Phase 2). |
| `docs/data_dictionary.md` | Column definitions, 64-bit integer integrity rules, and validation invariants. |
| `docs/experiment_plan.md` | Multi-phase experimental roadmap and hardware safety guardrails. |
| `scripts/inspect_environment.py` | Environment auditing script. |
| `scripts/inspect_dataset.py` | Streaming dataset validator and anomaly auditor. |
| `scripts/run_preliminary_analysis.py` | Sparse directed graph metric pipeline. |
| `tests/test_preliminary_analysis.py` | 7-part automated unit test suite. |

### C. Files Deleted
- **None**: No source scripts, configuration files, or data fixtures were deleted. Python bytecode caches (`__pycache__/*.pyc`) were inspected and confirmed to be properly ignored by Git without needing destructive operations.

---

## 3. Git Hygiene and Safety Audit

- **Destructive Commands Prohibited**: `git clean -fdx`, `git reset --hard`, and recursive `rm -rf` were strictly avoided.
- **Uncommitted Changes Status**: `environment.txt` and `results/software_test/summary.json` hold minor run-to-run runtime values. No uncommitted scientific work was overwritten.
- **Raw Data Exclusion**: `.gitignore` explicitly prevents tracking of `data/raw/` and all large biological data formats (`.csv`, `.tsv`, `.parquet`, `.feather`, `.arrow`, `.h5`, `.tar*`, `.zip`).

