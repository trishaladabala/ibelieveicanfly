# Research Experiment Plan: Fly-Brain Connectomics Preliminary Tests

## 1. Project Overview & Scientific Context

- **Project**: "I Believe I Can Fly" — Preliminary Drosophila Connectome Network Analysis.
- **Researcher**: Undergraduate Computational Biology / Bioinformatics Trainee.
- **Hardware Platform**: Dell Inspiron 5558 (Intel Core i5-4210U, 8 GB DDR3 RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04 LTS).
- **Core Objective**: Build a robust, memory-conscious, reproducible computational pipeline to audit, validate, and compute descriptive network statistics on fly-brain connectivity data without causing swap thrashing or system instability.

---

## 2. Experimental Phases

### Phase 1: Environment & Tooling Audit (Complete)
- [x] Inspect OS, CPU, memory, and storage characteristics.
- [x] Determine available scientific Python libraries (standard library baseline confirmed).
- [x] Establish Git repository and strict `.gitignore` protection against raw datasets.
- [x] Document data provenance, licensing, and schema constraints.

### Phase 2: Software Pipeline & Synthetic Validation (Current)
- [ ] Construct a clean synthetic connectivity fixture (`data/synthetic_connectivity_test.csv`) with known topological properties (pre, post, synapse count, self-loops, malformed rows) to verify edge cases.
- [ ] Implement `scripts/inspect_dataset.py` with streaming CSV reader, memory profiling, and edge validation.
- [ ] Implement `scripts/run_preliminary_analysis.py` to compute in-degree, out-degree, weighted in/out strengths, reciprocity, self-connection rates, and weakly connected components.
- [ ] Implement `tests/test_preliminary_analysis.py` using Python's `unittest` framework to verify mathematical correctness on deterministic graph structures.
- [ ] Measure runtime and peak resident memory with `/usr/bin/time -v`.

### Phase 3: Pilot Benchmark & Real Data Acquisition Plan
- [ ] Generate comprehensive `results/pilot_report.md` detailing software test results, memory usage benchmarks, and operational limits.
- [ ] Detail the exact real dataset download needed (FlyWire v783 aggregated connections, ~60 MB compressed) and present request to user before downloading.

---

## 3. Engineering & Memory Safety Guardrails

| Constraint | Operational Parameter | Implementation Mechanism |
|---|---|---|
| **Memory Ceiling** | < 2.5 GiB additional RAM | Stream rows one-by-one via `csv.reader`. Avoid `pd.read_csv()` loading millions of rows into a contiguous DataFrame. |
| **I/O Bottleneck** | 5400 RPM mechanical HDD | Avoid repeated scans of raw disk files. Collect degree frequencies, node sets, and summary tallies in a single sequential streaming pass. |
| **Precision Guard** | 64-bit integer IDs | Store node IDs as strings or native arbitrary-precision Python `int`s; never IEEE 754 floats. |
| **Graph Semantics** | Directed, weighted multigraph | Adjacency lists represented via sparse Python dictionaries: `dict[str, dict[str, int]]`. |
| **Verification** | 100% reproducible testing | Dedicated unit tests for schema parsing, malformed handling, and graph metric computations. |
