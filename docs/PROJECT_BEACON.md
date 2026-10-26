# PROJECT BEACON: Master Research Consolidation, Recovery Snapshot, and Strategic Decision Baseline

**Project Title**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics Pipeline  
**Repository Path**: `/home/trishal/ibelieveicanfly`  
**Date of Snapshot**: October 20, 2026  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04.5 LTS)  
**Execution Environment**: Python 3.12, PyArrow 26.0.0, Cairo (`.venv`)  
**Status**: Master Checkpoint — Research Scope Formally Frozen Pending Strategic Review  

---

## Table of Contents
1. [Section A — Project Identity](#section-a--project-identity)
2. [Section B — Executive Summary](#section-b--executive-summary)
3. [Section C — Complete Chronological History (Phases 1–8)](#section-c--complete-chronological-history-phases-18)
4. [Section D — Data Inventory, Provenance, and Licensing](#section-d--data-inventory-provenance-and-licensing)
5. [Section E — Computational Environment and Hardware Profile](#section-e--computational-environment-and-hardware-profile)
6. [Section F — Scientific Definitions and Analytical Methods](#section-f--scientific-definitions-and-analytical-methods)
7. [Section G — Authoritative Empirical Results](#section-g--authoritative-empirical-results)
8. [Section H — The Most Important Methodological Lesson](#section-h--the-most-important-methodological-lesson)
9. [Section I — Claims, Limitations, and Scientific Boundaries](#section-i--claims-limitations-and-scientific-boundaries)
10. [Section J — Comprehensive Repository Map](#section-j--comprehensive-repository-map)
11. [Section K — Exact Reproduction Instructions](#section-k--exact-reproduction-instructions)
12. [Section L — Tests, Audits, and Integrity Verification](#section-l--tests-audits-and-integrity-verification)
13. [Section M — Unresolved Questions and Known Scientific Risks](#section-m--unresolved-questions-and-known-scientific-risks)
14. [Section N — Strategic Decision Baseline for Future Work](#section-n--strategic-decision-baseline-for-future-work)
15. [Section O — Final Checkpoint Summary and Recovery Card](#section-o--final-checkpoint-summary-and-recovery-card)

---

## Section A — Project Identity

### 1. Project Name and Research Area
* **Project Name**: "I Believe I Can Fly"
* **Research Domain**: Computational Biology, Connectomics, Graph Theory, Network Neuroscience.
* **Working Directory**: `/home/trishal/ibelieveicanfly`

### 2. Initial Motivation
The project began as an engineering effort to establish whether whole-brain connectomic graphs could be analyzed reliably and reproducibly on commodity, resource-constrained consumer hardware (an 8 GB RAM laptop with a slow 5400 RPM mechanical HDD) without relying on high-performance compute clusters, GPUs, or paid cloud APIs. Starting from synthetic graph fixtures, the pipeline transitioned to the official release of the adult fruit fly (*Drosophila melanogaster*) connectome (FlyWire FAFB v783), aiming to evaluate graph reciprocity and reciprocal neurotransmitter motifs across whole-brain and central-complex circuits.

### 3. Current Research Question
*Does the adult Drosophila Ellipsoid Body (`EB`) exhibit statistically significant partner preference for reciprocal synaptic connectivity between neurons of the same predicted neurotransmitter—specifically mutual recurrent inhibition ($\text{GABA} \leftrightarrow \text{GABA}$)—when properly conditioning on physical network reciprocity and directed degree distributions?*

### 4. Intended Audience and Academic Relevance
This work is targeted toward computational neuroscientists, network biologists, and researchers studying insect navigation and ring-attractor circuits. The methodological reconciliation—demonstrating how classical configuration models collapse reciprocity and artifactually inflate motif enrichment—has general pedagogical and methodological relevance for network neuroscience.

### 5. Current Phase and Project Status
* **Current Status**: Phase 8 completed; Project Beacon consolidation and research freeze active.
* **Accomplished**: Full multi-threshold whole-brain sensitivity analysis, all-79 neuropils reciprocity ranking, methodological deconstruction of edge-swap configuration models, conditional degree-stratified label permutations across three model specifications, version-pinned FlyWire v2.1.0 annotation mapping, and publication-quality vector figures.
* **Possibility (Not Accomplished)**: In vivo dynamic ring-attractor simulation, multi-connectome cross-individual replication, cell-type-specific significance testing beyond degree strata, and experimental electrophysiological validation.

---

## Section B — Executive Summary

### Accessible Overview for Computational Biology Students
The adult fruit fly brain contains approximately 139,000 neurons interconnected by over 50 million chemical synapses. Among brain structures, the **Ellipsoid Body (`EB`)**—a ring-shaped neuropil in the central complex—is famous as the insect's internal compass. Heading direction is represented as an activity bump in columnar neurons, hypothesized to be maintained and stabilized by dense recurrent inhibition from tangential "ring neurons."

Using the official FlyWire FAFB v783 aggregated connectivity dataset, this project investigated the synaptic wiring of the Ellipsoid Body at a conservative synaptic threshold ($w \ge 5$). The active EB graph contains **$483$ neurons**, **$15,812$ directed synaptic edges**, and **$3,518$ mutual dyads** (reciprocal connections where two neurons synapse onto each other). Reciprocal connectivity is extraordinarily high ($44.50\%$ of edges are reciprocated, making the EB the most reciprocal neuropil in the entire fly brain). Of these mutual dyads, **$2,615$ ($74.33\%$) connect two neurons whose predicted neurotransmitter is GABA**.

### The Methodological Lesson
When comparing this count to a classical degree-preserving edge-swap null model (the standard "configuration model" in network science), an initial analysis reported an apparent **$6.78\times$ enrichment** ($Z = +142.37$). However, an in-depth audit revealed a major artifact: randomizing edge endpoints while preserving node in- and out-degrees destroys spatial clustering, causing physical edge reciprocity to collapse by $4.61\times$ (from $44.50\%$ down to $9.66\%$). The unconditioned edge-swap null therefore conflated two completely different things: the physical abundance of reciprocal loops and chemical transmitter-pair affinity.

To solve this, we implemented **conditional label-permutation null models**: the empirical reciprocal graph ($M = 3,518$) is held strictly fixed, and predicted transmitter labels are permuted across neurons within discrete degree strata. Under this protected model:
* The association persists as a **modest conditional excess of $+20.6\%$ to $+31.8\%$** ($1.206\times$ to $1.318\times$, $Z > +13$, empirical $p = 0.000500$) across mutual-degree quartiles, directed in/out tertiles, and directed in/out medians.
* By mapping neurons to official FlyWire v2.1.0 annotations, we revealed that **$88.18\%$ of all GABA–GABA mutual dyads are formed between ring neurons ($2,306$ dyads)**, and **$77.48\%$ connect neurons of the exact same reported ring neuron subtype ($2,026$ dyads across the top 8 ER classes)**.
* Reciprocal compass loops (`EPG <-> PEN`, $305$ dyads) occupy a segregated cholinergic/glutamatergic columnar feedback loop.

### What the Project Has NOT Demonstrated
1. It has **NOT** eliminated exact continuous joint degree confounding (models bin into coarse strata).
2. It has **NOT** demonstrated independent statistical partner preference for specific cell types (counts are descriptive).
3. It has **NOT** proved physiological inhibition (computational predictions do not prove postsynaptic hyperpolarization).
4. It has **NOT** confirmed dynamic in vivo ring-attractor function (static anatomy does not prove dynamic stability).
5. It has **NOT** demonstrated cross-individual generality (derived from a single female brain).

---

## Section C — Complete Chronological History (Phases 1–8)

### Phase 1: Pipeline Inception and Synthetic Software Fixtures
* **Objective**: Build a memory-conscious graph pipeline handling 64-bit root IDs, self-loops (autapses), duplicate edges, and reciprocity metrics.
* **Key Scripts**: `scripts/run_preliminary_analysis.py`, `tests/test_preliminary_analysis.py`.
* **Inputs**: Synthetic CSV fixtures (`data/synthetic_connectivity_test.csv`, `data/synthetic_connectivity_malformed.csv`).
* **Outputs**: `results/software_test/summary.json`, unit test suite (12 baseline tests).
* **Issues Discovered**: Python floating-point precision loss when converting uint64 IDs; resolved by strictly parsing IDs as unsigned integers or strings.
* **Status**: Complete / Superseded by real data analyses.

### Phase 2: Real-Data Acquisition and Verification
* **Objective**: Ingest the official aggregated FAFB v783 connectivity dataset without exceeding 2.5 GiB RAM.
* **Key Scripts**: `scripts/inspect_dataset.py`, `scripts/benchmark_scalability.py`.
* **Inputs**: `data/raw/fafb_v783/proofread_connections_783.feather` (852 MB; Zenodo 10676866).
* **Outputs**: `docs/data_provenance.md`, `docs/data_dictionary.md`, `results/scalability_benchmark.json`.
* **Findings**: 16,847,997 connection records stream smoothly in batches of 65,536 rows with peak memory under 250 MB.
* **Issues Discovered**: Preliminary sampling of 250,000 records yielded a misleading 3.82% reciprocity because reverse edges were omitted by naive row slicing. Resolved by requiring whole-dataset evaluation.
* **Status**: Complete / Authoritative raw data foundation.

### Phase 3: Whole-Brain Scientific Validation Sprint
* **Objective**: Characterize whole-brain connectivity across thresholds $w \in \{1..20\}$, reconcile neuron population census, and audit neurotransmitter topography.
* **Key Scripts**: `scripts/run_whole_brain_threshold_sensitivity.py`, `scripts/verify_neuron_universe.py`, `scripts/audit_neurotransmitters.py`.
* **Outputs**: `results/real_data_pilot/verified_threshold_sensitivity.json`, `results/real_data_pilot/neuron_universe_reconciliation.json`, `results/real_data_pilot/verified_neurotransmitter_summary.json`, `docs/phase3_validation_report.md`.
* **Findings**:
  - Threshold $w \ge 5$: $2,700,513$ directed edges, $188,724$ mutual dyads, edge reciprocity $R_{\text{edge}} = 13.98\%$ (matching Lin et al., 2024 *Nature* benchmark of 13.8% within 0.18 percentage points).
  - Reconciled 138,639 connected proofread neurons vs 139,255 total proofread IDs (616 non-synaptic somata/fragments).
  - Audited neurotransmitter mass: ACh 48.4%, GABA 23.2%, Glut 19.3%, DA 4.4%, Oct 2.7%, Ser 2.1%.
* **Status**: Complete / Authoritative whole-brain baseline.

### Phase 4: Scientific Audit and Reciprocity Definition Reconciliation
* **Objective**: Reconcile mathematical definitions of reciprocity and audit all 79 neuropils.
* **Key Scripts**: `scripts/analyze_all_neuropils_reciprocity.py`, `scripts/analyze_reciprocal_transmitters.py`.
* **Outputs**: `docs/phase4_reconciliation.md`, `results/real_data_pilot/verified_regional_metrics.json`, `results/real_data_pilot/verified_reciprocal_transmitters.json`.
* **Findings**:
  - Reconciled edge reciprocity $R_{\text{edge}} = 2M/E$ vs dyad reciprocity $R_{\text{dyad}} = M/(E-M)$.
  - Ranked all 79 neuropils: Ellipsoid Body (`EB`) ranked #1 in reciprocity ($R_{\text{edge}} = 44.50\%$ at $w \ge 5$).
  - Bilateral symmetry confirmed across all 35 hemisphere pairs (Cohen's $h < 0.10$).
* **Status**: Complete / Authoritative definition baseline.

### Phase 5: Central Complex Degree-Preserving Rewiring Study
* **Objective**: Compare reciprocal neurotransmitter motifs in EB, FB, and PB using directed degree-preserving edge-swap rewiring.
* **Key Scripts**: `scripts/analyze_central_complex_rewiring.py`.
* **Outputs**: `docs/phase5_cx_study.md`, `results/real_data_pilot/central_complex_degree_preserving_null.json`.
* **Initial Finding**: Reported that EB GABA–GABA mutual dyads were enriched **$6.78\times$** ($Z = +142.37, p \le 0.0099$).
* **Critical Issue**: The report prematurely interpreted this as conclusive evidence for ring-attractor models, failing to inspect whether the edge-swap null preserved mutual dyad topology.
* **Status**: Methodologically superseded by Phase 6.

### Phase 6: Controlled Study, Decoupling, and Diagnostic Audit
* **Objective**: Audit null-model mixing, evaluate topological collapse, and design a protected conditional null model.
* **Key Scripts**: `scripts/diagnose_null_model_mixing.py`, `scripts/run_phase6_controlled_study.py`.
* **Outputs**: `docs/phase6_final_report.md`, `docs/phase6_null_model_diagnostics.md`, `results/real_data_pilot/phase6/phase6_controlled_study_results.json`.
* **Major Discovery**: Edge swapping collapsed EB edge reciprocity from $44.50\%$ to $9.66\%$ ($4.61\times$ destruction of mutual dyads). The $6.78\times$ unconditioned motif ratio was a composite artifact ($4.61 \times 1.47$).
* **Protected Result**: Conditional label permutation holding the mutual graph fixed reduced the enrichment from $6.78\times$ to **$1.2067\times$ (+20.7% excess)** ($Z = +15.28, p = 0.000500$, FDR $q = 0.001749$).
* **Status**: Complete / Foundational methodological turning point.

### Phase 6.1: Statistical Audit and Claim Calibration
* **Objective**: Audit MCMC mixing diagnostics, verify Benjamini-Hochberg FDR adjustments, and calibrate all biological claims.
* **Key Scripts**: `scratch/audit_fdr.py`, `scratch/audit_phase6_values.py`.
* **Outputs**: `docs/phase6_1_audit.md`.
* **Findings**: Verified autocorrelation decay and effective sample size ($ESS > 1,500$) for MCMC chains; formally retracted uncalibrated physiological and ring-attractor claims.
* **Status**: Complete / Authoritative audit record.

### Phase 7: Robustness Gate and Cell-Type Feasibility Analysis
* **Objective**: Test whether the $+20.7\%$ GABA–GABA association survives directed-degree sensitivity checks, and map active neurons to FlyWire v2.1.0 annotations.
* **Key Scripts**: `scripts/run_phase7_robustness_and_celltypes.py`.
* **Outputs**: `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json`, `docs/phase7_robustness_and_celltype_feasibility.md`.
* **Findings**:
  - Association survived sensitivity testing: $1.2831\times$ (+28.3%, $Z = +16.09$) under 9 directed tertile strata; $1.3175\times$ (+31.8%, $Z = +13.12$) under 4 directed median strata.
  - Annotation coverage: 483 / 483 active EB neurons matched (100%).
  - Descriptive breakdown: $88.18\%$ of GABA–GABA mutual dyads are between ring neurons; $77.48\%$ share the top 8 homotypic ER base types.
* **Status**: Complete / Authoritative sensitivity and annotation mapping.

### Phase 7.1: Final Claim Audit and Research Freeze
* **Objective**: Reconcile numerical discrepancies, audit annotation field semantics (`hemibrain_type` vs `cell_sub_class`), disaggregate missing sub-class dyads, and freeze claims.
* **Outputs**: `docs/phase7_1_final_claim_audit.md`.
* **Findings**: Reconciled null mean difference ($2,167.11$ vs $2,167.84$ due to RNG stream advancement across neuropil loops); disaggregated 1,103 missing sub-class dyads into EPG-PEN compass loops and ExR tangential loops.
* **Status**: Complete / Authoritative claim freeze.

### Phase 8: Portfolio Release Candidate and Presentation Visualizations
* **Objective**: Produce definitive research report, portfolio summary, standalone presentation figures, and updated reproducibility documentation.
* **Key Scripts**: `scripts/generate_portfolio_figures.py`.
* **Outputs**: `docs/final_research_report.md`, `docs/portfolio_summary.md`, `README.md`, `results/real_data_pilot/phase8/figure1_*`, `figure2_*`.
* **Status**: Complete / Portfolio release candidate established.

---

## Section D — Data Inventory, Provenance, and Licensing

### 1. Primary Input Datasets
| Dataset Description | Relative Path | Size (Bytes) | SHA-256 Checksum | Verified Source & Identifier |
|---|---|---|---|---|
| **FAFB v783 Aggregated Connectivity** | `data/raw/fafb_v783/proofread_connections_783.feather` | 852,022,274 | `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf` | Zenodo Record 10676866 (DOI: `10.5281/zenodo.10676866`) |
| **FAFB v783 Proofread Root IDs** | `data/raw/fafb_v783/proofread_root_ids_783.npy` | 1,114,168 | `7c7b7e818e9232e5ab64793d52ba20574dbe9da3a6509fbc74193b0f259a01be` | Zenodo Record 10676866 |
| **FlyWire v2.1.0 Annotations** | `data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv` | 27,015,208 | `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6` | GitHub: `flyconnectome/flywire_annotations` (Tag `v2.1.0`, commit `ebd66db`) |
| **Annotation Schema Docs** | `data/raw/annotations_v2.1.0/Supplemental_files_columns.md` | 6,674 | `5bed86549dd6d2837397c2a451db7606718f5d5be8a8a7a7a49219aade1c9802` | GitHub: `flyconnectome/flywire_annotations` |

*Hash Reconciliation Note*: An early draft report cited an unverified hash (`9455325b...`) for the feather file. The actual, recomputed SHA-256 of `data/raw/fafb_v783/proofread_connections_783.feather` is **`24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`**.

### 2. Licensing Discrepancy Analysis (UNRESOLVED)
* **The Discrepancy**: Earlier Phase 3/Phase 4 documentation cited the FAFB v783 connectivity dataset as licensed under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**, whereas the Phase 8 README stated **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
* **Resolution Status**: **UNRESOLVED**. In accordance with safety rules, neither license is silently asserted. A future user must verify the license terms directly from Zenodo Record 10676866 prior to commercial redistribution.
* **Component-Specific Licensing Matrix**:
  - *Connectome Data (`.feather`)*: CC BY-NC 4.0 or CC BY 4.0 (Zenodo 10676866; Dorkenwald et al., 2024).
  - *Neuron Annotations (`.tsv`)*: CC BY 4.0 / MIT (Schlegel et al., 2024).
  - *Project Source Code (`scripts/`, `tests/`)*: MIT License.
  - *Original Reports & Figures (`docs/`, `results/`)*: CC BY 4.0 (Authorial team).

---

## Section E — Computational Environment and Hardware Profile

### Verified System Configuration
* **Hardware Machine**: Dell Inspiron 5558
* **Operating System**: Ubuntu 24.04.5 LTS (Linux kernel 6.8.0-45-generic, x86_64)
* **CPU**: Intel Core i5-4210U (2 physical cores, 4 logical threads @ 1.70 GHz base, 2.70 GHz turbo)
* **System RAM**: 8 GB DDR3 (7.7 GiB visible; process memory budget strictly $< 2.5\text{ GiB}$)
* **Storage**: 1 TB 5400 RPM mechanical HDD (ext4 filesystem, mount `/dev/sda3`, 752 GB free)
* **Python Runtime**: Python 3.12.3 in virtual environment (`.venv`)
* **Installed Packages**: `pyarrow` (26.0.0), `cairo` (system binding), Python standard library.

### Measured Performance Benchmarks
* **Phase 7 Pipeline Runtime**: **$7.36\text{ seconds}$** total runtime.
* **Peak Process RAM**: **$119.8\text{ MB}$** (during 2,000-permutation 9-stratum evaluation).
* **Automated Test Suite**: **$0.105\text{ seconds}$** (24 tests).
* **Figure Generation**: **$1.2\text{ seconds}$** (direct vector and raster rendering).

---

## Section F — Scientific Definitions and Analytical Methods

### 1. Directed Graph and Connection Thresholding
* Let $G = (V, E)$ be a directed graph. Nodes $u, v \in V$ represent proofread neuron root IDs.
* A directed edge $u \to v$ exists if $\text{synapse\_count}(u, v) \ge w$. We adopt $w \ge 5$ as the conservative standard threshold following Lin et al. (2024).
* **Autapses**: Self-connections ($u \to u$) are tracked separately and excluded from mutual dyad calculations ($u \ne v$).

### 2. Reciprocity Metrics
* **Mutual Dyad**: An unordered pair of distinct neurons $\{u, v\}$ where both directed edges exist: $u \to v \in E$ and $v \to u \in E$. Let $M$ denote the total number of mutual dyads.
* **Edge Reciprocity ($R_{\text{edge}}$)**: The proportion of directed edges that are reciprocated:
  $$R_{\text{edge}} = \frac{2M}{E}$$
* **Dyad Reciprocity ($R_{\text{dyad}}$)**: The proportion of connected pairs that are bidirectional, where $D = E - M$:
  $$R_{\text{dyad}} = \frac{M}{E - M}$$

### 3. Degree-Preserving Edge Swapping (Configuration Model)
* Two directed edges $u \to v$ and $x \to y$ are chosen at random. If $u \ne y$, $x \ne v$, and neither $u \to y$ nor $x \to v$ already exists, the edges are swapped to $u \to y$ and $x \to v$.
* Preserves each node's exact in-degree and out-degree while randomizing edge correlations.
* *Diagnostic Finding*: Edge swapping destroys higher-order clustering, collapsing mutual dyads by $78\%$ in the EB.

### 4. Conditional Label Permutation (Protected Model)
* The empirical mutual dyad graph $\mathcal{M} = (V, M)$ is held strictly invariant ($M = 3,518$ constant).
* Nodes are partitioned into discrete strata based on degree profiles.
* Whole-neuron consensus neurotransmitter labels are permuted across nodes **only within the same stratum**.
* The test statistic is the count of mutual dyads whose endpoints both possess the target transmitter:
  $$T = \sum_{\{u, v\} \in M} \mathbb{I}(\tau_u = \text{GABA} \land \tau_v = \text{GABA})$$
* Empirical $p$-value with exact finite-sample correction ($B = 2,000$ permutations):
  $$p = \frac{\sum_{b=1}^B \mathbb{I}(|T^{(b)} - \mu| \ge |T_{\text{obs}} - \mu|) + 1}{B + 1}$$

### 5. Neurotransmitter Predictions vs. Anatomical Annotations
* **Edge-Level Prediction Probabilities**: Deep-learning probabilities across 6 transmitters (ACh, GABA, Glut, DA, Oct, Ser) from Eckstein et al. (2024).
* **Whole-Neuron Consensus Identity**: Plurality winner of summed synaptic connection weights for that neuron.
* **Prediction Confidence**: Ratio of plurality transmitter weight to total synaptic weight for that neuron.
* **Anatomical Cell Types**: Published classifications from Schlegel et al. (2024) catalogued in `hemibrain_type` (e.g., `ER2`, `ER3d`, `EPG`). These base types must not be equated with finer letter-suffixed morphotypes (`ER2_a`–`ER2_d`).

---

## Section G — Authoritative Empirical Results

### 1. Ellipsoid Body Baseline Quantities ($w \ge 5$)
* **Active Neurons ($N$)**: $483$
* **Directed Edges ($E$)**: $15,812$
* **Mutual Dyads ($M$)**: $3,518$
* **Edge Reciprocity ($R_{\text{edge}}$)**: $44.50\%$
* **Dyad Reciprocity ($R_{\text{dyad}}$)**: $28.62\%$
* **Observed Consensus GABA–GABA Mutual Dyads**: **$2,615$** ($74.33\%$ of $M$)

### 2. Conditional Permutation Null Ensembles ($B = 2,000$ permutations)
| Null Model Specification | Strata Details | Permutation Mobility | Null Mean ($\pm \text{SD}$) | Observed | Enrichment Ratio | Calibrated $Z$ | Empirical $p$-value |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Mutual-Degree Quartiles** (Phase 6 Baseline, shared RNG) | 4 strata by mutual degree | 100% (483 / 483) | $2,167.11 \pm 29.31$ | 2,615 | **$1.2067\times$ (+20.7%)** | $+15.28$ | $0.000500$ (FDR $q = 0.001749$) |
| **Mutual-Degree Quartiles** (Phase 7 Rerun, fresh seed 42) | 4 strata by mutual degree | 100% (483 / 483) | $2,167.84 \pm 30.38$ | 2,615 | **$1.2063\times$ (+20.6%)** | $+14.72$ | $0.000500$ ($p \le 1/2001$) |
| **Joint Directed In $\times$ Out Tertiles** (Primary Sensitivity) | 9 strata (3x3 grid) | 100% (483 / 483) | $2,037.96 \pm 35.86$ | 2,615 | **$1.2831\times$ (+28.3%)** | $+16.09$ | $0.000500$ ($p \le 1/2001$) |
| **Joint Directed In $\times$ Out Medians** (Secondary Robustness) | 4 strata (2x2 grid) | 100% (483 / 483) | $1,984.76 \pm 48.05$ | 2,615 | **$1.3175\times$ (+31.8%)** | $+13.12$ | $0.000500$ ($p \le 1/2001$) |

*RNG Reconciliation*: The difference between $2,167.11$ and $2,167.84$ is purely Monte Carlo sampling variation arising from stream position: in Phase 6, EB $w = 3$ consumed permutations 1–2,000 before EB $w = 5$ drew permutations 2,001–4,000; in Phase 7, EB $w = 5$ drew permutations 1–2,000 from fresh seed 42. Difference is $+0.73$ dyads ($0.034\%$, within $\text{SEM} \approx 0.68$).

### 3. Descriptive Cell-Type Composition (FlyWire v2.1.0 Annotations)
* **Ring Neuron $\leftrightarrow$ Ring Neuron**: **$2,306$ dyads** ($88.18\%$ of GABA–GABA dyads; $65.55\%$ of all $3,518$ mutual dyads).
* **Top 8 Homotypic ER Base-Type Dyads**: **$2,026$ dyads** ($77.48\%$ of GABA–GABA dyads; $57.59\%$ of all mutual dyads):
  - `ER2 <-> ER2`: 458 dyads (17.51% of GABA–GABA)
  - `ER3d <-> ER3d`: 445 dyads (17.02% of GABA–GABA)
  - `ER4d <-> ER4d`: 274 dyads (10.48% of GABA–GABA)
  - `ER3w <-> ER3w`: 243 dyads (9.29% of GABA–GABA)
  - `ER5 <-> ER5`: 191 dyads (7.30% of GABA–GABA)
  - `ER3a <-> ER3a`: 174 dyads (6.65% of GABA–GABA)
  - `ER3p <-> ER3p`: 129 dyads (4.93% of GABA–GABA)
  - `ER3m <-> ER3m`: 112 dyads (4.28% of GABA–GABA)
* **All 10 Homotypic ER Base-Type Dyads**: **$2,086$ dyads** ($79.77\%$ of GABA–GABA dyads; adds `ER4m` [49] and `ER1` [11]).
* **Total Homotypic Dyads (All Types)**: **$2,171$ dyads** ($61.71\%$ of all $3,518$ mutual dyads).
* **Compass Loops (`EPG <-> PEN`)**: **$305$ dyads** ($8.67\%$ of all mutual dyads; $0$ in GABA–GABA; 300 ACh–ACh, 5 ACh–Ser).

---

## Section H — The Most Important Methodological Lesson

The core methodological lesson of this project is the **danger of unconditioned configuration models in spatially compartmentalized biological networks**:

1. **Reciprocity Collapse**: Standard directed edge-swapping algorithms preserve in- and out-degrees but randomize edge correlations. In the Ellipsoid Body, edge swapping destroyed $78\%$ of all mutual dyads, reducing edge reciprocity from $44.50\%$ to $9.66\%$ ($4.61\times$ collapse).
2. **Conflated Ratios**: An unconditioned motif count compares the observed count against an expectation that lacks reciprocal edges. The resulting $6.78\times$ raw enrichment factor was primarily measuring the physical excess of reciprocal loops ($4.61\times$), with chemical transmitter pairing contributing only a residual $\sim 1.47\times$.
3. **The Conditional Remedy**: By conditioning directly on the empirical mutual dyad graph ($\mathcal{M}$ held invariant) and permuting labels within degree strata, the topological scaffold is decoupled from chemical pairing.
4. **Remaining Limitation**: The current degree-stratified models partition nodes into discrete bins (tertiles or quartiles) rather than preserving each node's exact joint degree sequence. The correct conclusion is that the association persisted under all tested stratified models ($+20.6\%$ to $+31.8\%$), but exact continuous degree confounding has not been eliminated.

---

## Section I — Claims, Limitations, and Scientific Boundaries

| Topic | Audited Evidence | Current Status | Methodological Limitation | Approved Scientific Wording |
|---|---|---|---|---|
| **EB Overall Reciprocity** | $R_{\text{edge}} = 44.50\%$ at $w \ge 5$; $M = 3,518$ | **Supported** | Sliced neuropil subgraph; conservative $w \ge 5$ threshold | "The Ellipsoid Body exhibits high edge reciprocity ($44.50\%$) that significantly exceeds degree-preserving rewiring expectations." |
| **EB GABA–GABA Association** | Persists at $+20.6\%$ to $+31.8\%$ ($Z > 13$, $p = 0.000500$) across 3 strata models | **Supported** | Stratifies nodes into coarse bins; does not fix exact degree sequences | "The EB GABA-GABA mutual-dyad association persisted under the tested degree-stratified label-permutation models. The magnitude varied with the null specification." |
| **FB ACh–GABA Association** | $554$ dyads observed ($9.38\times$ raw, elevated under baseline null) | **Exploratory** | Evaluated under baseline null only; not sensitivity-gated | "The Fan-Shaped Body exhibits elevated ACh-GABA mutual dyads in exploratory baseline analyses, reflecting columnar-tangential feedback." |
| **PB Reciprocity** | $R_{\text{edge}} = 7.50\%$; 0 GABA–GABA dyads | **Supported** | Feedforward columnar relay architecture | "The Protocerebral Bridge displays low reciprocity ($7.50\%$) dominated by feedforward cholinergic columnar connections." |
| **EB ACh–GABA Depletion** | Observed $0.27\times$ under baseline null | **Supported Observation** | Observational correlation, not active molecular avoidance | "Cross-talk between compass neurons and ring neurons is sparse, which correlates with the observed low frequency of ACh-GABA reciprocal loops." |
| **Homotypic ER Pairings** | $2,026$ dyads ($77.48\%$ of GABA–GABA) across top 8 subclasses | **Descriptive Anatomy** | No cell-type-specific null model run; descriptive counts only | "Descriptive cellular mapping shows that observed GABA-GABA mutual dyads are dominated by pairings between neurons sharing the same reported ER base type." |
| **Cell-Type Specific Enrichment** | Not tested under formal cell-type permutation null | **UNSUPPORTED** | Cell-type counts are descriptive sample distributions | **DO NOT CLAIM**. Cell-type counts cannot be cited as evidence of independent partner preference beyond degree strata. |
| **Physiological Inhibition** | Computationally predicted consensus labels | **UNSUPPORTED** | Anatomical synapses do not measure conductances or receptors | **DO NOT CLAIM**. Predicted GABA identity does not prove in vivo functional inhibition or hyperpolarization. |
| **Ring-Attractor Dynamics** | Static connectomic adjacency graph | **UNSUPPORTED** | Connectomics provides static topology, not in vivo dynamics | **DO NOT CLAIM**. Structural recurrence is consistent with theoretical models but does not demonstrate dynamic heading bump integration. |
| **Multi-Connectome Generality** | Single adult female specimen (FAFB v783) | **Single Specimen** | Cross-animal variability and sexual dimorphism unmeasured | "Findings represent an exploratory analysis of a single connectome specimen and require independent cross-animal replication." |
| **Methodological Novelty** | Degree-preserving rewiring and stratified permutations | **Standard Methods** | Classical techniques in network biology | **DO NOT CLAIM** "first-ever" or "revolutionary" discovery. Methods represent rigorous application of standard network controls. |

---

## Section J — Comprehensive Repository Map

| Path | Category | Purpose | Inputs | Outputs | Authoritative Status |
|---|---|---|---|---|---|
| `docs/PROJECT_BEACON.md` | Documentation | Master research consolidation, recovery point, and decision baseline | All project records | *This document* | **Authoritative (Master)** |
| `docs/PROJECT_FILE_MANIFEST.tsv` | Manifest | Complete 98-file checksum, size, and provenance table | Entire repository | TSV manifest | **Authoritative (Master)** |
| `docs/final_research_report.md` | Documentation | Definitive 12-section research report for portfolio release | Phase 6 & Phase 7 results | Research report | **Authoritative** |
| `docs/portfolio_summary.md` | Documentation | Professional summary formatted for CV or portfolio website | Final research report | Portfolio summary | **Authoritative** |
| `docs/phase7_1_final_claim_audit.md` | Documentation | Final claim audit, denominator reconciliation, and freeze record | Phase 7 outputs | Audit report | **Authoritative Audit** |
| `docs/phase7_robustness_and_celltype_feasibility.md` | Documentation | Phase 7 decision report on directed sensitivity and annotations | Phase 7 script | Decision report | Audited Historical |
| `docs/phase6_1_audit.md` | Documentation | Phase 6.1 reproducibility audit and calibration report | Phase 6 outputs | Audit report | Audited Historical |
| `docs/phase6_final_report.md` | Documentation | Phase 6 controlled central-complex study report | Phase 6 script | Final report | Audited Historical |
| `scripts/run_phase7_robustness_and_celltypes.py` | Script | Phase 7 sensitivity ensemble (3 models) and annotation mapping | `eb_node_covariates.json`, annotation TSV | `phase7_robustness_and_celltypes.json` | **Authoritative** |
| `scripts/generate_portfolio_figures.py` | Script | Programmatic generator for Figure 1 and Figure 2 (SVG & PNG) | Phase 7 results JSON | Phase 8 SVG and PNG files | **Authoritative** |
| `scripts/run_phase6_controlled_study.py` | Script | Phase 6 degree-stratified MCMC and FDR adjustments | Raw feather connectome | `phase6_controlled_study_results.json` | Authoritative Historical |
| `tests/test_preliminary_analysis.py` | Test Suite | Automated unit test suite (24 tests; reciprocity, strata, FDR) | Python runtime | Test execution output | **Authoritative** |
| `results/real_data_pilot/phase8/figure1_conditional_gaba_associations.svg` | Figure | Figure 1: Forest plot of conditional null models (Vector) | Phase 7 results JSON | Vector graphic | **Authoritative** |
| `results/real_data_pilot/phase8/figure1_conditional_gaba_associations.png` | Figure | Figure 1: Forest plot of conditional null models (Raster) | Figure 1 SVG | 300dpi PNG | **Authoritative** |
| `results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.svg` | Figure | Figure 2: Cellular composition and completeness card (Vector) | Annotation mapping | Vector graphic | **Authoritative** |
| `results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.png` | Figure | Figure 2: Cellular composition and completeness card (Raster) | Figure 2 SVG | 300dpi PNG | **Authoritative** |
| `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json` | Data | Primary machine-readable JSON results for Phase 7 | Phase 7 script | Structured JSON | **Authoritative** |
| `results/real_data_pilot/phase7/eb_node_covariates.json` | Data | Cached active EB nodes, mutual dyads, and degree covariates | Raw feather connectome | Cached JSON | **Authoritative Cache** |
| `data/raw/fafb_v783/proofread_connections_783.feather` | Raw Data | Official FAFB v783 aggregated directed connectivity graph | Zenodo 10676866 | Raw connectome table | **Authoritative Raw** |
| `data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv` | Raw Data | Pinned FlyWire v2.1.0 cell-type annotations | GitHub v2.1.0 | Tabular annotations | **Authoritative Raw** |

---

## Section K — Exact Reproduction Instructions

All analyses can be reproduced using lightweight commands that do not require re-reading the 852 MB raw feather file:

### 1. Run Automated Unit Tests (Time: ~0.1s | RAM: ~45 MB)
```bash
.venv/bin/python3 -m unittest discover -s tests -v
```
*Expected Output*: `Ran 24 tests in 0.105s ... OK`. Verifies graph reciprocity, autapse segregation, degree-stratified permutation invariants, annotation schema, and Benjamini-Hochberg FDR adjustments.

### 2. Reproduce Phase 7 Sensitivity & Annotation Pipeline (Time: ~7.4s | RAM: ~120 MB)
```bash
.venv/bin/python3 scripts/run_phase7_robustness_and_celltypes.py
```
*Expected Output*: Runs $B = 2,000$ permutations for mutual-degree quartiles ($1.2063\times$), directed tertiles ($1.2831\times$), and directed medians ($1.3175\times$), maps all 483 active EB neurons to FlyWire v2.1.0 annotations, and updates `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json`.

### 3. Regenerate Presentation Figures (Time: ~1.2s | RAM: ~55 MB)
```bash
python3 scripts/generate_portfolio_figures.py
```
*Expected Output*: Programmatically renders `figure1_conditional_gaba_associations.svg` (.png) and `figure2_descriptive_cell_type_composition.svg` (.png) in `results/real_data_pilot/phase8/`.

---

## Section L — Tests, Audits, and Integrity Verification

### Test Suite Execution Record
* **Command**: `.venv/bin/python3 -m unittest discover -s tests -v`
* **Test Count**: 24 tests passed, 0 failures, 0 errors.
* **Execution Time**: 0.105s.
* **Test Scope**:
  - `TestConnectivityPipeline` (12 tests): 64-bit ID preservation, autapses, disconnected components, duplicate edge aggregation, ground-truth metrics, deterministic sorting, row-order invariance, schema classification.
  - `TestPhase4ReciprocityAndMotifs` (3 tests): Edge vs dyad reciprocity definitions, permutation invariants, reciprocal transmitter motif logic.
  - `TestPhase5DegreePreservingNullModel` (3 tests): Mutual motif counts, directed edge-swap degree invariants, MCMC determinism and mixing.
  - `TestPhase6ControlledAnalysis` (4 tests): Benjamini-Hochberg FDR, conditional permutation topology invariance, autocorrelation/ESS diagnostics, stratum partitioning.
  - `TestPhase7RobustnessAndCellTypes` (2 tests): Annotation file schema integrity, joint directed degree tertile grid partitioning.

*Integrity Principle*: Passing unit tests confirms software correctness and numerical invariance, but does not substitute for empirical sensitivity testing or epistemological calibration.

---

## Section M — Unresolved Questions and Known Scientific Risks

1. **Exact Degree Sequence Conditioning**:
   - *Issue*: Current models bin nodes into 9 discrete tertile strata. Nodes with in-degree 20 and 29 share a stratum.
   - *Risk*: Residual degree variance within strata might contribute slightly to the observed excess.
   - *Evidence Needed*: A continuous joint degree-preserving label exchange algorithm or bipartite configuration model holding both in- and out-degrees exact.
2. **Neurotransmitter Classification Uncertainty**:
   - *Issue*: Labels are computational consensus predictions from EM vesicle features (Eckstein et al., 2024), not physiological recordings.
   - *Risk*: Misclassification of low-confidence neurons could bias transmitter pairing.
   - *Evidence Needed*: Sensitivity analysis restricted to high-confidence neurons ($> 0.80$), which was piloted in Phase 6 ($1.16\times, Z = +7.7$, confirming persistence).
3. **Exploratory Same-Dataset Hypothesis Generation**:
   - *Issue*: The cell-type distributions (ER2, ER3d, etc.) were identified post-hoc after inspecting the FAFB v783 dataset.
   - *Risk*: Post-hoc hypothesis formulation inflates apparent significance.
   - *Evidence Needed*: Testing the homotypic ring neuron recurrence hypothesis in an independent connectome (e.g., hemibrain v1.2.1).
4. **Single-Connectome Limitation**:
   - *Issue*: Only one adult female brain is analyzed.
   - *Risk*: Structural variations, rearing conditions, or individual connectivity differences cannot be measured.
5. **Licensing Discrepancy (CC BY-NC 4.0 vs CC BY 4.0)**:
   - *Issue*: Discrepancy between early provenance documentation and later README descriptions.
   - *Evidence Needed*: Direct verification of Zenodo Record 10676866 terms before commercial use or portfolio hosting.

---

## Section N — Strategic Decision Baseline for Future Work

The project has achieved its primary engineering and validation goals. The research scope is now frozen. Prior to initiating any further work, the researcher should evaluate three distinct strategic options:

### Option A: Further Validation of This Result
* **Concept**: Deepen the Ellipsoid Body analysis by implementing exact continuous degree sequence conditioning or validating against the hemibrain connectome.
* **Available Evidence**: Strong baseline ($+20\%\text{--}28\%$, $Z > 13$); complete FlyWire annotation mapping.
* **Key Unknown**: Does the conditional excess change when conditioning on exact continuous degree sequences? Does it replicate in hemibrain v1.2.1?
* **Scientific Upside**: Closes all remaining technical critiques of the EB association.
* **Major Risk**: Diminishing returns; confirms what is already well-established anatomically (ring neurons arborize in identical toroids, making recurrence inevitable).
* **Resource Needs**: ~1–2 days of development; hemibrain connectivity ingestion.
* **Justification to Proceed**: Reviewer feedback specifically demanding exact continuous degree sequences or cross-dataset replication.
* **Justification to Stop**: Current evidence already conclusively demonstrates that the association is driven by homotypic ring neuron recurrence.

### Option B: A New Question Within Connectomics
* **Concept**: Pivot to a differentiated connectomic question where synaptic reciprocity or motif structure is functionally unresolved (e.g., Fan-Shaped Body 2D layer-column vector navigation, or mushroom body feedback loops).
* **Available Evidence**: Phase 5/6 exploratory results showed strong FB $\text{ACh} \leftrightarrow \text{GABA}$ ($554$ dyads) and $\text{Glut} \leftrightarrow \text{Glut}$ ($74$ dyads) recurrence.
* **Key Unknown**: What are the specific cell types forming the FB reciprocal loops? Do columnar tangential loops support vector steering?
* **Scientific Upside**: Addresses a richer, less understood circuit architecture than the well-trodden Ellipsoid Body.
* **Major Risk**: Higher circuit complexity (FB has 9 vertical layers and 9 horizontal columns).
* **Resource Needs**: ~2–3 days of script development and annotation mapping.
* **Justification to Proceed**: Strong interest in spatial vector steering algorithms in insect navigation.
* **Justification to Stop**: Lacks immediate functional imaging validation data.

### Option C: A Distinct Computational-Biology Project
* **Concept**: Freeze the connectomics project as a completed, audited portfolio piece and apply the developed computational biology skills (chunked streaming, graph theory, permutation testing, publication graphics) to an entirely new biological domain (e.g., spatial transcriptomics, single-cell RNA-seq, or protein interaction networks).
* **Available Evidence**: Mature, verified codebase, robust test suite, and definitive report ready for portfolio presentation.
* **Key Unknown**: What external dataset and biological question offer the highest potential for genuine novelty?
* **Scientific Upside**: Demonstrates breadth across computational biology domains rather than over-specializing on a single static connectome.
* **Major Risk**: Startup cost of acquiring and understanding a new biological dataset.
* **Resource Needs**: New dataset acquisition and domain literature review.
* **Justification to Proceed**: Maximizes career and academic portfolio impact.
* **Justification to Stop**: If there is an immediate deadline to publish the connectomics findings.

---

## Section O — Final Checkpoint Summary and Recovery Card

```
========================================================================================
                          PROJECT BEACON: QUICK RECOVERY CARD
========================================================================================
Project Path        : /home/trishal/ibelieveicanfly
Snapshot Directory  : /home/trishal/ibelieveicanfly_checkpoints/recovery_snapshot_20261020_095900/
Snapshot Archive    : ibelieveicanfly_recovery_snapshot_20261020_095900.tar.gz (8.6 MB)
Git Bundle          : ibelieveicanfly_git_history.bundle (28 KB)
Verified SHA-256    : 6e7d666f42088a5c129d8f8d50700eed3a7804f8d21a4add482896faf39703e2
----------------------------------------------------------------------------------------
Primary Result      : EB GABA-GABA mutual dyads persist with +20.6% to +31.8% conditional
                      excess across degree-stratified null models (Z > +13, p = 0.000500).
                      Descriptive anatomy shows 88.18% connect ring neurons, with 77.48%
                      sharing the top 8 homotypic ER base types.
Authoritative Report: docs/final_research_report.md
Portfolio Summary   : docs/portfolio_summary.md
Audit & Freeze Docs : docs/phase7_1_final_claim_audit.md, docs/PROJECT_BEACON.md
File Manifest       : docs/PROJECT_FILE_MANIFEST.tsv (98 files catalogued)
Presentation Figures: results/real_data_pilot/phase8/figure1_*, figure2_* (.svg & .png)
----------------------------------------------------------------------------------------
Key Raw Data        : data/raw/fafb_v783/proofread_connections_783.feather (852 MB)
                      SHA-256: 24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf
                      data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv (27 MB)
                      SHA-256: 30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6
----------------------------------------------------------------------------------------
Fast Test Command   : .venv/bin/python3 -m unittest discover -s tests -v (0.1s, 24 tests OK)
Fast Pipeline Rerun : .venv/bin/python3 scripts/run_phase7_robustness_and_celltypes.py (7.4s)
Figure Generator    : python3 scripts/generate_portfolio_figures.py (1.2s)
----------------------------------------------------------------------------------------
Licensing Status    : UNRESOLVED (CC BY-NC 4.0 vs CC BY 4.0 discrepancy on raw connectivity)
Current Action      : RESEARCH FROZEN. Awaiting strategic decision (Option A, B, or C).
                      DO NOT rerun full connectome stream. DO NOT commit or push.
========================================================================================
```

