# Quantitative Reciprocity and Neurotransmitter Pairing in the Adult *Drosophila* Central Complex: An Audited Connectomic Study

**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics Pipeline  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Author**: Computational Biology Research Team  
**Date**: October 20, 2026  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04.5 LTS)  
**Software Environment**: Python 3.12, PyArrow 26.0.0, Cairo  
**Status**: Final Definitive Research Report — Portfolio Release Candidate  

---

## Abstract

We present a reproducible graph-theoretic analysis of synaptic reciprocity and reciprocal neurotransmitter motifs in the central complex of the adult female *Drosophila melanogaster* connectome (FAFB v783), integrated with official FlyWire version 2.1.0 annotations. An initial unconditioned directed edge-swap null model produced an apparent $\sim 6.78\times$ enrichment of $\text{GABA} \leftrightarrow \text{GABA}$ mutual dyads in the Ellipsoid Body (`EB`, threshold $w \ge 5$). Methodological audit revealed that this extreme ratio was primarily an artifact of topological reciprocity collapse: degree-preserving edge-swap rewiring collapsed baseline empirical edge reciprocity by $4.61\times$ (from $44.50\%$ to $9.66\%$), artificially inflating unconditioned motif ratios. To decouple physical reciprocity from chemical transmitter pairing, we implemented conditional, degree-stratified label-permutation ensembles that hold the empirical mutual dyad graph ($M = 3,518$) invariant while exchanging whole-neuron predicted transmitter labels within degree strata. Under this protected framework, a modest conditional excess of GABA–GABA mutual dyads persisted across all tested specifications: $+20.6\%$ to $+20.7\%$ under mutual-degree quartiles ($1.206\times$, $Z = +14.72$ to $+15.28$, empirical $p = 0.000500$), $+28.3\%$ under joint directed in/out tertiles ($1.283\times$, $Z = +16.09$, $p = 0.000500$), and $+31.8\%$ under directed in/out median splits ($1.318\times$, $Z = +13.12$, $p = 0.000500$). Mapping active neurons to version-pinned annotations demonstrates that this signal reflects an underlying anatomical substrate dominated by homotypic ring neuron recurrence: $88.18\%$ of GABA–GABA mutual dyads connect ring neurons to ring neurons ($2,306$ dyads), and $77.48\%$ share the exact same reported ER base type among the top 8 subclasses ($2,026$ dyads). In contrast, cholinergic/glutamatergic compass loops (`EPG <-> PEN`, $305$ dyads) occupy a segregated columnar feedback loop. These cell-type counts are strictly descriptive anatomy and do not establish independent cell-type-specific partner preference, in vivo physiological inhibition, or dynamic ring-attractor function.

---

## 1. Introduction and Research Question

Reciprocal synaptic connectivity—where two neurons form bidirectional chemical synapses—is a fundamental motif of neural circuits implicated in feedback inhibition, gain control, reverberatory memory, and ring-attractor networks. In the insect central complex (CX), comprising the Ellipsoid Body (EB), Fan-Shaped Body (FB), and Protocerebral Bridge (PB), spatial navigation and heading representation are mediated by interconnected columnar and tangential neuron populations.

This project addresses two specific computational questions:
1. **Topological Reciprocity**: To what extent is synaptic reciprocity elevated in the central complex compared to whole-brain baseline levels, and does classical degree-preserving rewiring accurately evaluate reciprocal motifs?
2. **Conditional Chemical Pairing**: Given the empirical reciprocal dyad topology, are reciprocal connections between neurons sharing the same predicted neurotransmitter (specifically GABAergic ring neurons) statistically enriched beyond what is expected from neuronal degree distributions?

---

## 2. Dataset Provenance and Annotation Versioning

All analyses are conducted on public, version-controlled biological connectome resources:

1. **Aggregated Connectome Graph**:
   - **Source**: FlyWire FAFB v783 aggregated connectivity dataset ([Zenodo record 10676866](https://zenodo.org/records/10676866)).
   - **File**: `proofread_connections_783.feather` (852 MB; SHA-256: `9455325b1617d5e466e3eb7f9379e49c7ad6e72b0dbd28cc886c965c404c0ec3`).
   - **Properties**: 13,440,642 raw directed connection records across 127,978 proofread root IDs, containing pre/post 64-bit identifiers, neuropil labels, synapse counts, and connection-level neurotransmitter prediction weights.
2. **Version-Pinned Neuron Annotations**:
   - **Source**: Official FlyWire Annotation Repository ([flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations/releases/tag/v2.1.0)).
   - **Release**: Tag `v2.1.0`, Git commit `ebd66db2596fcc39c6950fb54ea3efa00f7fe8a0`.
   - **File**: `Supplemental_file1_neuron_annotations.tsv` (27 MB; SHA-256: `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6`).

---

## 3. Directed Graph Construction and Reciprocity Definitions

### Graph Construction
The directed graph $G = (V, E)$ is constructed from connection records by filtering at a conservative synaptic weight threshold $w \ge 5$ to suppress automated false-positive synaptic detections:
- **Active Neurons ($V$)**: All root IDs participating in at least one directed edge with weight $w \ge 5$.
- **Directed Edges ($E$)**: A directed edge $u \to v$ exists if $\text{weight}(u, v) \ge 5$.
- **Self-Connections (Autapses)**: $u \to u$ self-loops are catalogued separately and excluded from dyad and motif counting.
- **Neuropil Slicing**: Regional subgraphs (EB, FB, PB) are induced by restricting connections to those located anatomically within each neuropil.

### Reciprocity Definitions
For a directed graph with $E$ directed edges (excluding self-loops):
1. **Mutual Dyads ($M$)**: Unordered pairs $\{u, v\}$ such that both $u \to v \in E$ and $v \to u \in E$.
2. **Mutual Directed Edges ($E_{\text{mutual}}$)**: The directed edges participating in reciprocal connections: $E_{\text{mutual}} = 2M$.
3. **Edge Reciprocity ($R_{\text{edge}}$)**: The proportion of directed edges that are reciprocated:
   $$R_{\text{edge}} = \frac{2M}{E}$$
4. **Dyad Reciprocity ($R_{\text{dyad}}$)**: For a graph with $D$ total connected dyads ($D = E - M$):
   $$R_{\text{dyad}} = \frac{M}{D} = \frac{M}{E - M}$$

At threshold $w \ge 5$ in the Ellipsoid Body:
- $N = 483$ active neurons
- $E = 15,812$ directed edges
- $M = 3,518$ mutual dyads ($E_{\text{mutual}} = 7,036$)
- $R_{\text{edge}} = 44.50\%$
- $R_{\text{dyad}} = 28.62\%$

---

## 4. Deconstructing the Unconditioned Edge-Swap Null Model

### The Artifact
An initial configuration-model analysis using directed edge swapping (Marlon–Sonnenschein / Maslov–Sneppen degree-preserving randomization) reported an apparent **$6.78\times$ enrichment** of $\text{GABA} \leftrightarrow \text{GABA}$ mutual dyads in the EB.

### The Mechanism of Confounding
Audit of the edge-swapped networks revealed that degree-preserving rewiring severely collapses higher-order clustering and reciprocity:
* **Empirical EB Edge Reciprocity**: $R_{\text{edge}} = 44.50\%$ ($M = 3,518$ mutual dyads).
* **Rewired Edge Reciprocity**: $R_{\text{edge}} = 9.66\% \pm 0.17\%$ ($M_{\text{null}} \approx 764$ mutual dyads).
* **Topological Reciprocity Collapse Factor**: $44.50 / 9.66 = \mathbf{4.607\times}$.

Because the edge-swap null destroys $78\%$ of the physical mutual dyads, any unconditioned count of reciprocal dyads in the rewired network evaluates two conflated phenomena simultaneously:
$$\text{Unconditioned Motif Ratio} \approx (\text{Topological Reciprocity Excess}) \times (\text{Chemical Pairing Excess})$$
$$\frac{2,615}{385.7} \approx 6.78\times \approx 4.61 \times 1.47$$

Presenting the $6.78\times$ figure as an estimate of neurotransmitter-pair affinity is statistically invalid.

---

## 5. Protected Method: Conditional Degree-Stratified Label Permutation

To rigorously isolate chemical partner preference from graph topology, we implemented **conditional label-permutation null models**:

1. **Topology Held Invariant**: The empirical mutual dyad graph $\mathcal{M} = (V, M)$ is held strictly fixed ($M = 3,518$ constant). No edges are rewired.
2. **Whole-Neuron Transmitter Conservation**: Each neuron's consensus neurotransmitter prediction (assigned by plurality of connection-level weights) is held constant as a single discrete label.
3. **Degree-Stratified Permutation**: Transmitter labels are permuted across nodes **only within defined degree strata**. This preserves the correlation between neuronal degree and transmitter class.
4. **Statistical Evaluation**: Across $B = 2,000$ permutations (reproducible seed), the test statistic is the count of $\text{GABA} \leftrightarrow \text{GABA}$ mutual dyads:
   $$T = \sum_{\{u, v\} \in M} \mathbb{I}(\tau_u = \text{GABA} \land \tau_v = \text{GABA})$$
   Empirical $p$-values are computed with exact finite-sample correction:
   $$p = \frac{\sum_{b=1}^B \mathbb{I}(|T^{(b)} - \mu| \ge |T_{\text{obs}} - \mu|) + 1}{B + 1}$$

---

## 6. Controlled Results Across Degree-Stratified Null Models

We evaluated three alternative degree-stratification schemes to assess sensitivity to binning resolution:

| Model ID | Strata Definition | Strata Count | Permutation Mobility | Null Mean ($\pm \text{SD}$) | Observed Dyads | Conditional Enrichment | Effect Size ($Z$) | Empirical $p$-value |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Model 1** | Mutual-Degree Quartiles (Phase 6 Baseline) | 4 | $100\%$ (483 / 483) | $2,167.11 \pm 29.31$ | 2,615 | **$1.2067\times$ (+20.7%)** | $+15.28$ | $0.000500$ ($q = 0.001749$) |
| **Model 2** | Joint Directed In $\times$ Out Tertiles (3x3 Grid) | 9 | $100\%$ (483 / 483) | $2,037.96 \pm 35.86$ | 2,615 | **$1.2831\times$ (+28.3%)** | $+16.09$ | $0.000500$ ($p \le 1/2001$) |
| **Model 3** | Joint Directed In $\times$ Out Medians (2x2 Grid) | 4 | $100\%$ (483 / 483) | $1,984.76 \pm 48.05$ | 2,615 | **$1.3175\times$ (+31.8%)** | $+13.12$ | $0.000500$ ($p \le 1/2001$) |

![Figure 1: EB GABA-GABA Mutual Dyad Association Across Degree-Stratified Null Models](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure1_conditional_gaba_associations.svg)

### Model Interpretation:
* **Statistical Stability**: Across all three specifications, the conditional enrichment consistently remains between **$+20.6\%$ and $+31.8\%$ excess** ($Z > +13$, $p = 0.000500$).
* **Model Differences**: Fine in/out degree tertile stratification shifts the null expectation downward from $\sim 2,167$ to $\sim 2,038$, increasing conditional enrichment from $1.206\times$ to $1.283\times$. This occurs because high-in/high-out bins capture higher proportions of GABAergic ring neurons.
* **Permutation Mobility**: Every stratum in the 9-stratum grid retains multi-transmitter representation (strata sizes: 18 to 106 nodes; 0 frozen strata).

---

## 7. Descriptive Cellular Composition from Pinned FlyWire v2.1.0 Annotations

Mapping the 483 active EB root IDs to `Supplemental_file1_neuron_annotations.tsv` reveals complete annotation coverage and the exact anatomical substrate of the statistical association:

* **Annotation Row Match**: $483 / 483$ active neurons ($100.00\%$) and $3,518 / 3,518$ mutual dyads ($100.00\%$).
* **Field Completeness**:
  - `hemibrain_type`: $479 / 483$ neurons ($99.17\%$). All $3,518$ mutual dyads have both endpoints annotated with a valid hemibrain base type ($100.00\%$ dyad coverage).
  - `cell_sub_class`: $332 / 483$ neurons ($68.74\%$). 151 neurons lack sub-class labels in FlyWire v2.1.0 (including columnar `EPG`, `PEN`, `PEG`, and tangential `ExR`).
  - `cell_type`: $15 / 483$ neurons ($3.11\%$). Central-complex cell types are catalogued in `hemibrain_type`.

![Figure 2: Descriptive Cellular Composition of EB Mutual Dyads](file:///home/trishal/ibelieveicanfly/results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.svg)

### A. Broad Sub-Class Pairings ($M = 3,518$)
- **Ring neuron $\leftrightarrow$ Ring neuron**: **$2,306$ dyads ($65.55\%$ of $M$)**. Every single ring-ring dyad is consensus GABA–GABA, accounting for **$88.18\%$ of all $2,615$ GABA–GABA mutual dyads**.
- **Missing $\leftrightarrow$ Missing ($639$ dyads, $18.16\%$)**: Comprises $305$ reciprocal compass loops (`EPG <-> PEN_a`: 163, `EPG <-> PEN_b`: 142), $161$ compass-to-tangential loops (`EPG <-> ExR`), $80$ homotypic columnar loops (`EPG <-> EPG`: 69), and $93$ other loops.
- **Ring neuron $\leftrightarrow$ Missing ($399$ dyads, $11.34\%$)**: Comprises $195$ ring-to-ExR loops and $134$ ring-to-EPG loops.
- **Columnar $\leftrightarrow$ Ring neuron ($109$ dyads, $3.10\%$)**: Connections between `EL` / `hDelta` neurons and ring neurons.
- **Columnar $\leftrightarrow$ Missing ($65$ dyads, $1.85\%$)**: Connections between `EL` and `EPG` / `ExR`.

### B. Dominant Homotypic Ring Neuron Subtypes
Across all 3,518 mutual dyads, **$2,171$ dyads ($61.71\%$) are strictly homotypic** (both endpoints share the exact same reported hemibrain base type).

Among the $2,615$ consensus GABA–GABA mutual dyads:
- **`ER2 <-> ER2`**: $458$ dyads ($17.51\%$ of GABA–GABA; $13.02\%$ of $M$)
- **`ER3d <-> ER3d`**: $445$ dyads ($17.02\%$ of GABA–GABA; $12.65\%$ of $M$)
- **`ER4d <-> ER4d`**: $274$ dyads ($10.48\%$ of GABA–GABA; $7.79\%$ of $M$)
- **`ER3w <-> ER3w`**: $243$ dyads ($9.29\%$ of GABA–GABA; $6.91\%$ of $M$)
- **`ER5 <-> ER5`**: $191$ dyads ($7.30\%$ of GABA–GABA; $5.43\%$ of $M$)
- **`ER3a <-> ER3a`** : $174$ dyads ($6.65\%$ of GABA–GABA; $4.95\%$ of $M$)
- **`ER3p <-> ER3p`**: $129$ dyads ($4.93\%$ of GABA–GABA; $3.67\%$ of $M$)
- **`ER3m <-> ER3m`**: $112$ dyads ($4.28\%$ of GABA–GABA; $3.18\%$ of $M$)
- **Top 8 Homotypic Subtotal**: **$2,026$ dyads ($77.48\%$ of GABA–GABA; $57.59\%$ of $M$)**
- **All 10 Homotypic Subtotal** (adding `ER4m` [49] and `ER1` [11]): **$2,086$ dyads ($79.77\%$ of GABA–GABA; $59.29\%$ of $M$)**

---

## 8. Biological Interpretation: Topology vs. Chemical Composition

1. **Physical Substrate of the Association**:
   The statistical persistence of $+20.6\%$ to $+28.3\%$ conditional GABA–GABA excess is physically grounded in the dense, all-to-all recurrence within discrete ring neuron morphological classes. Each ring neuron subclass arborizes in a distinct concentric layer of the Ellipsoid Body, making homotypic recurrence structurally dense.
2. **Modular Compass Segregation**:
   The apparent depletion of cross-transmitter $\text{ACh} \leftrightarrow \text{GABA}$ mutual dyads ($0.27\times$) reflects modular circuit organization: cholinergic compass neurons (`EPG <-> PEN`, 305 dyads) form a closed recurrent feedback loop dedicated to angular velocity propagation, interacting sparsely with ring neuron layers. This anatomical separation correlates with the low observed frequency of cross-transmitter dyads, but does not prove active molecular partner exclusion.

---

## 9. Methodological Limitations and Epistemic Guardrails

To maintain strict scientific calibration, the following limitations are explicitly noted:

1. **Single-Connectome Scope**:
   All data derive from a single adult female *Drosophila melanogaster* brain (FAFB v783). Cross-individual variability, developmental plasticity, and sexual dimorphism cannot be evaluated without independent connectomes (e.g., hemibrain or future male connectomes).
2. **Computational Neurotransmitter Predictions**:
   Neurotransmitter identities are computational consensus predictions from synapse-level machine learning models. Predicted GABA release does not demonstrate in vivo inhibitory postsynaptic currents, hyperpolarization, or receptor expression ($Rdl$ vs. others).
3. **Discrete Degree Stratification**:
   While sensitivity checks partitioned nodes into 9 joint tertile strata, the null models bin nodes rather than preserving exact node-by-node joint degree sequences. Degree variance remains within strata.
4. **Exploratory Same-Dataset Analysis**:
   The cell-type breakdowns and sensitivity models were developed iteratively on the same connectome dataset. Cell-type pair counts are descriptive anatomy, not an independent statistical hypothesis test.
5. **No Direct Evidence of Ring-Attractor Dynamics**:
   Static anatomical connectivity provides the physical wiring diagram but does not establish in vivo bump attractor dynamics, continuous heading representation, or physiological stability.

---

## 10. Approved Summary Verdict

> **"The EB GABA-GABA mutual-dyad association persisted under the tested degree-stratified label-permutation models. The magnitude varied with the null specification. The cell-type counts are descriptive and do not establish a new functional mechanism."**

---

## 11. Reproducibility and File Manifest

All analyses are deterministic and reproducible on standard laptop hardware (Dell Inspiron 5558, 8 GB RAM):

```bash
# 1. Run Automated Unit Test Suite (24 tests, ~0.1s)
.venv/bin/python3 -m unittest discover -s tests -v

# 2. Reproduce Phase 7 Sensitivity & Annotation Pipeline (~5s)
.venv/bin/python3 scripts/run_phase7_robustness_and_celltypes.py

# 3. Generate Presentation Figures (SVG & PNG, ~2s)
python3 scripts/generate_portfolio_figures.py
```

### Authoritative File Hashes (SHA-256)
| File Path | SHA-256 Checksum | Description |
|---|---|---|
| `data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv` | `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6` | Pinned FlyWire v2.1.0 Annotations |
| `results/real_data_pilot/phase7/eb_node_covariates.json` | `179cc472bd4066d90962814a597499b6008e97df145caccff961f9cd5fe88e3b` | Cached EB Node Covariates & Dyads |
| `results/real_data_pilot/phase7/phase7_robustness_and_celltypes.json` | `31f29f578cf404b20dae9fa5e67bed313e36b6af9e04cf685fd842f00973eee9` | Phase 7 Structured Results Artifact |
| `results/real_data_pilot/phase6/phase6_controlled_study_results.json` | `0ecb390aad40872bcbf2da70c24295fdbce628c71724986a5357d36b1d2a5d1b` | Phase 6 Regional Controlled Study Results |
| `scripts/run_phase6_controlled_study.py` | `cdd3718d622049c0b1c2fd7b11fffa29b5901c45e376ae0135ac57096a68af5c` | Phase 6 Analysis Pipeline |
| `scripts/run_phase7_robustness_and_celltypes.py` | `151d99c189091df44047f1c71c0432664923942eb0c06312f6f8a57011d48190` | Phase 7 Sensitivity & Annotation Pipeline |
| `scripts/generate_portfolio_figures.py` | `ce8c90949501f6fd1a7f3623bc7ec861f56cc37fd4e8a03cc410148d3fe0cfd4` | Portfolio Presentation Figure Generator |
| `tests/test_preliminary_analysis.py` | `f0a13447adfc5139989b4f84886db3ce143ce4e33c23feab1f87c03b9449a716` | Automated Unit Test Suite (24/24 passing) |
| `results/real_data_pilot/phase8/figure1_conditional_gaba_associations.svg` | `1f0b9f2d68a6de5069e91b09b44e87f55328298bd9d12aea19d06008e6056fdb` | Presentation Figure 1 (Vector SVG) |
| `results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.svg` | `bff9374d4834af99b16a00398f75a0d96858ff0c347675a794bedfdd33abacd9` | Presentation Figure 2 (Vector SVG) |

---

## 12. References
1. Dorkenwald, S. et al. (2024). Neuronal wiring diagram of an adult brain. *Nature*, 634, 124–138.
2. Schlegel, P. et al. (2024). Whole-brain annotation and multi-connectome cell typing of *Drosophila*. *Nature*, 634, 139–152.
3. Eckstein, N. et al. (2024). Neurotransmitter classification from electron microscopy images. *Cell*, 187, 2525–2541.
4. Hulse, B. K. et al. (2021). A connectome of the *Drosophila* central complex reveals network motifs suitable for flexible navigation and context-dependent action. *eLife*, 10, e66039.
5. Maslov, S. & Sneppen, K. (2002). Specificity and stability in topology of protein networks. *Science*, 296, 910–913.
6. Benjamini, Y. & Hochberg, Y. (1995). Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J. R. Stat. Soc. B*, 57, 289–300.
