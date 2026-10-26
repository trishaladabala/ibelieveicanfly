# Pilot Report: Preliminary Pipeline Verification & Benchmarking

**Project**: "I Believe I Can Fly" — Fly-Brain Connectomics Preliminary Tests  
**Run Classification**: **SOFTWARE TEST**  
**Execution Timestamp**: 2026-10-19  
**Platform**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70GHz, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04 LTS)  

---

## 1. Objective

To establish, test, and benchmark a reproducible, memory-safe computational pipeline for auditing and analyzing directed, weighted neuronal connectivity graphs under strict resource constraints (peak RAM increase $< 2.5\text{ GiB}$, single-process execution on mechanical HDD).

---

## 2. Dataset & Provenance

### Local Workspace Status
At the onset of this investigation, an exhaustive inspection of `/home/trishal/ibelieveicanfly`, `~/Downloads`, and `~/projects` confirmed that **no real fly connectome datasets existed locally**.

### Data Used for This Benchmark
- **File**: `data/synthetic_connectivity_test.csv`
- **Classification**: **SOFTWARE TEST ONLY**
- **Provenance**: Synthetic fixture constructed specifically to test schema parsing, 64-bit ID preservation, autapse detection, edge aggregation, reciprocity, and component partitioning.
- **Scientific Caveat**: *These results do NOT represent real Drosophila melanogaster brain biology. They exist exclusively to verify software correctness and profile memory consumption before handling real connectomics data.*

---

## 3. Computational Methodology

1. **Streaming Ingestion**: The pipeline streams records sequentially using Python's standard `csv.reader`, avoiding bulk DataFrame loading into memory.
2. **64-Bit Integer Integrity**: Node identifiers (such as FlyWire 18-digit IDs) are maintained as arbitrary-precision strings/integers, eliminating precision loss inherent to 64-bit floats ($> 2^{53}$).
3. **Sparse Representation**: Graph connectivity is held in directed sparse adjacency dictionaries (`dict[str, dict[str, int]]`), eliminating dense $O(V^2)$ matrix allocations.
4. **Calculated Network Metrics**:
   - Directed In-Degree ($k_{in}$) and Out-Degree ($k_{out}$)
   - Weighted In-Strength ($s_{in} = \sum w_{in}$) and Out-Strength ($s_{out} = \sum w_{out}$)
   - Dyadic Reciprocity ($r = \frac{2 \times \text{mutual edges}}{\text{total edges}}$)
   - Self-Connection (autapse) frequency
   - Weakly Connected Components (WCC) via iterative Breadth-First Search (BFS)
5. **Memory & Performance Profiling**: Peak resident set size (RSS) tracked via `resource.getrusage` and validated with `/usr/bin/time -v`.

---

## 4. Exact Counts and Experimental Results

### Record Validation
- **Total Valid Records Processed**: 10
- **Malformed / Rejected Records**: 0 (Tested separately with 5 rejections on `synthetic_connectivity_malformed.csv`)
- **Duplicate Directed Edges Aggregated**: 0
- **Self-Loops (Autapses) Detected**: 1 (Node `720575940614000002` $\to$ `720575940614000002`)

### Network Topology (Software Test)
- **Total Unique Neurons**: 8
- **Total Directed Edges**: 10
- **Total Anatomical Synapses**: 75
- **Mutual Dyads**: 1 pair (`720575940614000001` $\leftrightarrow$ `720575940614000003`)
- **Reciprocity Ratio**: 0.2000
- **Weakly Connected Components**: 2
  - Largest Component: 6 neurons (75.0% coverage)
  - Secondary Component: 2 neurons (25.0% coverage)

### Degree and Weight Distributions
| Metric | Count | Min | 25th % | Median | 75th % | Max | Mean |
|---|---|---|---|---|---|---|---|
| **Out-Degree** | 8 | 0 | 1.00 | 1.00 | 2.00 | 2 | 1.25 |
| **In-Degree** | 8 | 0 | 1.00 | 1.00 | 2.00 | 2 | 1.25 |
| **Synapse Weight** | 10 | 1 | 3.25 | 6.00 | 9.50 | 20 | 7.50 |

---

## 5. Performance and Resource Consumption

Benchmarked with `/usr/bin/time -v`:
- **Elapsed Wall Clock Time**: 0.16 seconds
- **User CPU Time**: 0.11 s
- **System CPU Time**: 0.02 s
- **Peak Resident Memory (Max RSS)**: **14.12 MB** (14,464 KB)
- **Major Page Faults (I/O)**: 0
- **Swapping Activity**: 0 swaps
- **Exit Status**: 0 (Clean exit)

> [!NOTE]
> The memory footprint of 14.12 MB is over **170 times below** our hardware ceiling of 2.5 GiB, confirming that the streaming standard-library architecture imposes near-zero system overhead.

---

## 6. Limitations and Scientific Caveats

1. **No Biological Interpretation**: This pilot operated on synthetic test data. The degree distributions and reciprocity rates cannot be used to hypothesize about insect neural processing.
2. **Anatomical Count vs. Synaptic Efficacy**: When real data are loaded, synapse counts reflect physical anatomical active zones, not physiological conductances or electrical coupling.
3. **Sample Subgraph Boundary Effects**: When analyzing a subset or spatial bounding box of the brain, neurons near the perimeter suffer artificial truncation of degrees (boundary effects).

---

## 7. Reproduction Instructions

To reproduce this pipeline audit and benchmark:

```bash
# 1. Audit hardware and execution environment
python3 scripts/inspect_environment.py

# 2. Run unit tests verifying mathematical correctness
python3 -m unittest discover tests

# 3. Audit dataset schema and integrity
python3 scripts/inspect_dataset.py --file data/synthetic_connectivity_test.csv --max-rows 0

# 4. Execute preliminary connectivity analysis with memory profiling
/usr/bin/time -v python3 scripts/run_preliminary_analysis.py --file data/synthetic_connectivity_test.csv --max-records 0
```

---

## 8. Recommended Next Experiment

Now that the software pipeline, validation guards, unit tests, and memory profiling are verified, the recommended next step is:

1. **Acquire a real biological sample dataset**: Target the official **FlyWire v783 aggregated connections table** (or a 50,000-row sample from FlyWire Codex / Princeton repository, compressed $\approx 1.5\text{ MB}$).
2. **Obtain neuron metadata**: Download the cell classification table to map root IDs to anatomical classes (`central`, `sensory`, `motor`, `visual`).
3. **Execute first real connectomics pilot**: Run `run_preliminary_analysis.py` on the real 50,000-edge subset to compare biological fly degree distributions (power-law / heavy-tailed) against synthetic baselines.
