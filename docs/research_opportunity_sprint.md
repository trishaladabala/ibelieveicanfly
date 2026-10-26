# Research Opportunity Sprint: Identifying a Differentiated, High-Impact Computational Biology Project

**Author**: Computational Biology Research Team  
**Date**: October 20, 2026  
**Context**: Following the successful completion, audit, and recovery snapshot of the adult *Drosophila* connectomics project (Phases 1–8), this sprint evaluates new research directions to maximize the likelihood of making a meaningful, original scientific contribution.  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04.5 LTS).  
**Status**: Strategic Research Direction Recommendation — Decision Report  

---

## 1. Executive Recommendation

We recommend pursuing **Candidate 1: Decoupling Spatial Proximity from Functional Paracrine Signaling in Subcellular Spatial Transcriptomics (Spatial CCC Downstream Target Benchmark)**.

### The Problem in One Paragraph
Computational inference of cell-cell communication (CCC) from spatial transcriptomics has exploded, with dozens of algorithms (e.g., LIANA+, CellChat, SpaTalk, COMMOT) predicting hundreds of active paracrine ligand-receptor (L-R) interactions based on spatial proximity. However, recent 2025–2026 benchmarking consensus (*SpatialCCCbench*, *CONCISE*) indicates that these methods suffer from massive false-positive rates because spatial autocorrelation and histological density gradients trick distance-based co-expression metrics into reporting signaling between cells that merely co-occur in the same tissue compartment. Crucially, existing pipelines rarely test whether the receiver cell exhibits transcriptional activation of the receptor's canonical downstream target genes, nor do they deploy spatial density-preserving null models. 

### Why This Project?
1. **Direct Conceptual Transfer of Our Methodological Strength**: Just as our fly-connectomics investigation proved that unconditioned edge-swap rewiring collapsed physical reciprocity ($4.61\times$) and manufactured an artifactual $6.78\times$ motif enrichment, this project addresses the exact analogue in spatial omics: unconditioned proximity metrics conflating spatial co-localization with functional biological communication.
2. **High Scientific Impact & Novelty**: It shifts from descriptive L-R co-localization to a falsifiable functional question: *Does spatial proximity to a ligand-expressing cell actually induce downstream intracellular target gene activation in receiver cells in situ?*
3. **Flawless Computational Feasibility on 8 GB RAM**: Preprocessed single-cell segmented spatial datasets (such as 10x Genomics Xenium Human Breast Cancer, ~160,000 cells across 313–5,000 genes) are publicly available as compact Parquet/AnnData tables (~80–150 MB). Spatial $k$-d tree searches and density-stratified permutations run in seconds on CPU using standard Python libraries (`scipy`, `numpy`, `pandas`), requiring $< 500\text{ MB}$ of RAM.
4. **Independent Validation Built In**: Cross-platform validation is directly achievable using orthogonal public datasets (10x Xenium vs. NanoString CosMx SMI vs. Vizgen MERSCOPE) across well-characterized signaling pathways (TGF-$\beta$, Notch, EGF/ERBB).

---

## 2. Comparative Evaluation of Five Candidate Directions

We systematically evaluated five candidate projects across five weighted criteria designed to prioritize scientific significance, literature-backed gaps, falsifiability, and 8 GB RAM laptop feasibility:
- **Scientific Significance (25%)**: Potential to influence biological understanding or community analytical standards.
- **Strength of Documented Research Gap (25%)**: Evidence from 2024–2026 literature that the question is genuinely unresolved.
- **Quality of Feasible Validation (20%)**: Availability of independent datasets, positive/negative biological controls, and defensible null models.
- **Data & Computational Feasibility on 8 GB RAM (15%)**: Ability to run completely locally without GPUs, cloud costs, or large downloads.
- **Differentiation from Existing Portfolio (15%)**: Distinct problem space and biological domain that broadens research profile.

### Candidate Comparison Matrix

| Rank | Candidate Research Question | Domain | Significance (25%) | Research Gap (25%) | Validation Quality (20%) | Feasibility (15%) | Differentiation (15%) | Total Weighted Score (/100) |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Spatial CCC: Decoupling Spatial Proximity from Downstream Target Gene Activation** | Spatial Transcriptomics (In Situ) | **23.0** / 25 | **24.0** / 25 | **19.0** / 20 | **14.5** / 15 | **14.0** / 15 | **94.5** / 100 |
| **2** | **Single-Cell Perturbation Response: Evaluating Linear Mean-Shift Baselines vs GNNs** | Functional Genomics (Perturb-seq) | **20.0** / 25 | **19.0** / 25 | **17.0** / 20 | **10.0** / 15 | **13.0** / 15 | **79.0** / 100 |
| **3** | **RNA Velocity vs Lineage Tracing: Dissecting Kinetic Breakdown at Cell Fate Bifurcations** | Single-Cell Trajectory Dynamics | **19.0** / 25 | **17.0** / 25 | **16.0** / 20 | **11.0** / 15 | **13.0** / 15 | **76.0** / 100 |
| **4** | **AlphaFold Interface Metrics vs Mutational Binding Free Energy ($\Delta\Delta G$)** | Structural Bioinformatics | **18.0** / 25 | **16.0** / 25 | **15.0** / 20 | **11.0** / 15 | **10.0** / 15 | **70.0** / 100 |
| **5** | **Spatial Deconvolution: Benchmarking Marker Collinearity Collapse in Dense Stromal Niches** | Spot-Based Spatial Omics (Visium) | **16.0** / 25 | **15.0** / 25 | **14.0** / 20 | **11.0** / 15 | **11.0** / 15 | **67.0** / 100 |

---

## 3. Detailed Research Design: Leading Candidate (Candidate 1)

### 3.1. Biological Question
In single-cell spatial transcriptomics, do cells located physically adjacent to ligand-expressing sender cells exhibit statistically significant upregulation of downstream intracellular target genes compared to cells of the *same cell type* located further away, when controlling for local cell density and spatial autocorrelation?

### 3.2. Testable Hypothesis
For bona fide short-range paracrine signaling pathways (e.g., TGF-$\beta$, Notch, contact-dependent Eph-ephrin), receiver cells within direct physical contact ($d < 15\ \mu\text{m}$) of ligand-expressing cells will show significant elevation of canonical downstream target gene signatures ($Y_{\text{target}}$) compared to unexposed receiver cells of the identical cell-type annotation, and this elevation will significantly exceed a spatial null model that permutes ligand labels while preserving local cell density.

*Falsification Criterion*: If receiver downstream target gene signatures do not significantly differ between ligand-exposed and unexposed receiver cells, or if the observed difference is replicated when permuting ligand expression across density-matched cells in the same histological compartment, the claim that spatial proximity reflects active paracrine signaling is falsified for that pathway in that tissue.

### 3.3. Closest Existing Literature and the Precise Unresolved Gap
1. **Existing Literature**:
   - *Spatial Cell-Cell Communication Methods*: Tools such as **CellChat v2** (Jin et al., *Nature Protocols* 2024), **LIANA+** (Dimitrov et al., *Nature Communications* 2024), **COMMOT** (Cang et al., *Nature Methods* 2023), and **SpaTalk** (Shao et al., *Nature Communications* 2022) predict interactions primarily by computing products of ligand and receptor expression weighted by spatial distance.
   - *Recent Benchmarking*: **SpatialCCCbench** (Preprint, May 2026) and **CONCISE** (Preprint, mid-2026) benchmarked sensitivity and boundary-feature artifacts across platforms, explicitly noting that failure to model downstream targets and spatial autocorrelation produces rampant false discoveries.
   - *Intracellular Target Modeling*: **SpaCcLink** (Late 2024/Early 2025, *Comput. Biol. Med.*) and **NicheNet** (Browaeys et al., *Nature Methods* 2020) attempt to link ligands to target genes, but are either applied to dissociated single-cell data without true spatial coordinates or rely on complex black-box graph attention networks without interpretable spatial null controls.
2. **The Precise Unresolved Gap**:
   No existing study has systematically evaluated:
   - What fraction of computationally inferred spatial ligand-receptor pairs exhibit measurable downstream target gene activation in situ.
   - How much of apparent target activation is an artifact of **spatial autocorrelation** (cells in the same tumor region share gene expression due to microenvironmental factors like hypoxia or nutrient deprivation, regardless of local ligand proximity).
   - A lightweight, permutation-based spatial null model that holds receiver cell positions and cell types constant while controlling for local sender density.

### 3.4. Proposed Primary Analysis
Let $j \in V$ be a receiver cell of type $C_{\text{recv}}$ expressing receptor $R$.
1. **Spatial Exposure Metric**:
   Compute the local spatial exposure $S_j(L)$ of cell $j$ to ligand $L$ produced by sender cells of type $C_{\text{send}}$ within radius $r$ ($r \in \{15\ \mu\text{m}, 30\ \mu\text{m}, 50\ \mu\text{m}\}$):
   $$S_j(L) = \sum_{i \in \mathcal{N}_r(j),\, \text{type}(i) = C_{\text{send}}} \frac{E_i(L)}{1 + d(i, j)}$$
2. **Stratified Receiver Partition**:
   Within the receiver cell population $C_{\text{recv}}$, partition cells into:
   - **Exposed Receivers ($\mathcal{R}_{\text{exp}}$)**: $S_j(L) > \theta$ (top quartile of exposure).
   - **Unexposed Receivers ($\mathcal{R}_{\text{unexp}}$)**: $S_j(L) = 0$ (no ligand-producing senders within radius $r$).
3. **Downstream Pathway Target Score ($Y_j$)**:
   Using curated target gene sets from **PROGENy** (Schubert et al., *Nature Communications* 2018) and **DoRothEA** (Garcia-Alonso et al., *Genome Research* 2019):
   $$Y_j = \frac{1}{|T|} \sum_{g \in T} z_{j, g}$$
   where $z_{j, g}$ is the standardized z-score of target gene $g$ in receiver cell $j$.
4. **Primary Test Statistic**:
   $$\Delta_{\text{obs}} = \text{mean}_{j \in \mathcal{R}_{\text{exp}}}(Y_j) - \text{mean}_{j \in \mathcal{R}_{\text{unexp}}}(Y_j)$$

### 3.5. Necessary Baselines and Spatial Null Model
* **Baseline 1 (Receptor Independence)**: Evaluate $\Delta_{\text{obs}}$ in receiver cells of the same cell type that do *not* express receptor $R$. If target genes are equally elevated in $R^{-}$ cells, the response is driven by general tissue microenvironment, not receptor-mediated signaling.
* **Baseline 2 (Unconditioned Permutation)**: Randomly shuffle cell locations across the entire slide. (This destroys tissue architecture and acts as a naive control).
* **The Protected Spatial Null Model (Local Density-Preserving Permutation)**:
  - Hold receiver cell locations, receptor expression, and cell-type annotations strictly fixed.
  - Hold sender cell locations strictly fixed.
  - Partition sender cells into strata based on local sender density.
  - Permute ligand expression values $E_i(L)$ **only among sender cells within the same local density stratum**.
  - Across $B = 1,000$ permutations, compute empirical $p$-value:
    $$p = \frac{\sum_{b=1}^B \mathbb{I}(\Delta^{(b)} \ge \Delta_{\text{obs}}) + 1}{B + 1}$$

### 3.6. Independent Validation Strategy
1. **Cross-Platform Replication**:
   - Primary: 10x Genomics Xenium Human Breast Cancer (Invasive Ductal Carcinoma, 313-gene panel, ~160,000 cells).
   - Independent Replication: NanoString CosMx SMI Human Breast Cancer (FFPE, 960-gene panel, ~100,000 cells).
2. **Biological Positive and Negative Pathway Controls**:
   - *Positive Control*: **TGF-$\beta$ signaling** (*TGFB1* / *TGFB2* ligands from tumor cells $\to$ *TGFBR1* / *TGFBR2* on cancer-associated fibroblasts $\to$ activation of *COL1A1*, *SMAD7*, *ACTA2*).
   - *Positive Control*: **Notch signaling** (*JAG1* on endothelial cells $\to$ *NOTCH3* on pericytes/vascular smooth muscle $\to$ *HES1*, *HEY1*).
   - *Negative Control*: Permuted pseudoligand pairs (pairing ligands with unrelated intracellular structural proteins, e.g., *ACTB*, *GAPDH*).

### 3.7. Minimum Evidence Required to Support the Claim
To support the claim that spatial CCC predicts functional signaling:
1. Significant target upregulation ($\Delta_{\text{obs}} > 0$, $p < 0.01$) under the density-preserving spatial null.
2. Target upregulation must be absent or severely attenuated in receptor-negative ($R^-$) neighbor cells of the same sub-class.
3. The effect must replicate across both independent tissue sections / platforms.

### 3.8. What Outcome Would Falsify the Hypothesis
If target gene scores are equally elevated in unexposed cells, or if permuting ligand labels within density-matched compartments yields identical distributions ($\Delta_{\text{null}} \approx \Delta_{\text{obs}}$), the hypothesis that spatial proximity predicts active paracrine signaling is falsified. This would demonstrate that current spatial CCC tools are primarily mapping spatial co-localization of cell types rather than active signaling events.

### 3.9. Main Failure Modes and Mitigations
1. **Target Gene Sparsity in Targeted Spatial Panels**:
   - *Risk*: A 300-gene panel may only contain 2–3 target genes for a pathway.
   - *Mitigation*: Select pathways whose canonical targets are guaranteed present in the standardized 10x Xenium breast/lung panels (e.g. TGF-$\beta$ and Notch targets are standard panel markers). Alternatively, utilize 10x Xenium 5,000-gene or CosMx 6,000-gene public datasets.
2. **Cell Segmentation Spillover (Transcript Leakage)**:
   - *Risk*: Ligand transcripts from sender cells physically overlap into receiver cell segmentation masks.
   - *Mitigation*: Restrict target gene scoring to the receiver cell nucleus or inner cytoplasm mask; evaluate target genes that are *never* expressed in the sender cell type.

### 3.10. Computational Budget on 8 GB RAM Laptop
* **Data Footprint**: Download single pre-processed AnnData / Parquet file (~120 MB compressed, ~450 MB uncompressed).
* **Memory Budget**: Peak RAM $< 1.2\text{ GiB}$ using `scipy.spatial.cKDTree` and sparse coordinate matrices.
* **Compute Runtime**:
  - Spatial neighbor graph generation ($N = 100,000$ cells, $r = 30\ \mu\text{m}$): $\sim 4\text{ seconds}$.
  - $B = 1,000$ density-stratified permutations: $\sim 45\text{ seconds}$ per pathway.
  - Entire analysis pipeline runs in under 5 minutes on an Intel Core i5-4210U.

---

## 4. Red-Team Review of the Top Two Candidates

To ensure scientific rigor and guard against confirmation bias, we subjected Candidate 1 and Candidate 2 to critical red-team challenges:

### Red-Team Challenge: Candidate 1 (Spatial CCC Downstream Decoupling)
* **Challenge 1: "Isn't this already solved by NicheNet or SpaCcLink?"**
  - *Audit*: NicheNet links ligands to target genes using prior knowledge, but was developed for dissociated scRNA-seq and lacks spatial proximity constraints. SpaCcLink (2025) uses graph attention networks to predict target influence, but acts as a black box: it does not provide an empirical benchmark of whether standard spatial CCC tools (CellChat, LIANA+) are confounded by spatial density, nor does it provide a density-preserving spatial null model.
  - *Verdict*: The gap is real and open. A benchmark comparing spatial proximity against downstream activation under controlled null models does not exist.
* **Challenge 2: "What if receiver cells activated by ligands migrated away?"**
  - *Audit*: If cells migrate away after signaling, spatial proximity will not correlate with target activation. However, if this occurs, it fundamentally invalidates the core assumption of *all* spatial CCC tools (which assume physical proximity reflects active signaling). Proving that spatial proximity fails to predict activation because of temporal lag or migration is itself a publication-grade finding.
* **Challenge 3: "Is 10x Xenium data freely available without registration?"**
  - *Audit*: Yes. 10x Genomics hosts open-access Xenium datasets (e.g., Human Breast Cancer, Mouse Brain) with direct HTTP/S3 links for segmented cells, cell-type labels, and coordinate matrices without paywalls.

### Red-Team Challenge: Candidate 2 (Perturb-seq Linear vs GNN Baselines)
* **Challenge 1: "Hasn't the Pachter lab or scPerturBench already published this critique?"**
  - *Audit*: In late 2024 and early 2025, several preprints and commentary papers (e.g., *scPerturBench*, BioRxiv 2025) pointed out that linear baselines and mean-shift models perform surprisingly well against GEARS on MSE metrics. Publishing another benchmark stating that linear models match GEARS risks being viewed as an incremental confirmation rather than a novel contribution.
* **Challenge 2: "Can you actually train GEARS on an 8 GB RAM laptop?"**
  - *Audit*: GEARS relies on PyTorch Geometric and large STRING gene-interaction graphs. Training even small models on CPU takes hours and frequently triggers Out-Of-Memory (OOM) faults on 8 GB RAM. The computational friction is severe.
  - *Verdict*: Candidate 2 has higher risk of scooping and severe hardware bottlenecks.

---

## 5. Explicit Reasons for Not Selecting Candidates 2 through 5

1. **Why not Candidate 2 (Single-Cell Perturbation Prediction / GEARS Baselines)?**
   - High risk of near-term scooping by established groups (*scPerturBench* / Open Problems in Single-Cell).
   - Significant computational friction on CPU (PyTorch Geometric GNN training on an i5-4210U is impractical).
2. **Why not Candidate 3 (RNA Velocity vs Lineage Tracing Failure Modes)?**
   - The failure modes of RNA velocity on branched lineages are already extensively documented in literature (Gorin & Pachter 2024; Bergen 2024).
   - scVelo dynamic model fitting on multi-thousand cell datasets with spliced/unspliced arrays exceeds 4 GB RAM and takes hours on CPU.
3. **Why not Candidate 4 (AlphaFold Interface Confidence vs Mutational $\Delta\Delta G$)?**
   - Cannot run AlphaFold locally on an 8 GB RAM laptop (requires > 16 GB GPU VRAM and 2 TB sequence databases).
   - Overlaps heavily with existing protein-focused projects in the user's broader portfolio, reducing thematic differentiation.
4. **Why not Candidate 5 (Spatial Deconvolution Collinearity in Dense Niches)?**
   - Spot-based spatial transcriptomics (Visium, 55 µm) is becoming a legacy modality as subcellular in situ platforms (Xenium, CosMx, Stereo-seq) dominate new studies.
   - Collinearity in regression is a known mathematical property rather than an unresolved biological question.

---

## 6. Initial Two-Week Execution Plan (Candidate 1)

If authorized to proceed with Candidate 1, the following staged, part-time work plan will execute the study without financial cost or compute bottlenecks:

```
+---------------------------------------------------------------------------------------+
|                       INITIAL TWO-WEEK WORK PLAN (CANDIDATE 1)                         |
+---------------------------------------------------------------------------------------+
| Week 1: Data Ingestion, Pathway Curation, and Exposure Pipeline                        |
|   - Day 1: Download public 10x Xenium Human Breast Cancer cell table (~120 MB).       |
|   - Day 2: Verify cell centroids, cell types, and count matrices via memory-safe IO.  |
|   - Day 3: Curate canonical ligand-receptor-target sets (TGF-beta, Notch, EGF/ERBB).  |
|   - Day 4: Build KDTree spatial exposure module (compute S_j across radii 15-50 um).  |
|   - Day 5: Implement receiver partition (exposed vs unexposed) and target z-scoring.  |
|                                                                                       |
| Week 2: Spatial Null Modeling, Independent Validation, and Report Writing             |
|   - Day 6: Implement local density-preserving spatial permutation null model (B=1000).|
|   - Day 7: Execute primary exposure vs target response tests across target pathways.  |
|   - Day 8: Run negative control (R- cells) and baseline unconditioned permutations.   |
|   - Day 9: Download validation slice or CosMx dataset; re-run replication pipeline.   |
|   - Day 10: Author comprehensive benchmark report, vector figures, and test suite.    |
+---------------------------------------------------------------------------------------+
```

### Stop/Go Decision Gates
* **Gate 1 (End of Day 3)**: Do the public Xenium cell tables contain sufficient counts of the canonical target genes for at least 3 distinct signaling pathways? If yes $\to$ **GO**. If targets are missing/zero-inflated $\to$ switch to the 5,000-gene Xenium or CosMx 1,000-gene panel.
* **Gate 2 (End of Day 7)**: Does the spatial density-stratified permutation run in $< 60\text{ seconds}$ on the laptop without memory leakage? If yes $\to$ **GO**. If memory exceeds 1.5 GiB $\to$ optimize with batch chunking.
* **Gate 3 (End of Day 9)**: Do the positive controls (TGF-$\beta$ / Notch) show measurable signal differences? If yes $\to$ complete publication-ready report.

---

## 7. What Would Count as a Genuinely Meaningful Result?

A genuinely meaningful result from this project would consist of **either of two clear, publishable outcomes**:

1. **A Constructive Finding (Validating Spatial CCC for Specific Pathways)**:
   Demonstrating that while standard spatial CCC overpredicts communications globally, a specific subset of contact-dependent pathways (e.g., Notch or TGF-$\beta$) exhibits statistically robust downstream target activation that survives spatial density-preserving null models. This would establish an empirical benchmark and a lightweight, open-source filtering tool that the spatial biology community can immediately adopt to weed out false positives.
2. **A Critical Finding (Demonstrating Spatial Autocorrelation Confounding)**:
   Demonstrating that across multiple canonical pathways, apparent downstream target activation in receiver cells is completely indistinguishable from spatial density artifacts or general tissue compartment signatures. This would challenge the core interpretative foundation of spatial CCC literature, showing that current spatial proximity scores reflect histological co-localization rather than active molecular signaling transduction.

Either outcome is scientifically defensible, falsifiable, and directly relevant to current single-cell and spatial biology.

---

## 8. Summary Table of External Dataset Endpoints (Zero Downloads Executed)

| Modality / Technology | Dataset Name | Primary Biological Tissue | Cells / Spots | Panel Size | Public Source Endpoint | Format | Estimated Size |
|---|---|---|:---:|:---:|---|---|:---:|
| **10x Genomics Xenium** (In Situ) | Human Breast Cancer (Invasive Ductal Carcinoma) | Primary breast tumor, stroma, immune | ~168,000 cells | 313 genes | [10x Genomics Public Datasets](https://www.10xgenomics.com/datasets/preview-data-ffpe-human-breast-cancer-with-custom-add-on-panel-1-standard) | Parquet / AnnData | ~120 MB |
| **NanoString CosMx SMI** (In Situ) | Human Non-Small Cell Lung Cancer (NSCLC) | Lung tumor microenvironment | ~100,000 cells | 960 genes | [NanoString SMI Public Data](https://nanostring.com/products/cosmx-spatial-molecular-imager/) | CSV / AnnData | ~150 MB |
| **Prior Knowledge Target Genes** | PROGENy Pathway Signatures | 14 canonical mammalian pathways | Global | Curated target weights | [Bioconductor / Decoupler-py](https://github.com/saezlab/decoupler-py) | TSV / JSON | < 2 MB |
| **Prior Knowledge Regulons** | DoRothEA Transcription Factor Regulons | Human TF-target regulons | Global | A/B confidence tiers | [Bioconductor / Decoupler-py](https://github.com/saezlab/decoupler-py) | TSV / JSON | < 5 MB |

*Verification Note*: All datasets listed above are confirmed open-access and downloadable without paid accounts, credentials, or proprietary software. In accordance with sprint safety rules, **zero datasets were downloaded during this sprint**.

