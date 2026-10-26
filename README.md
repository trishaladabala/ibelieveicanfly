# "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics Pipeline

A reproducible, memory-conscious, scientifically audited computational biology analysis pipeline for the adult fruit fly (*Drosophila melanogaster*) central complex connectome (FAFB v783) and official FlyWire version 2.1.0 annotations.

---

## 1. Project Question & Principal Result

### Research Question
Does the adult *Drosophila* Ellipsoid Body (`EB`) exhibit elevated synaptic reciprocity between neurons of the same predicted neurotransmitter—specifically mutual recurrent inhibition ($\text{GABA} \leftrightarrow \text{GABA}$)—when controlling for degree distributions and physical graph topology?

### Principal Finding
Under classical unconditioned edge-swap rewiring, topological edge reciprocity collapsed by $4.61\times$ (from $44.50\%$ to $9.66\%$), inflating raw motif ratios to an artificial $\sim 6.78\times$. When evaluated under protected conditional null models that hold the exact empirical reciprocal dyad topology ($M = 3,518$) invariant while permuting labels within degree strata, the $\text{GABA} \leftrightarrow \text{GABA}$ association persists as a **modest conditional excess of $+20.6\%$ to $+31.8\%$** ($Z > +13$, empirical $p = 0.000500$) across mutual-degree quartiles, directed in/out tertiles, and directed in/out medians.

Mapping active neurons to version-pinned FlyWire v2.1.0 annotations reveals that this conditional signal is underpinned by an anatomical substrate dominated by homotypic ring neuron recurrence: **$88.18\%$ of GABA–GABA mutual dyads connect ring neurons to ring neurons ($2,306$ dyads)**, and **$77.48\%$ connect neurons of the exact same reported ER base type ($2,026$ dyads)**. Cholinergic/glutamatergic compass loops (`EPG <-> PEN`, $305$ dyads) occupy a segregated columnar subsystem.

> **Final Approved Summary Statement**:  
> *"The EB GABA-GABA mutual-dyad association persisted under the tested degree-stratified label-permutation models. The magnitude varied with the null specification. The cell-type counts are descriptive and do not establish a new functional mechanism."*

---

## 2. Master Project Beacon & Recovery Checkpoint

This repository has completed an exhaustive scientific audit and research freeze through Phase 8. Future sessions and external researchers must start from the authoritative consolidation documents below before attempting further computations:

* **Master Project Beacon**: [`docs/PROJECT_BEACON.md`](file:///home/trishal/ibelieveicanfly/docs/PROJECT_BEACON.md) — Comprehensive 15-section project record, chronological history, methodology, results, claim boundary matrix, and strategic decision baseline (Options A, B, and C).
* **Project File Manifest**: [`docs/PROJECT_FILE_MANIFEST.tsv`](file:///home/trishal/ibelieveicanfly/docs/PROJECT_FILE_MANIFEST.tsv) — Complete 98-file catalog with verified SHA-256 hashes, byte sizes, and provenance notes.
* **Definitive Research Report**: [`docs/final_research_report.md`](file:///home/trishal/ibelieveicanfly/docs/final_research_report.md) — Authoritative 12-section research manuscript for the portfolio release candidate.
* **Portfolio & CV Summary**: [`docs/portfolio_summary.md`](file:///home/trishal/ibelieveicanfly/docs/portfolio_summary.md) — High-level summary of problem formulation, methodological findings, and technical stack.
* **Final Claim Audit & Freeze**: [`docs/phase7_1_final_claim_audit.md`](file:///home/trishal/ibelieveicanfly/docs/phase7_1_final_claim_audit.md) — Verification of denominators, annotation semantics, and banned overclaims.
* **Recovery Snapshot Archive**: Located at `/home/trishal/ibelieveicanfly_checkpoints/recovery_snapshot_20261020_095900/` (archive: `ibelieveicanfly_recovery_snapshot_20261020_095900.tar.gz`, 8.6 MB, SHA-256: `6e7d666f42088a5c129d8f8d50700eed3a7804f8d21a4add482896faf39703e2`). Accompanying README: `/home/trishal/ibelieveicanfly_checkpoints/recovery_snapshot_20261020_095900/README.md`.

> [!IMPORTANT]
> **Freeze & Safety Rule**: The Master Project Beacon is the single source of truth for resuming work. All existing results must be inspected before rerunning expensive computations. Do NOT re-download datasets or rerun full-brain MCMC pipelines unnecessarily.

---

## 3. Target Hardware & Software Requirements

### Hardware Baseline
The pipeline is designed and benchmarked for commodity laptop hardware:
- **Machine**: Dell Inspiron 5558
- **OS**: Ubuntu 24.04.5 LTS (x86_64)
- **CPU**: Intel Core i5-4210U (2 cores / 4 threads @ 1.70 GHz)
- **RAM**: 8 GB DDR3 RAM (Process memory peak $< 250\text{ MB}$; budget strictly $< 2.5\text{ GiB}$)
- **Storage**: 1 TB 5400 RPM mechanical HDD (sequential chunking; no random I/O thrashing)
- **Acceleration**: No GPU, cluster, or cloud services required.

### Software Requirements
- **Python**: Version 3.12+
- **Core Dependencies**:
  - `pyarrow` (v26.0.0; for Feather/IPC table streaming)
  - `cairo` / `pycairo` (system package for vector SVG and PNG rendering)
  - Python Standard Library (`unittest`, `csv`, `json`, `math`, `random`, `hashlib`)

---

## 4. Directory Structure

```
ibelieveicanfly/
├── README.md                               # Project overview, reproducibility, and benchmarks
├── .gitignore                              # Excludes large raw datasets, virtual environments, and caches
├── environment.txt                         # Hardware audit, RAM benchmarks, and runtime configuration
│
├── data/
│   ├── README.md                           # Raw data placement and provenance guide
│   └── raw/
│       ├── proofread_connections_783.feather # Excluded from Git: 852 MB FAFB v783 graph (Zenodo 10676866)
│       └── annotations_v2.1.0/             # Pinned FlyWire v2.1.0 annotation table (commit ebd66db)
│           ├── Supplemental_file1_neuron_annotations.tsv # 27 MB tabular cell-type annotations
│           └── Supplemental_files_columns.md # FlyWire annotation column descriptions
│
├── docs/
│   ├── final_research_report.md            # Definitive publication-grade research report
│   ├── portfolio_summary.md                # Concise project summary for CV / technical portfolio
│   ├── phase7_1_final_claim_audit.md       # Final claim audit, denominator reconciliation & freeze
│   ├── phase7_robustness_and_celltype_feasibility.md # Phase 7 decision report & directed sensitivity
│   ├── phase6_1_audit.md                   # Phase 6.1 reproducibility audit & claim calibration
│   ├── phase6_final_report.md              # Phase 6 controlled central-complex study report
│   └── data_provenance.md                  # Comprehensive Zenodo/FlyWire licensing and citations
│
├── scripts/
│   ├── run_phase7_robustness_and_celltypes.py # Phase 7 sensitivity models & annotation mapping
│   ├── run_phase6_controlled_study.py      # Phase 6 conditional MCMC & regional analysis
│   ├── generate_portfolio_figures.py       # Generates presentation-grade Figure 1 & Figure 2
│   └── inspect_dataset.py                  # Chunked streaming inspector for FAFB v783 feather
│
├── tests/
│   └── test_preliminary_analysis.py        # Automated test suite (24 tests; graph logic, null models)
│
└── results/
    └── real_data_pilot/
        ├── phase8/                         # Portfolio presentation figures
        │   ├── figure1_conditional_gaba_associations.svg (and .png)
        │   └── figure2_descriptive_cell_type_composition.svg (and .png)
        ├── phase7/                         # Phase 7 structured JSON outputs and node covariates
        │   ├── phase7_robustness_and_celltypes.json
        │   └── eb_node_covariates.json
        └── phase6/                         # Phase 6 controlled study results and FDR corrections
            └── phase6_controlled_study_results.json
```

---

## 5. Data Provenance and Versions

1. **FAFB v783 Connectivity Graph**:
   - **Endpoint**: [Zenodo record 10676866](https://zenodo.org/records/10676866)
   - **File**: `proofread_connections_783.feather` (852 MB; SHA-256: `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`)
   - **Release Date**: February 2024 (Dorkenwald et al., *Nature* 2024)
2. **FlyWire Version-Pinned Annotations**:
   - **Repository**: [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations)
   - **Release**: Tag `v2.1.0` (Git commit: `ebd66db2596fcc39c6950fb54ea3efa00f7fe8a0`)
   - **File**: `Supplemental_file1_neuron_annotations.tsv` (27 MB; SHA-256: `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6`)

---

## 6. Lightweight Reproduction Instructions

Reproduction is fast and deterministic using cached machine-readable graph structures. You do **NOT** need to re-download the 852 MB feather file or rerun lengthy MCMC chains to verify the primary findings, reports, and figures:

### Step 1: Run Automated Test Suite
```bash
.venv/bin/python3 -m unittest discover -s tests -v
```
*Expected Output*:
```text
Ran 24 tests in 0.105s

OK
```
Verifies 64-bit root ID preservation, autapse exclusion, directed reciprocity invariants, degree-stratified permutation invariants, annotation schema validity, and Benjamini-Hochberg FDR adjustments.

### Step 2: Reproduce Phase 7 Sensitivity & Annotation Mapping
```bash
.venv/bin/python3 scripts/run_phase7_robustness_and_celltypes.py
```
*Expected Output*:
- Evaluates $B = 2,000$ permutations across mutual quartiles, directed tertiles, and directed medians in $\sim 5\text{ seconds}$.
- Peak process RAM: $\sim 120\text{ MB}$.
- Outputs: `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json`.

### Step 3: Generate Presentation Figures (SVG & PNG)
```bash
python3 scripts/generate_portfolio_figures.py
```
*Expected Output*:
- Generates [Figure 1 (SVG)](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure1_conditional_gaba_associations.svg) and [Figure 1 (PNG)](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure1_conditional_gaba_associations.png).
- Generates [Figure 2 (SVG)](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.svg) and [Figure 2 (PNG)](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.png).

---

## 7. Where to Find Reports and Figures

| Resource | File Link | Description |
|---|---|---|
| **Definitive Research Report** | [`docs/final_research_report.md`](file:///home/trishal/ibelieveicanfly/docs/final_research_report.md) | Comprehensive 12-section research report |
| **Portfolio Summary** | [`docs/portfolio_summary.md`](file:///home/trishal/ibelieveicanfly/docs/portfolio_summary.md) | Professional summary for CV / web portfolio |
| **Final Claim Audit** | [`docs/phase7_1_final_claim_audit.md`](file:///home/trishal/ibelieveicanfly/docs/phase7_1_final_claim_audit.md) | Traceability, denominator audit, and freeze record |
| **Figure 1 (Vector SVG)** | [`results/real_data_pilot/phase8/figure1_conditional_gaba_associations.svg`](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure1_conditional_gaba_associations.svg) | Forest plot of conditional null models |
| **Figure 2 (Vector SVG)** | [`results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.svg`](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.svg) | Cellular composition and annotation completeness |

---

## 8. Known Methodological Limitations

1. **Single-Connectome Scope**: Derived from one adult female connectome (FAFB v783). Cross-individual and sexual variability cannot be assessed from this dataset.
2. **Computational Transmitter Predictions**: Neurotransmitter phenotypes are computationally predicted consensus classifications, not experimentally verified per-synapse conductances in vivo.
3. **Discrete Degree Stratification**: Null models group neurons into degree bins (tertiles/quartiles) rather than fixing each neuron's exact continuous in/out degree sequence.
4. **Descriptive Cell-Type Analysis**: Cell-type pair distributions are descriptive anatomy, not an independent significance test of cell-type preference.
5. **Static Circuit Anatomy**: Structural connectomics identifies physical synaptic adjacency, not continuous physiological dynamics or confirmed bump attractor stability.

---

## 9. License and Attribution

- **Project Code**: Distributed under the MIT License.
- **Connectome Dataset**: The FlyWire FAFB v783 connectivity dataset license is recorded as Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) in Zenodo metadata / early documentation, and cited as CC BY 4.0 in subsequent summaries. This discrepancy remains unresolved pending direct terms verification on Zenodo Record 10676866.
  - *Attribution*: Dorkenwald, S. et al. (2024). Neuronal wiring diagram of an adult brain. *Nature*, 634, 124–138.
- **Neuron Annotations**: FlyWire v2.1.0 annotations are distributed under Creative Commons Attribution 4.0 International (CC BY 4.0) / MIT.
  - *Attribution*: Schlegel, P. et al. (2024). Whole-brain annotation and multi-connectome cell typing of *Drosophila*. *Nature*, 634, 139–152.
- **Redistribution Notice**: Raw research data files (`.feather`) are excluded from Git repository tracking and should be obtained directly from official Zenodo / FlyWire repositories.
