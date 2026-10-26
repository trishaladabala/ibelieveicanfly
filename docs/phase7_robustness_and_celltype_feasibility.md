# Phase 7: Robustness Gate and Cell-Type Feasibility Analysis

**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Date**: October 20, 2026  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04.5 LTS)  
**Execution Environment**: Project-local `.venv` (Python 3.12, PyArrow 26.0.0)  
**Status**: Completed Decision and Feasibility Report  

---

## 1. Concise Decision

**DECISION: SURVIVED ROBUSTNESS GATE — PROCEED TO CALIBRATED PRESENTATION**

1. **The Primary Association Survives Directed Degree-Aware Sensitivity Testing**:
   When controlling for joint directed in-degree and directed out-degree (3x3 tertile grid, 9 strata), the Ellipsoid Body (`EB`, $w \ge 5$) $\text{GABA} \leftrightarrow \text{GABA}$ mutual dyad association remains statistically robust:
   - Observed: **$2,615$ dyads** ($74.33\%$ of all $3,518$ mutual dyads).
   - Sensitivity Null Mean: **$2,037.96 \pm 35.86$ dyads**.
   - Conditional Enrichment: **$1.2831\times$ (+28.31% excess)**.
   - Calibrated Z-Score: **$+16.09$** ($p = 0.000500$, finite-sample resolution limit $p \le 1/2001$ under $B = 2,000$ permutations).
2. **Annotation Row Coverage is 100% (Field-Specific Granularity Documented)**:
   Using the official, version-pinned FlyWire v2.1.0 release annotations (`Supplemental_file1_neuron_annotations.tsv`), **483 / 483 active EB nodes (100.00%)** match an annotation row. Within matched nodes, **479 / 483 (99.17%)** possess a specific `hemibrain_type` (and 100% of nodes participating in mutual dyads possess a `hemibrain_type`), **332 / 483 (68.74%)** possess a `cell_sub_class`, and **15 / 483 (3.11%)** possess an entry in the literal `cell_type` column.
3. **Biological Reality Revealed**:
   - **$88.18\%$ of all GABA–GABA mutual dyads** ($2,306 / 2,615$) are formed specifically between **ring neurons** (`ring neuron <-> ring neuron`).
   - Across the entire Ellipsoid Body, **$61.71\%$ of all mutual dyads ($2,171 / 3,518$) are strictly homotypic** (both endpoints belong to the exact same published cell type, e.g. ER2–ER2, ER3d–ER3d, ER4d–ER4d).
   - Reciprocal compass loops (`EPG <-> PEN_a`, `EPG <-> PEN_b`) account for 305 mutual dyads ($8.67\%$).
   - Cross-talk between compass neurons and ring neurons is sparse, which correlates with the observed low frequency of $\text{ACh} \leftrightarrow \text{GABA}$ reciprocal loops ($0.27\times$), rather than demonstrating an active partner exclusion mechanism.
4. **Epistemic Stop Rule**:
   All inferential claims remain exploratory and derived from a single connectome specimen. In accordance with Phase 7 instructions, execution stops after this report. No further unprompted biological analyses or pipeline reruns will be initiated.

---

## 2. Baseline Result and Independently Reproduced Quantities

At threshold $w \ge 5$, the Ellipsoid Body (`EB`) baseline quantities were verified from `results/real_data_pilot/phase6/phase6_controlled_study_results.json` and cached in `results/real_data_pilot/phase7/eb_node_covariates.json`:
* **Active Neurons**: $483$
* **Directed Edges**: $15,812$ ($R_{\text{edge}} = 44.50\%$)
* **Total Mutual Dyads**: $M = 3,518$
* **Observed Consensus $\text{GABA} \leftrightarrow \text{GABA}$ Dyads**: $2,615$ ($74.33\%$ of $M$)
* **Phase 6 Baseline Null Model** (Mutual-Degree Quartiles, 4 strata, $B = 2,000$):
  - Null Mean: $2,167.11 \pm 29.31$ ($2,167.84 \pm 30.38$ on seed rerun)
  - Conditional Enrichment: $1.2067\times$ (+20.67% excess)
  - Z-Score: $+15.28$ ($+14.72$ on rerun)
  - Empirical $p$-value: $0.000500$ ($p \le 1/2001$)
  - Two-tailed empirical Monte Carlo test.

---

## 3. Targeted Sensitivity Analysis: Accounting for Directed Degrees and Confidence

### A. Pre-Specification of the Sensitivity Model
To address the critique that the Phase 6 null conditioned only on undirected mutual degree quartiles without preserving directed connectivity profiles, we designed the **Joint Directed In/Out-Degree Sensitivity Model**:

1. **Precise Null Hypothesis ($H_0^{\text{sens}}$)**:
   Given the empirical reciprocal topology ($M = 3,518$), the observed count of $\text{GABA} \leftrightarrow \text{GABA}$ mutual dyads is explained by the joint distribution of directed in-degrees and directed out-degrees of the active neurons.
2. **Statistic Tested**:
   The number of unordered mutual dyads $\{u, v\}$ where both neurons have consensus neurotransmitter label GABA: $C(\text{gaba}, \text{gaba})$.
3. **Properties Held Fixed vs. Changed**:
   - *Fixed*: Exact empirical mutual dyad graph ($\mathcal{M}$, with $M = 3,518$ constant); each node's joint directed degree tier; whole-cell consensus label counts.
   - *Relaxed*: Specific assignment of transmitter labels to individual nodes within the same joint degree stratum.
4. **Permutation Procedure & Stratification Grid**:
   - The active node population ($N = 483$) is partitioned using a 2D grid defined by **tertiles of directed in-degree** ($T_{\text{in}} \in \{0, 1, 2\}$) and **tertiles of directed out-degree** ($T_{\text{out}} \in \{0, 1, 2\}$), yielding **9 strata**.
   - In-degree tertile cutoffs: $\le 18$, $19\text{--}30$, $> 30$.
   - Out-degree tertile cutoffs: $\le 26$, $27\text{--}38$, $> 38$.
5. **Permutation Mobility and Stratum Diagnostics**:
   Every one of the 9 strata contains non-zero representation of multiple neurotransmitter classes, ensuring full permutation mobility (zero frozen strata):

| Stratum Key | In-Degree Range | Out-Degree Range | Total Nodes ($N$) | GABA Nodes | GABA % | Other NT Composition |
|---|---|---|---|---|---|---|
| **$\text{In}_0\_\text{Out}_0$** | $\le 18$ | $\le 26$ | 106 | 12 | 11.32% | ACh: 50, Ser: 29, DA: 8, Glut: 7 |
| **$\text{In}_0\_\text{Out}_1$** | $\le 18$ | $27\text{--}38$ | 38 | 29 | 76.32% | ACh: 9 |
| **$\text{In}_0\_\text{Out}_2$** | $\le 18$ | $> 38$ | 18 | 17 | 94.44% | ACh: 1 |
| **$\text{In}_1\_\text{Out}_0$** | $19\text{--}30$ | $\le 26$ | 32 | 18 | 56.25% | ACh: 9, DA: 5 |
| **$\text{In}_1\_\text{Out}_1$** | $19\text{--}30$ | $27\text{--}38$ | 73 | 64 | 87.67% | ACh: 9 |
| **$\text{In}_1\_\text{Out}_2$** | $19\text{--}30$ | $> 38$ | 62 | 52 | 83.87% | ACh: 8, DA: 2 |
| **$\text{In}_2\_\text{Out}_0$** | $> 30$ | $\le 26$ | 29 | 17 | 58.62% | ACh: 9, DA: 3 |
| **$\text{In}_2\_\text{Out}_1$** | $> 30$ | $27\text{--}38$ | 53 | 25 | 47.17% | ACh: 28 |
| **$\text{In}_2\_\text{Out}_2$** | $> 30$ | $> 38$ | 72 | 64 | 88.89% | Glut: 5, ACh: 3 |

6. **Permutable Population**: $100\%$ of active nodes ($483 / 483$) participate in permutation. No nodes are excluded or frozen.
7. **Empirical $p$-value**: Computed as an exact two-tailed Monte Carlo test: $p = (1 + \text{extreme}) / (B + 1)$ with $B = 2,000$ permutations.

---

## 4. Sensitivity Results: Robustness Gate Evaluation

| Model Evaluated | Strata Count & Grid | Observed GABA–GABA | Null Mean $\pm$ Std | Enrichment Ratio | Z-Score | Empirical $p$-value | Robustness Gate Status |
|---|---|---|---|---|---|---|---|
| **Phase 6 Baseline** | 4 strata (Mutual degree quartiles) | 2,615 (74.33%) | $2,167.84 \pm 30.38$ | $1.2063\times$ (+20.6%) | $+14.72$ | $p = 0.000500$ | **CONFIRMED** |
| **Primary Sensitivity (Model B)** | **9 strata (Directed in/out tertiles)** | **2,615 (74.33%)** | **$2,037.96 \pm 35.86$** | **$1.2831\times$ (+28.3%)** | **$+16.09$** | **$p = 0.000500$** | **SURVIVED (PASSED)** |
| **Secondary Sensitivity (Model A)** | 4 strata (Directed in/out medians) | 2,615 (74.33%) | $1,984.76 \pm 48.05$ | $1.3175\times$ (+31.8%) | $+13.12$ | $p = 0.000500$ | **SURVIVED (PASSED)** |

### Conclusion on the Robustness Gate:
The primary association **survived the robustness gate with high statistical stability**. Whether stratified by mutual-degree quartiles ($1.21\times, Z = +14.7$), directed in/out medians ($1.32\times, Z = +13.1$), or directed in/out tertiles ($1.28\times, Z = +16.1$), the conditional enrichment consistently remains between **$+20\%$ and $+32\%$ excess**, with empirical $p \le 0.000500$. 

This indicates that the residual $+20\%\text{--}28\%$ GABA–GABA excess persists when conditioning on coarse directed in-degree and out-degree tertile bins, although this sensitivity model stratifies nodes into 9 discrete strata rather than holding every node's exact directed degree sequence fixed.

---

## 5. Cell-Type Annotation Feasibility (FlyWire v2.1.0)

* **Source Repository**: `https://github.com/flyconnectome/flywire_annotations`
* **Version Pinned**: Tag `v2.1.0` (Git commit: `ebd66db2596fcc39c6950fb54ea3efa00f7fe8a0`)
* **Primary Annotation File**: `data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv`
* **File Checksum**: `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6` ($27,015,208$ bytes, $139,255$ neuron records)

### Mapping Coverage
* **Active EB Nodes ($w \ge 5$)**: **483 / 483 (100.00%) matched**. Zero unmatched nodes.
* **All EB Mutual Dyads ($w \ge 5$)**: **3,518 / 3,518 (100.00%) both endpoints matched**.
* **Observed GABA–GABA Mutual Dyads**: **2,615 / 2,615 (100.00%) both endpoints matched**.

### Broader Node Taxonomy Breakdown ($N = 483$)
* **Cell Class**:
  - `CX` (Central Complex): $474$ neurons ($98.14\%$)
  - `Kenyon_Cell`: $2$ neurons ($0.41\%$)
  - `olfactory`: $2$ neurons ($0.41\%$)
  - `MBON`: $1$ neuron ($0.21\%$)
  - `MBIN`: $1$ neuron ($0.21\%$)
  - `ALLN`: $1$ neuron ($0.21\%$)
  - `unannotated`: $2$ neurons ($0.41\%$)
* **Cell Sub-Class**:
  - `ring neuron`: $276$ neurons ($57.14\%$)
  - `unannotated`: $151$ neurons ($31.26\%$)
  - `columnar`: $48$ neurons ($9.94\%$)
  - `tangential`: $8$ neurons ($1.66\%$)

---

## 6. Descriptive Biological Summary of EB Mutual Dyads

### A. All 3,518 Observed Mutual Dyads
1. **Homotypic vs. Heterotypic Specific Types**:
   - **Both endpoints have the EXACT same specific cell type**: **2,171 dyads (61.71%)**.
   - Endpoints belong to different cell types: $1,347$ dyads ($38.29\%$).
   - Endpoints lacking specific cell-type annotation: **0 dyads (0.00%)**.
2. **Sub-Class Pairings**:
   - `ring neuron <-> ring neuron`: **2,306 dyads (65.55%)**
   - `unannotated <-> unannotated`: $639$ dyads ($18.16\%$)
   - `ring neuron <-> unannotated`: $399$ dyads ($11.34\%$)
   - `columnar <-> ring neuron`: $109$ dyads ($3.10\%$)
   - `columnar <-> unannotated`: $65$ dyads ($1.85\%$)
   *(Note on Sub-Class 'unannotated': 151 EB neurons, including columnar EPG, PEN, PEG and tangential ExR neurons, have empty cell_sub_class entries in FlyWire v2.1.0 but have fully resolved hemibrain_type entries. Disaggregating these reveals that the 639 'unannotated <-> unannotated' dyads comprise 305 EPG-PEN dyads, 161 ExR-columnar dyads, 80 homotypic columnar dyads like EPG-EPG and PEN-PEN, and 93 other tangential/columnar dyads).*

### B. Observed GABA–GABA Mutual Dyads ($N = 2,615$)
The $2,615$ GABA–GABA mutual dyads are overwhelmingly accounted for by **homotypic ring neuron subtypes**:

| Specific Cell Type Pairing | Anatomical Description | Observed Dyads | Pct of GABA–GABA Dyads | Homotypic / Heterotypic |
|---|---|---|---|---|
| **`ER2 <-> ER2`** | Ring neuron subtype 2 (visual/heading) | 458 | 17.51% | Homotypic |
| **`ER3d <-> ER3d`** | Ring neuron subtype 3d | 445 | 17.02% | Homotypic |
| **`ER4d <-> ER4d`** | Ring neuron subtype 4d | 274 | 10.48% | Homotypic |
| **`ER3w <-> ER3w`** | Ring neuron subtype 3w | 243 | 9.29% | Homotypic |
| **`ER5 <-> ER5`** | Ring neuron subtype 5 (sleep/state) | 191 | 7.30% | Homotypic |
| **`ER3a <-> ER3a`** | Ring neuron subtype 3a | 174 | 6.65% | Homotypic |
| **`ER3p <-> ER3p`** | Ring neuron subtype 3p | 129 | 4.93% | Homotypic |
| **`ER3m <-> ER3m`** | Ring neuron subtype 3m | 112 | 4.28% | Homotypic |
| **`ER5 <-> ExR1`** | Ring neuron 5 to tangential interneuron 1 | 84 | 3.21% | Heterotypic |
| **`ER3d <-> ExR1`** | Ring neuron 3d to tangential interneuron 1 | 81 | 3.10% | Heterotypic |
| **`ER3a <-> ER3m`** | Ring neuron 3a to ring neuron 3m | 75 | 2.87% | Heterotypic |
| **`EL <-> ER4d`** | Ellipsoid tangential to ring neuron 4d | 72 | 2.75% | Heterotypic |
| **`ER2 <-> ER4m`** | Ring neuron 2 to ring neuron 4m | 65 | 2.49% | Heterotypic |
| **`ER4m <-> ER4m`** | Ring neuron subtype 4m | 49 | 1.87% | Homotypic |
| **`ER2 <-> ER3w`** | Ring neuron 2 to ring neuron 3w | 42 | 1.61% | Heterotypic |

*Descriptive Anatomical Summary*:
Intra-subtype ring neuron dyads (`ER2–ER2`, `ER3d–ER3d`, etc.) account for **$2,026$ dyads (77.48% of all GABA–GABA mutual dyads, 57.59% of all EB mutual dyads)**. These descriptive counts show that observed GABA–GABA mutual dyads are dominated by pairings between neurons sharing the same ring neuron type, but do not establish independent cell-type-specific enrichment beyond degree-stratified models or dynamic ring-attractor function.

---

## 7. Ambiguities and Methodological Limitations

1. **Exploratory Single-Connectome Scope**:
   All findings are derived from one adult female connectome (FAFB v783). While connection counts and topologies are verified, cross-animal variability cannot be evaluated from this dataset alone.
2. **Descriptive Nature of Cell-Type Counts**:
   The cell-type breakdown is presented purely as descriptive anatomy. We do not claim cell-type-specific statistical enrichment or infer in vivo partner preferences beyond what degree sequences explain.
3. **No Direct Physiological Proof**:
   Consensus GABAergic phenotypes and anatomical synapses do not demonstrate functional inhibitory postsynaptic currents, gain control, or attractor bump dynamics. Functional imaging or electrophysiology is required for dynamic claims.

---

## 8. What the Evidence Supports vs. What It Does Not Support

```
+-----------------------------------------------------------------------------------------+
|                                    EVIDENTIARY AUDIT                                    |
+-----------------------------------------------------------------------------------------+
| WHAT THE EVIDENCE SUPPORTS:                             WHAT IT DOES NOT SUPPORT:       |
|                                                                                         |
| 1. Robust Statistical Association:                      1. No Ring Attractor Discovery: |
|    EB GABA-GABA mutual dyads remain +20% to +32%        Anatomy alone does not prove    |
|    enriched across mutual-degree and directed-degree    dynamic heading integration.    |
|    strata (Z > 13, p = 0.0005).                                                         |
|                                                         2. No "First-Ever" Claim:       |
| 2. Complete Annotation Traceability:                    Rewiring and stratified nulls   |
|    100% of EB active nodes map to FlyWire v2.1.0.       are standard classical methods. |
|                                                                                         |
| 3. Ring Neuron Architecture:                            3. No Physiological Proof:      |
|    88.2% of GABA-GABA reciprocity is between ring       Predicted GABA release does not |
|    neurons, dominated by homotypic subtype loops.       guarantee inhibitory effect.    |
+-----------------------------------------------------------------------------------------+
```

---

## 9. Smallest Justified Next Action

The core research question of Phase 6 and Phase 7 is now conclusively answered:
* The unconditioned edge-swap null was confounded by topological reciprocity collapse ($4.61\times$).
* The conditional degree-stratified association survives sensitivity testing ($+20\%\text{--}28\%$, $Z > 13$).
* The descriptive biological substrate is predominantly homotypic ring neuron recurrence ($88.18\%$ of GABA–GABA dyads are between ring neurons, with $77.48\%$ sharing the exact same ring neuron subtype among the top 8 ER classes).

**Smallest Justified Next Action**:
Prepare the project for archival, presentation, or formal submission. No further algorithmic modifications or pipeline runs are warranted.

---

## 10. File Artifacts and SHA-256 Checksums

| File Path | File Size (Bytes) | SHA-256 Checksum | Description |
|---|---|---|---|
| `docs/phase7_robustness_and_celltype_feasibility.md` | *This file* | *Computed upon write* | Official Phase 7 Decision Report |
| `data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv` | 27,015,208 | `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6` | Pinned FlyWire v2.1.0 Annotations |
| `data/raw/annotations_v2.1.0/Supplemental_files_columns.md` | 6,717 | `5bed86549dd6d2837397c2a451db7606718f5d5be8a8a7a7a49219aade1c9802` | Annotation Schema Documentation |
| `results/real_data_pilot/phase7/eb_node_covariates.json` | 134,801 | `179cc472bd4066d90962814a597499b6008e97df145caccff961f9cd5fe88e3b` | Cached EB Node Covariates & Dyads |
| `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json` | 10,879 | `31f29f578cf404b20dae9fa5e67bed313e36b6af9e04cf685fd842f00973eee9` | Phase 7 Structured Results Artifact |
| `scripts/run_phase7_robustness_and_celltypes.py` | 13,293 | `151d99c189091df44047f1c71c0432664923942eb0c06312f6f8a57011d48190` | Executed Phase 7 Analysis Script |
| `tests/test_preliminary_analysis.py` | 29,887 | `f0a13447adfc5139989b4f84886db3ce143ce4e33c23feab1f87c03b9449a716` | Automated Test Suite (24/24 passing) |

---

## 11. Automated Test Suite Execution

```bash
.venv/bin/python3 -m unittest discover -s tests -v
```

Actual output:
```text
Ran 24 tests in 0.079s

OK
```
All 24 automated unit tests pass, confirming grid stratification logic, annotation schema integrity, topology preservation, and FDR corrections.

