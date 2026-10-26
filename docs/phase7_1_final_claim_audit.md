# Phase 7.1: Final Claim Audit and Research Freeze

**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Date**: October 20, 2026  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04.5 LTS)  
**Execution Environment**: Project-local `.venv` (Python 3.12, PyArrow 26.0.0)  
**Status**: Research Scope Formally Frozen — Portfolio Audit Complete  

---

## 1. One-Paragraph Project Verdict

This adult *Drosophila melanogaster* connectomics investigation has rigorously evaluated synaptic reciprocity and reciprocal neurotransmitter motifs across whole-brain and central-complex circuits of the FAFB v783 connectome. The initial report of an extreme $\sim 6.78\times$ $\text{GABA} \leftrightarrow \text{GABA}$ mutual-dyad enrichment in the Ellipsoid Body (`EB`, threshold $w \ge 5$) was demonstrated to be an artifact of an unconditioned edge-swap null model that collapsed topological reciprocity by $4.61\times$. When evaluated under degree-stratified label-permutation null models holding the exact empirical mutual dyad graph fixed, the EB $\text{GABA} \leftrightarrow \text{GABA}$ mutual-dyad association persisted as a modest conditional excess ($+20.6\%$ to $+28.3\%$, $Z > +13$, empirical $p = 0.000500$) across mutual-degree quartiles, directed-degree medians, and directed-degree tertiles. Mapping active neurons to the version-pinned FlyWire v2.1.0 release annotations reveals that this association is underpinned by an anatomical substrate dominated by homotypic ring neuron pairings ($88.18\%$ of GABA–GABA mutual dyads connect ring neurons to ring neurons, and $77.48\%$ connect neurons of the exact same ring neuron subtype among the top 8 ER classes), whereas cholinergic compass feedback loops (`EPG <-> PEN`, 305 dyads) occupy a distinct columnar subsystem. All cell-type counts are strictly descriptive anatomy: they do not establish independent cell-type statistical preference, in vivo physiological inhibition, or dynamic ring-attractor function. All analytical benchmarks and primary quantities are audited, reproducible, and calibrated; no further research phases or unprompted computational experiments are warranted.

---

## 2. Compact Table of Validated Results

All quantities are audited from project-local artifacts at threshold $w \ge 5$ in the Ellipsoid Body (`EB`):

| Metric / Analysis | Observed Value | Null Mean ($\pm \text{SD}$) | Enrichment Ratio | Effect Size ($Z$) | Empirical $p$-value | Multiple Testing / FDR | Status |
|---|---|---|---|---|---|---|---|
| **Active EB Neurons ($N$)** | $483$ | — | — | — | — | — | **Verified** |
| **Directed Edges ($E$)** | $15,812$ | — | — | — | — | $R_{\text{edge}} = 44.50\%$ | **Verified** |
| **Mutual Dyads ($M$)** | $3,518$ | — | — | — | — | $R_{\text{dyad}} = 28.62\%$ | **Verified** |
| **Consensus GABA–GABA Dyads** | $2,615$ | — | — | — | — | $74.33\%$ of $M$ | **Verified** |
| **Phase 6 Baseline Null** (Mutual quartiles, shared stream) | $2,615$ | $2,167.11 \pm 29.31$ | $1.2067\times$ (+20.7%) | $+15.28$ | $0.000500$ | $q = 0.001749$ (21 tests) | **Reproduced** |
| **Phase 7 Baseline Rerun** (Mutual quartiles, fresh seed 42) | $2,615$ | $2,167.84 \pm 30.38$ | $1.2063\times$ (+20.6%) | $+14.72$ | $0.000500$ | $p \le 1/(B+1)$ | **Reproduced** |
| **Primary Sensitivity** (In $\times$ Out tertiles, 9 strata) | $2,615$ | $2,037.96 \pm 35.86$ | $1.2831\times$ (+28.3%) | $+16.09$ | $0.000500$ | $p \le 1/(B+1)$ | **Reproduced** |
| **Secondary Sensitivity** (In $\times$ Out medians, 4 strata) | $2,615$ | $1,984.76 \pm 48.05$ | $1.3175\times$ (+31.8%) | $+13.12$ | $0.000500$ | $p \le 1/(B+1)$ | **Reproduced** |
| **Ring Neuron $\leftrightarrow$ Ring Neuron** | $2,306$ | — | — | — | — | $88.18\%$ of GABA–GABA; $65.55\%$ of $M$ | **Verified** |
| **Top 8 Homotypic ER Subtype Dyads** | $2,026$ | — | — | — | — | $77.48\%$ of GABA–GABA; $57.59\%$ of $M$ | **Verified** |
| **All 10 Homotypic ER Subtype Dyads** | $2,086$ | — | — | — | — | $79.77\%$ of GABA–GABA; $59.29\%$ of $M$ | **Verified** |
| **Total Homotypic Dyads (All Types)** | $2,171$ | — | — | — | — | $61.71\%$ of $M$ | **Verified** |
| **Compass `EPG <-> PEN` Dyads** | $305$ | — | — | — | — | $8.67\%$ of $M$ (0 GABA–GABA; 300 ACh–ACh) | **Verified** |

---

## 3. Annotation-Row Coverage versus Cell-Type-Label Coverage

The analysis mapped the 483 active EB root IDs to the local, version-pinned FlyWire v2.1.0 annotation release (`Supplemental_file1_neuron_annotations.tsv`, commit `ebd66db2596fcc39c6950fb54ea3efa00f7fe8a0`).

### A. Node-Level Annotation Breakdown ($N = 483$)

| Field Name | Non-Missing Entries | Coverage (%) | Description & Missingness Nature |
|---|:---:|:---:|---|
| **Annotation Row Match** | **$483$** | **$100.00\%$** | Every single active EB node has an exact row match by 64-bit `root_id`. |
| `super_class` | $483$ | $100.00\%$ | All $483$ assigned to `central`. |
| `cell_class` | $481$ | $99.59\%$ | $474$ `CX`, $2$ `Kenyon_Cell`, $2$ `olfactory`, $1$ `MBON`, $1$ `MBIN`, $1$ `ALLN`. Two unassigned (descending neuron `DNd01`, central brain neuron `CB3500`). |
| `cell_sub_class` | $332$ | $68.74\%$ | $276$ `ring neuron`, $48$ `columnar`, $8$ `tangential`. **$151$ nodes are blank in this field**, including major CX columnar types (`EPG`, `PEN`, `PEG`) and tangential (`ExR`) types. |
| `cell_type` | $15$ | $3.11\%$ | **$468$ nodes are blank in this field**. In FlyWire v2.1.0, central-complex cell types are catalogued in `hemibrain_type`, not `cell_type`. |
| `hemibrain_type` | $479$ | $99.17\%$ | $479$ nodes possess specific types (`ER2`, `ER3d`, `EPG`, `PEN_a(PEN1)`, etc.). Only $4$ nodes lack `hemibrain_type` ($3$ CX columnar, $1$ `CB3500`). None of these $4$ nodes participate in mutual dyads at $w \ge 5$. |

### B. Dyad-Level Endpoint Coverage ($M = 3,518$)

* **Annotation Row Match**: **$3,518 / 3,518$ dyads ($100.00\%$)** have both endpoints matched to an annotation row.
* **`hemibrain_type` Coverage**: **$3,518 / 3,518$ dyads ($100.00\%$)** have both endpoints matched to a specific hemibrain type. Zero mutual dyads involve nodes with missing `hemibrain_type`.
* **`cell_sub_class` Coverage**:
  - Both endpoints non-missing: $2,415$ dyads ($68.65\%$).
  - One or both endpoints missing `cell_sub_class`: $1,103$ dyads ($31.35\%$).

### C. Complete Disaggregation of the $1,103$ Missing Sub-Class Dyads

The $1,103$ dyads involving missing `cell_sub_class` endpoints are resolved by cross-referencing their `hemibrain_type`:
1. **Both Endpoints Missing Sub-Class ($639$ dyads, $18.16\%$ of $M$)**:
   - **$305$ Reciprocal Compass Loops**: $163$ `EPG <-> PEN_a(PEN1)` and $142$ `EPG <-> PEN_b(PEN2)`.
   - **$161$ Compass to Tangential Loops**: $81$ `EPG <-> ExR6`, $58$ `EPG <-> ExR5`, $12$ `ExR4 <-> PEN_a`, $6$ `ExR4 <-> PEN_b`, $4$ `ExR7 <-> PEN_b`.
   - **$80$ Homotypic Columnar Loops**: $69$ `EPG <-> EPG`, $11$ `PEN_b <-> PEN_b`.
   - **$93$ Other Columnar / Tangential Loops**: $32$ `EPG <-> ExR4`, $25$ `ExR6 <-> PEN_a`, $11$ `ExR4 <-> PEG`, $25$ miscellaneous pairs.
2. **One Endpoint Ring Neuron, One Endpoint Missing Sub-Class ($399$ dyads, $11.34\%$ of $M$)**:
   - **$195$ Ring Neuron to Extrinsic Ring (ExR) Loops**: $84$ `ER5 <-> ExR1`, $81$ `ER3d <-> ExR1`, $29$ `ER3d <-> ExR3`, $1$ `ER3p <-> ExR1`.
   - **$134$ Ring Neuron to Columnar Compass Loops**: $102$ `EPG <-> ER4m`, $16$ `EPG <-> ER2`, $10$ `EPG <-> ER3w`, $4$ `EPG <-> ER3d`, $2$ `EPG <-> ER3a`.
   - **$70$ Ring Neuron to PEG / Other Columnar Loops**: $51$ `ER6 <-> PEG`, $19$ miscellaneous pairs.
3. **Columnar to Missing Sub-Class ($65$ dyads, $1.85\%$ of $M$)**:
   - $49$ `EL <-> EPG`, $15$ `EL <-> ExR1`, $1$ `EL <-> ExR6`.

---

## 4. Resolution of Numerical Inconsistencies and Ambiguities

### A. Baseline Null Mean: $2,167.11$ vs. $2,167.84$
* **Finding**: The Phase 6 artifact reported a null mean of $2,167.11 \pm 29.31$, whereas the Phase 7 baseline comparison reported $2,167.84 \pm 30.38$.
* **Audit Cause**: Pure Monte Carlo random-number generator (RNG) stream position.
  - In `scripts/run_phase6_controlled_study.py`, a single `rng_perm = random.Random(42)` generator was shared across neuropil regions and thresholds. Because EB $w = 3$ was processed prior to EB $w = 5$, the $w = 5$ baseline drew permutations 2,001 through 4,000 from the sequence.
  - In `scripts/run_phase7_robustness_and_celltypes.py`, each ensemble was instantiated with a fresh `random.Random(seed=42)`, drawing permutations 1 through 2,000.
* **Assessment**: The numerical difference is $+0.73$ dyads ($0.034\%$ of the mean), well within the expected standard error of the mean ($\text{SEM} \approx 30.38 / \sqrt{2000} \approx 0.68$). Both runs share identical code, strata, and observed counts.

### B. Homotypic ER Dyad Counts: $2,026$ vs. $2,086$
* **Finding**: Earlier summaries cited both $2,026$ and $2,086$ homotypic ring neuron dyads.
* **Audit Cause**: Explicit subtype inclusion boundary.
  - **$2,026$ dyads**: Strictly the top 8 homotypic ER subtypes: `ER2` ($458$), `ER3d` ($445$), `ER4d` ($274$), `ER3w` ($243$), `ER5` ($191$), `ER3a` ($174$), `ER3p` ($129$), and `ER3m` ($112$).
  - **$2,086$ dyads**: All 10 homotypic ER subtypes present in the EB graph, which adds `ER4m` ($49$ dyads) and `ER1` ($11$ dyads).
* **Assessment**: Both counts are mathematically exact. $2,026 / 2,615 = 77.48\%$ represents the top 8 classes; $2,086 / 2,615 = 79.77\%$ represents all 10 ER classes.

### C. Denominator Clarity for Proportions
To prevent confusion across manuscripts and presentations, all dyad proportions are explicitly indexed to their exact denominators:
1. **Total EB Mutual Dyads Denominator ($M = 3,518$)**:
   - Consensus GABA–GABA dyads: $2,615 / 3,518 = 74.33\%$
   - Ring neuron $\leftrightarrow$ Ring neuron dyads: $2,306 / 3,518 = 65.55\%$
   - Total homotypic dyads (all types): $2,171 / 3,518 = 61.71\%$
   - All homotypic ER dyads: $2,086 / 3,518 = 59.29\%$
   - Top 8 homotypic ER dyads: $2,026 / 3,518 = 57.59\%$
   - Compass `EPG <-> PEN` dyads: $305 / 3,518 = 8.67\%$
2. **GABA–GABA Mutual Dyads Denominator ($N_{\text{GABA–GABA}} = 2,615$)**:
   - Ring neuron $\leftrightarrow$ Ring neuron dyads: $2,306 / 2,615 = 88.18\%$
   - All homotypic ER dyads: $2,086 / 2,615 = 79.77\%$
   - Top 8 homotypic ER dyads: $2,026 / 2,615 = 77.48\%$
   - Compass `EPG <-> PEN` dyads: $0 / 2,615 = 0.00\%$
3. **Ring–Ring Mutual Dyads Denominator ($N_{\text{Ring–Ring}} = 2,306$)**:
   - All homotypic ER dyads: $2,086 / 2,306 = 90.46\%$
   - Top 8 homotypic ER dyads: $2,026 / 2,306 = 87.86\%$

### D. Taxonomy Level and Finer Morphotypes
* The labels `ER2`, `ER3d`, `ER4d`, `ER3w`, `ER5`, etc., derive directly from the `hemibrain_type` field in FlyWire v2.1.0 annotations.
* In Hulse et al. (2021), ring neuron types were anatomically subdivided into finer morphotypes (e.g., `ER2_a` through `ER2_d`, `ER3d_a` through `ER3d_d`).
* The FlyWire v2.1.0 release table does NOT provide these letter-suffixed morphotypes in `hemibrain_type` or `cell_type`. Therefore, all claims in this project apply strictly to the base hemibrain cell types and must not be described as confirming finer morphotypic sub-clustering.

---

## 5. Final Approved Wording for the Primary Result

The sole approved summary statement for the core finding of this project is:

> **"The EB GABA-GABA mutual-dyad association persisted under the tested degree-stratified label-permutation models. The magnitude varied with the null specification. The cell-type counts are descriptive and do not establish a new functional mechanism."**

---

## 6. Claims That Must NOT Be Made

To preserve scientific integrity and avoid uncalibrated overclaiming, the following claims are explicitly barred from any paper, presentation, or portfolio summary:

1. **NO Claim of Exact Directed-Degree Confounding Elimination**:
   - The sensitivity null models stratify neurons into discrete tertile or quartile bins ($9$ strata or $4$ strata). They do NOT preserve each node's exact directed in-degree and out-degree sequence. Within each stratum, degree variance remains.
2. **NO Claim of Independent Cell-Type Statistical Enrichment**:
   - No cell-type-level permutation null model was executed. Homotypic ER counts ($2,026$ / $2,086$) are descriptive sample counts, not formal hypothesis tests demonstrating partner preference beyond degree or regional co-occurrence.
3. **NO Claim of Causal or Mechanistic Explanation for ACh–GABA Depletion**:
   - The low count of $\text{ACh} \leftrightarrow \text{GABA}$ mutual dyads ($0.27\times$) correlates with the spatial and anatomical segregation of compass columnar neurons and tangential ring neurons, but this observational co-occurrence does not prove an active partner-exclusion mechanism.
4. **NO Claim of Verified Physiological Inhibition**:
   - Neurotransmitter identities are computationally predicted consensus phenotypes derived from synapse-level machine learning models. Predicted GABAergic identity does not establish functional inhibitory postsynaptic currents, hyperpolarization, or receptor expression ($Rdl$ vs. others) in vivo.
5. **NO Claim of Confirmed Ring-Attractor Dynamics**:
   - Static connectomic wiring diagrams demonstrate structural synaptic adjacency, not continuous dynamic state transitions, bump attractor stability, or angular velocity integration.
6. **NO Claim of a "First-Ever" Method or Biological Discovery**:
   - Degree-stratified label permutations, configuration models, and directed reciprocity analyses are classical network-science methodologies.

---

## 7. Known Methodological Limitations

1. **Single Connectome Specimen Scope**:
   All findings derive from a single adult female *Drosophila melanogaster* brain (FAFB v783). Cross-animal variability, developmental plasticity, and sexual dimorphism cannot be evaluated from this dataset.
2. **Threshold Sensitivity ($w \ge 5$)**:
   Analyses rely on a conservative synaptic threshold ($w \ge 5$) to exclude false-positive automated synapse detections. While robustness was evaluated across $w \ge 3$ and $w \ge 5$, connections mediated by 1–2 synapses are excluded.
3. **Coarse Permutation Mobility**:
   In fine stratifications, high-degree neurons risk becoming immobile if strata contain few nodes of differing neurotransmitters. The $3 \times 3$ tertile model balanced mobility ($100\%$ mobile nodes) against degree resolution, but does not provide continuous conditioning.
4. **Static Morphological Topology**:
   Synaptic weights represent counted structural contacts, ignoring synaptic size, vesicle pool dynamics, neuromodulatory tone, and electrical gap junctions.

---

## 8. Short List of Existing Files Needed to Reproduce the Main Result

To independently reproduce the primary audited result from scratch, only the following project files and data resources are required:

1. **Source Connectome Data**:
   - `data/raw/proofread_connections_783.feather` (852 MB; aggregated FAFB v783 directed connectivity graph).
2. **Pinned Neuron Annotations**:
   - `data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv` (26 MB; official FlyWire v2.1.0 release annotations).
3. **Execution Scripts**:
   - `scripts/run_phase6_controlled_study.py` (Phase 6 controlled study, central-complex baseline, and rewiring diagnostics).
   - `scripts/run_phase7_robustness_and_celltypes.py` (Phase 7 directed sensitivity ensemble and cell-type mapping).
4. **Cached Analysis Graphs & Outputs**:
   - `results/real_data_pilot/phase7/eb_node_covariates.json` (Active EB node degree covariates, mutual dyad edge list, and consensus transmitters).
   - `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json` (Structured JSON containing all permutation distributions, Z-scores, and cell-type counts).
   - `results/real_data_pilot/phase6/phase6_controlled_study_results.json` (Structured Phase 6 regional results and Benjamini-Hochberg FDR adjustments).
5. **Verification Test Suite**:
   - `tests/test_preliminary_analysis.py` (24 automated unit tests covering graph reciprocity, degree stratification, topological invariants, and annotation integrity).

---

## 9. Modified Files and SHA-256 Checksums

| File Path | File Size (Bytes) | SHA-256 Checksum | Description |
|---|---|---|---|
| `docs/phase7_1_final_claim_audit.md` | *This file* | *Computed upon freeze* | Phase 7.1 Final Claim Audit & Freeze Report |
| `docs/phase7_robustness_and_celltype_feasibility.md` | 19,742 | `be3ec7d64410e961a2993580ee539d9fb7390379664daf7770a9ea1f751cd340` | Calibrated Phase 7 Decision Report |
| `data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv` | 27,015,208 | `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6` | Pinned FlyWire v2.1.0 Annotations |
| `results/real_data_pilot/phase7/eb_node_covariates.json` | 134,801 | `179cc472bd4066d90962814a597499b6008e97df145caccff961f9cd5fe88e3b` | Cached EB Node Covariates & Dyads |
| `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json` | 10,879 | `31f29f578cf404b20dae9fa5e67bed313e36b6af9e04cf685fd842f00973eee9` | Phase 7 Structured Results Artifact |
| `scripts/run_phase7_robustness_and_celltypes.py` | 13,293 | `151d99c189091df44047f1c71c0432664923942eb0c06312f6f8a57011d48190` | Executed Phase 7 Analysis Pipeline |
| `tests/test_preliminary_analysis.py` | 29,887 | `f0a13447adfc5139989b4f84886db3ce143ce4e33c23feab1f87c03b9449a716` | Automated Test Suite (24/24 passing) |

---

## 10. Automated Test Suite Verification

```bash
.venv/bin/python3 -m unittest discover -s tests -v
```

Output:
```text
test_64bit_id_preservation (test_preliminary_analysis.TestConnectivityPipeline.test_64bit_id_preservation) ... ok
test_autapse_self_connection (test_preliminary_analysis.TestConnectivityPipeline.test_autapse_self_connection) ... ok
test_disconnected_components (test_preliminary_analysis.TestConnectivityPipeline.test_disconnected_components) ... ok
test_duplicate_edge_aggregation (test_preliminary_analysis.TestConnectivityPipeline.test_duplicate_edge_aggregation) ... ok
test_ground_truth_graph_metrics (test_preliminary_analysis.TestConnectivityPipeline.test_ground_truth_graph_metrics) ... ok
test_hub_tie_breaking_determinism (test_preliminary_analysis.TestConnectivityPipeline.test_hub_tie_breaking_determinism) ... ok
test_max_records_limit_and_zero_behavior (test_preliminary_analysis.TestConnectivityPipeline.test_max_records_limit_and_zero_behavior) ... ok
test_missing_and_invalid_identifiers (test_preliminary_analysis.TestConnectivityPipeline.test_missing_and_invalid_identifiers) ... ok
test_neuropil_regional_aggregation (test_preliminary_analysis.TestConnectivityPipeline.test_neuropil_regional_aggregation) ... ok
test_reproducibility (test_preliminary_analysis.TestConnectivityPipeline.test_reproducibility) ... ok
test_row_order_invariance (test_preliminary_analysis.TestConnectivityPipeline.test_row_order_invariance) ... ok
test_schema_classification (test_preliminary_analysis.TestConnectivityPipeline.test_schema_classification) ... ok
test_edge_vs_dyad_reciprocity_definitions (test_preliminary_analysis.TestPhase4ReciprocityAndMotifs.test_edge_vs_dyad_reciprocity_definitions) ... ok
test_permutation_null_invariants (test_preliminary_analysis.TestPhase4ReciprocityAndMotifs.test_permutation_null_invariants) ... ok
test_reciprocal_transmitter_motif_toy_graph (test_preliminary_analysis.TestPhase4ReciprocityAndMotifs.test_reciprocal_transmitter_motif_toy_graph) ... ok
test_count_mutual_motifs_directed (test_preliminary_analysis.TestPhase5DegreePreservingNullModel.test_count_mutual_motifs_directed) ... ok
test_directed_edge_swap_invariants (test_preliminary_analysis.TestPhase5DegreePreservingNullModel.test_directed_edge_swap_invariants) ... ok
test_edge_swap_determinism_and_mixing (test_preliminary_analysis.TestPhase5DegreePreservingNullModel.test_edge_swap_determinism_and_mixing) ... ok
test_benjamini_hochberg_fdr (test_preliminary_analysis.TestPhase6ControlledAnalysis.test_benjamini_hochberg_fdr) ... ok
test_conditional_permutations_topology_invariance (test_preliminary_analysis.TestPhase6ControlledAnalysis.test_conditional_permutations_topology_invariance) ... ok
test_mixing_diagnostics_autocorrelation (test_preliminary_analysis.TestPhase6ControlledAnalysis.test_mixing_diagnostics_autocorrelation) ... ok
test_partition_into_strata (test_preliminary_analysis.TestPhase6ControlledAnalysis.test_partition_into_strata) ... ok
test_annotation_file_integrity (test_preliminary_analysis.TestPhase7RobustnessAndCellTypes.test_annotation_file_integrity) ... ok
test_joint_directed_degree_grid_strata (test_preliminary_analysis.TestPhase7RobustnessAndCellTypes.test_joint_directed_degree_grid_strata) ... ok

----------------------------------------------------------------------
Ran 24 tests in 0.083s

OK
```
All 24 automated unit tests pass, verifying data integrity, directed graph reciprocity, degree-preserving strata logic, annotation schema conformity, and FDR correction.
