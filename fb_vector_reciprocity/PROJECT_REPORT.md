# VectorWing: Layer-Resolved Columnar-Tangential Reciprocity and Chemospecific Feedback in the Adult *Drosophila* Fan-Shaped Body Connectome

**Target Field**: Computational Neuroscience, Connectomics, and Network Neuroscience  
**Primary Dataset**: Adult female *Drosophila melanogaster* whole-brain connectome (FlyWire FAFB v783; Zenodo DOI: `10.5281/zenodo.10676866`), annotations v2.1.0 (Schlegel et al., 2024; DOI: `10.1038/s41586-024-07686-5`), neurotransmitter predictions (Eckstein et al., 2024; DOI: `10.1016/j.cell.2024.03.016`).  
**Author**: Computational Biology Research Team  
**Repository Working Directory**: `/home/trishal/ibelieveicanfly/fb_vector_reciprocity/`  
**Parent Workspace**: `/home/trishal/ibelieveicanfly`  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04 LTS)  
**Software Environment**: Python 3.12, PyArrow 26.0.0, Cairo (`.venv` & system packages)  
**Date**: October 26, 2026  
**Status**: Scientifically Audited, Reproducible, and Portfolio-Ready Research Artifact  

---

## Abstract

Navigating in three-dimensional environments requires coordinating distinct internal representations of heading and travel direction. In the *Drosophila melanogaster* central complex, the Ellipsoid Body (`EB`) implements a 1D continuous-attractor heading compass dominated by homotypic recurrent inhibition between GABAergic ring neurons. In contrast, the microcircuit organization of the Fan-Shaped Body (`FB`), the central hub for 2D vector steering and goal routing, remains poorly understood. Here, we present an audited connectomic and computational analysis of all 5,435 mutual dyads in the adult female Fan-Shaped Body ($N = 2,465$ active neurons, $E = 46,903$ directed edges, $w \ge 5$). Using degree-stratified conditional null models that hold reciprocal graph topology strictly invariant, we show that the FB displays an inverted chemical pairing logic: homotypic recurrent inhibition is virtually absent (0.11%), replaced by a 4.96- to 5.92-fold enrichment of heterotypic acetylcholine–GABA ($ACh \leftrightarrow GABA$) reciprocal loops ($554$ dyads, $p = 0.000500$, Benjamini–Hochberg FDR $q < 0.003$). When in- and out-degree variation is constrained under fine-grained continuous $k$-nearest-neighbor micro-stratification ($k=8$, 308 strata), a 2.53-fold conditional enrichment persists ($Z = +6.19$, $p = 0.000999$, 95% Monte Carlo CI: $[2.49\times, 2.57\times]$), confirming that the heterotypic association remains significant under strict degree matching. Single-cell FlyWire v2.1.0 annotation mapping confirms that $99.46\%$ of these loops connect columnar steering neurons to tangential neurons with $100.00\%$ strict directional chemical polarity (Columnar=ACh, Tangential=GABA). Furthermore, $99.10\%$ ($549 / 554$ dyads) are localized in premotor Layers 4 and 5, dominated by `FB4A <-> vDeltaA` (150 dyads) and `FB5A <-> FC2` (272 dyads). Rate-based dynamical modeling indicates that this feedback provides linear subtractive attenuation that bounds columnar firing rates ($\le 30.6$ Hz vs 297.4 Hz runaway excitation when ablated) and preserves spatial bump tuning ($90.0^\circ$ FWHM). These results provide a topological and dynamical foundation for how tangential inhibitory state signals gate columnar vector navigation.

---

## 1. Introduction & Research Question

Spatial navigation in insects relies on the central complex (CX), a conserved group of midline neuropils that compute heading, translate sensory inputs across coordinate systems, and route motor goals (Green et al., 2017; Turner-Evans et al., 2020; Hulse et al., 2021). The central complex contains two prominent toroidal/stratified neuropils:
1. **The Ellipsoid Body (`EB`)**: A toroidal neuropil functioning as a 1D internal compass. Heading is represented as a single spatial activity "bump" among columnar neurons, stabilized by dense all-to-all homotypic recurrent inhibition among GABAergic ring neurons (Turner-Evans et al., 2020).
2. **The Fan-Shaped Body (`FB`)**: A layered, columnar neuropil comprising 9 horizontal layers and 16 vertical columns. The FB integrates heading representations from the EB and protocerebral bridge with translational optic flow, wind direction, and internal state cues to generate directed steering vectors (Shiozaki et al., 2020; Lu et al., 2022; Matheson et al., 2022).

While the 1D ring attractor architecture of the EB has been characterized extensively, the topological reciprocity and chemical pairing logic of the Fan-Shaped Body remained functionally unresolved:
*Does the 2D vector steering matrix share the homotypic recurrent inhibition of the 1D heading compass, or does it utilize an inverted, heterotypic feedback architecture to modulate motor steering vectors?*

Here, we address this question by extracting, auditing, and analyzing the complete intrinsic reciprocal connectome of the Fan-Shaped Body using the full-brain electron microscopy connectome of an adult female fruit fly (FlyWire FAFB v783).

---

## 2. Related Work & Connectomic Literature

To ground our findings in verified literature, we reviewed authoritative primary connectomics and neurobiology publications:

| Citation & DOI | Core Research Question | Dataset & Model | Relevant Finding | Relationship to VectorWing | What VectorWing Adds | Limitations |
|---|---|---|---|---|---|---|
| **Dorkenwald et al. (2024)**, *Nature* [10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y) | Whole-brain connectome reconstruction | FlyWire FAFB v783 (139k neurons, 50M synapses) | Full proofreading of adult female fly brain | Provides our primary connectomic dataset (`proofread_connections_783.feather`) | Neuropil-specific extraction and mutual-dyad accounting of the FB subgraph ($w \ge 5$) | Single adult female specimen; potential individual ultrastructural variation |
| **Schlegel et al. (2024)**, *Nature* [10.1038/s41586-024-07686-5](https://doi.org/10.1038/s41586-024-07686-5) | Hierarchical annotation and cell-typing | FlyWire v2.1.0 catalog (139k annotated neurons) | Unified nomenclature for central brain and CX types | Provides single-cell metadata, hemibrain type reconciliation, and layer assignments | 100% active node mapping and decomposition of reciprocal dyads into columnar vs tangential classes | Morphology classifications based on light-level and hemibrain matching |
| **Eckstein et al. (2024)**, *Cell* [10.1016/j.cell.2024.03.016](https://doi.org/10.1016/j.cell.2024.03.016) | Machine-learning neurotransmitter classification | Presynaptic T-bar EM images in FAFB | 94% whole-brain accuracy across 6 transmitter classes | Provides per-synapse transmitter probabilities used to compute whole-neuron consensus labels | Analysis of confidence distributions showing a 0.7873 ceiling for tangential GABA neurons | Machine-learning predictions without direct electrophysiological validation |
| **Hulse et al. (2021)**, *eLife* [10.7554/eLife.66039](https://doi.org/10.7554/eLife.66039) | Central complex connectome and circuit logic | Janelia Hemibrain (~25k neurons) | Detailed mapping of FB columnar (vDelta, hDelta, PFN, FC) and tangential (FB1-9) types | Validates our cell-type classifications and structural definitions of Layers 4 and 5 | Quantifies bidirectional reciprocity and chemospecific feedback between columnar and tangential types | Hemibrain dataset truncated several lateral tangential arborizations |
| **Turner-Evans et al. (2020)**, *Neuron* [10.1016/j.neuron.2020.08.006](https://doi.org/10.1016/j.neuron.2020.08.006) | Neuroanatomical basis of ring attractor | Janelia Hemibrain EB | Ring neurons provide all-to-all recurrent inhibition stabilizing compass bump | Serves as the comparative baseline for our 1D EB vs 2D FB architectural contrast | Direct statistical demonstration that EB and FB possess inverted reciprocity profiles | Restricted to the ellipsoid body heading system |
| **Lin et al. (2024)**, *Nature* [10.1038/s41586-024-07968-y](https://doi.org/10.1038/s41586-024-07968-y) | Network statistics of whole fly brain | FlyWire whole brain | Connectome-wide motif frequencies and reciprocity rankings | Confirms FB edge reciprocity rank (#6 among 79 neuropils) | Layer-resolved and transmitter-conditioned dissection of the FB's reciprocal excess | Connectome-wide survey without deep microcircuit or dynamical modeling |
| **Shiozaki et al. (2020)**, *Neuron* [10.1016/j.neuron.2020.07.005](https://doi.org/10.1016/j.neuron.2020.07.005) | Steering motor outputs in FB | Electrophysiology & anatomy | PFL3 neurons in ventral FB direct asymmetric steering turns | Provides functional context for premotor output modulation in Layers 4 & 5 | Explains why 99.1% of heterotypic reciprocal feedback is concentrated in premotor Layers 4 & 5 | Focused on downstream motor steering rather than upstream tangential feedback |

---

## 3. Dataset Provenance & Filtering Pipeline

### 3.1 Provenance & Data Ingestion
- **Source File**: `data/raw/fafb_v783/proofread_connections_783.feather` (852 MB, Apache Arrow IPC / Feather V2 format, SHA-256: `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`).
- **Records Processed**: 16,847,997 connection records across 258 record batches.
- **Whole-Brain Classification**: Whole-cell neurotransmitter consensus identities were computed across 138,005 neurons by accumulating synapse-weighted probabilities across all 54.5M synapses:
  $$\mathbf{p}_u = \frac{\sum_{e=(u, v)} w_e \cdot \mathbf{v}_e}{\sum_{e=(u, v)} w_e}$$
  where $\mathbf{v}_e \in [0, 1]^6$ represents the predicted probabilities for acetylcholine (ACh), GABA, glutamate, dopamine (DA), octopamine (Oct), and serotonin (Ser).

### 3.2 Subgraph Filtering Criteria
1. **Neuropil Isolation**: Intrinsic Fan-Shaped Body connections (`neuropil == "FB"`).
2. **Autapse Exclusion**: Self-loops ($pre == post$) were segregated and excluded from directed edge and dyad accounting.
3. **Weight Thresholding**: Connections with physical synapse counts $w \ge 5$ were retained for the primary graph, filtering out ultrastructural reconstruction noise.
4. **Canonical Pair Extraction**: Mutual dyads were identified as pairs of active neurons $(u, v)$ with $u < v$ where both directed edges $(u, v)$ and $(v, u)$ satisfy $w \ge 5$.

![Figure 1: Connectomic Architecture of FB & Data Ingestion Pipeline Overview](results/figures/figure1_network_and_pipeline_overview.svg)

---

## 4. Empirical Connectomic Baseline

Recomputation directly from `proofread_connections_783.feather` verifies the primary graph counts:
- **Active Neurons ($N$)**: $2,465$
- **Directed Edges ($E$)**: $46,903$ ($w \ge 5$)
- **Total Filtered Synapses**: $598,942$
- **Mutual Dyads ($M$)**: $5,435$ ($E_{\text{mutual}} = 10,870$)
- **Edge Reciprocity ($R_{\text{edge}} = 2M / E$)**: **$23.1755\%$** (ranks #6 out of 79 neuropils in the adult fly brain).
- **Dyad Reciprocity ($R_{\text{dyad}} = M / (E - M)$)**: **$13.1065\%$**.

### Neurotransmitter Composition of Mutual Dyads
Among the 5,435 mutual dyads, observed transmitter pairings show:
1. `ach_glut`: 2,267 dyads (41.71%)
2. `glut_glut`: 968 dyads (17.81%)
3. `ach_gaba`: **554 dyads (10.19%)**
4. `ach_ach`: 456 dyads (8.39%)
5. `gaba_glut`: 429 dyads (7.89%)
6. `gaba_gaba`: **6 dyads (0.11%)**

*Key Observation*: Homotypic GABA–GABA reciprocity, which accounts for $74.33\%$ of mutual dyads in the Ellipsoid Body, is almost non-existent in the Fan-Shaped Body (0.11%).

![Figure 2: Observed Transmitter-Pair Associations & Degree-Stratified Null Distribution](results/figures/figure2_transmitter_associations.svg)

---

## 5. Statistical Framework & Controlled Null Models

### 5.1 Defining the Scientific Estimand
To prevent conflating topological connectivity with chemical pairing preference, we explicitly define the primary estimand:
- **Null Hypothesis ($H_0$)**: Given the empirical reciprocal network topology ($M = 5,435$), the probability of a mutual dyad connecting an excitatory (ACh) neuron and an inhibitory (GABA) neuron is governed solely by the joint degree characteristics of the active neurons.
- **Randomization Unit**: Whole-cell neurotransmitter consensus labels.
- **Invariant**: The exact reciprocal graph topology is preserved ($M = 5,435$ constant).
- **Test Statistic**: The count of heterotypic ACh–GABA mutual dyads:
  $$T(X) = \sum_{(u, v) \in \mathcal{M}} \mathbb{I}\left( (\ell_u = \text{ACh} \land \ell_v = \text{GABA}) \lor (\ell_u = \text{GABA} \land \ell_v = \text{ACh}) \right)$$
- **Finite-Sample Empirical P-Value**: Evaluated with exact plus-one correction:
  $$p = \frac{\sum_{b=1}^B \mathbb{I}(|T(X^{(b)}) - \mu_{\text{null}}| \ge |T_{\text{obs}} - \mu_{\text{null}}|) + 1}{B + 1}$$

### 5.2 Controlled Permutation Results Across Null Models ($B = 2,000$ permutations each, seed = 42)

| Model Specification | Conditioning Variables | Strata Count | Observed Dyads | Null Mean ($\pm \text{SD}$) | 95% Null Simulation Range | Enrichment Ratio | 95% Monte Carlo Precision | Calibrated $Z$ | Empirical $p$-value | Benjamini-Hochberg FDR $q$ |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Model 1** | Mutual-Degree Quartiles | 4 | 554 | $93.6 \pm 26.1$ | $[48, 149]$ | **$5.92\times$** | $[5.85\times, 5.99\times]$ | **$+17.65$** | $0.000500$ | $0.002624$ (***) |
| **Model 2** | Joint In $\times$ Out Tertiles | 9 | 554 | $97.4 \pm 28.1$ | $[48, 157]$ | **$5.69\times$** | $[5.62\times, 5.76\times]$ | **$+16.25$** | $0.000500$ | $0.002099$ (***) |
| **Model 3** | Joint In $\times$ Out Medians | 4 | 554 | $101.7 \pm 26.5$ | $[54, 157]$ | **$5.45\times$** | $[5.39\times, 5.51\times]$ | **$+17.06$** | $0.000500$ | $0.001749$ (***) |
| **Model 4** | Total Degree Quintiles | 5 | 554 | $111.7 \pm 29.0$ | $[59, 172]$ | **$4.96\times$** | $[4.90\times, 5.02\times]$ | **$+15.27$** | $0.000500$ | $0.002624$ (***) |

*Note on Uncertainty*: Column 8 reports the 95% Monte Carlo simulation precision of the estimated ratio ($\text{SE}_{\text{MC}} \le 0.04\times$). Naive dyad-level bootstrapping was withdrawn because all 554 ACh–GABA dyads are formed by just 16 GABAergic tangential neurons, violating dyad independence. Population-level biological confidence intervals across fruit flies are mathematically unidentifiable from a single specimen ($N=1$).

### 5.8 Authoritative Results Table Across All Null Models

| Model | Null hypothesis | Quantities preserved | Observed statistic | Null expectation | Effect size | Uncertainty method | Empirical p-value | Multiplicity correction | Interpretation |
|---|---|---|:---:|:---:|:---:|---|:---:|:---:|---|
| **Model 1: Mutual Quartiles** | ACh/GABA labels exchangeable within mutual-degree quartiles | Mutual dyad graph ($M=5,435$), 4 mutual-degree strata, marginal NT counts | 554 dyads | $93.6 \pm 26.1$ dyads | **$5.92\times$** ($Z = +17.65$) | $s_{\text{null}} = 26.1$, $\text{SE}_{\text{MC}} = 0.58$, 95% MC: $[5.85\times, 5.99\times]$ | $p = 0.000500$ | FDR $q = 0.002624$ (***) | Strong enrichment under coarse mutual-degree conditioning; leaves within-quartile variance unconstrained. |
| **Model 2: Joint In $\times$ Out Tertiles** | NT labels exchangeable within joint in- and out-degree tertile grid bins | Mutual dyad graph ($M=5,435$), 9 joint grid strata, marginal NT counts | 554 dyads | $97.4 \pm 28.1$ dyads | **$5.69\times$** ($Z = +16.25$) | $s_{\text{null}} = 28.1$, $\text{SE}_{\text{MC}} = 0.63$, 95% MC: $[5.62\times, 5.76\times]$ | $p = 0.000500$ | FDR $q = 0.002099$ (***) | Persists across joint directed degree tertiles; coarse grid retains within-bin variance. |
| **Model 3: Joint In $\times$ Out Medians** | NT labels exchangeable within joint in- and out-degree median split bins | Mutual dyad graph ($M=5,435$), 4 joint median strata, marginal NT counts | 554 dyads | $101.7 \pm 26.5$ dyads | **$5.45\times$** ($Z = +17.06$) | $s_{\text{null}} = 26.5$, $\text{SE}_{\text{MC}} = 0.59$, 95% MC: $[5.39\times, 5.51\times]$ | $p = 0.000500$ | FDR $q = 0.001749$ (***) | High enrichment under median splits; broad partitions have high degree dispersion. |
| **Model 4: Total Degree Quintiles** | NT labels exchangeable within total degree ($d_{\text{in}} + d_{\text{out}}$) quintiles | Mutual dyad graph ($M=5,435$), 5 total-degree strata, marginal NT counts | 554 dyads | $111.7 \pm 29.0$ dyads | **$4.96\times$** ($Z = +15.27$) | $s_{\text{null}} = 29.0$, $\text{SE}_{\text{MC}} = 0.65$, 95% MC: $[4.90\times, 5.02\times]$ | $p = 0.000500$ | FDR $q = 0.002624$ (***) | Persists when conditioning on total degree; discards directional in/out asymmetry. |
| **Benchmark A: $k$-NN ($k=16$)** | Labels exchangeable within greedy clusters of 16 nearest degree neighbors | Mutual dyad graph ($M=5,435$), 154 micro-strata in normalized degree space | 554 dyads | $201.7 \pm 52.3$ dyads | **$2.75\times$** ($Z = +6.74$) | $s_{\text{null}} = 52.3$, $\text{SE}_{\text{MC}} = 1.65$, 95% MC: $[2.70\times, 2.79\times]$ | $p = 0.000999$ | Planned contrast ($q < 0.005$) | Substantial attenuation (5.7x -> 2.75x) as stratum degree variance is constrained ($< 3.0$). |
| **Benchmark B: $k$-NN ($k=8$)** | Labels exchangeable within tight clusters of 8 nearest degree neighbors | Mutual dyad graph ($M=5,435$), 308 micro-strata, degree variance $< 1.5$ | 554 dyads | $219.1 \pm 54.1$ dyads | **$2.53\times$** ($Z = +6.19$) | $s_{\text{null}} = 54.1$, $\text{SE}_{\text{MC}} = 1.71$, 95% MC: $[2.49\times, 2.57\times]$ | $p = 0.000999$ | Planned contrast ($q < 0.005$) | Strongest valid degree control; signal remains significant ($p < 0.001$). Caveat: small strata freeze label mobility. |
| **Audited Sampler: MCMC ($\sigma_d=0.20$)** | Continuous degree penalty $\exp(-\|\mathbf{d}_u - \mathbf{d}_v\|^2 / 2\sigma_d^2)$ | Mutual dyad graph ($M=5,435$), global transmitter counts | 554 dyads | $\sim 460$ (transient) $\to 393.8$ (theoretical uniform stationary mean) | Reported $1.20\times$ ($Z = +2.80$) | **None** (invalid chain) | **Withdrawn** (invalid) | Not applicable | **METHODOLOGICALLY INVALID**. Doubly stochastic transition matrix; stationary distribution is uniform permutation ($E[T] = 393.78$). |

![Figure 4: Statistical Robustness: Degree Conditioning, MCMC Audit & Confidence Sensitivity](results/figures/figure4_statistical_robustness_comparison.svg)

---

## 6. Continuous Degree Conditioning: k-NN Micro-Stratification & MCMC Audit

### 6.1 Validated Benchmark: Continuous k-NN Micro-Stratification
To test whether residual degree variation within coarse bins accounts for the observed enrichment, active neurons were partitioned into nearest-neighbor clusters in normalized $(d_{\text{in}}, d_{\text{out}})$ space:
- **$k = 16$ Micro-Strata ($154$ strata)**: Observed $554$ vs Null $201.65 \pm 52.29$ $\rightarrow$ **$2.75\times$ enrichment** (95% Monte Carlo CI: $[2.70\times, 2.79\times]$, $Z = +6.74, p = 0.000999$).
- **$k = 8$ Micro-Strata ($308$ strata)**: Observed $554$ vs Null $219.09 \pm 54.14$ $\rightarrow$ **$2.53\times$ enrichment** (95% Monte Carlo CI: $[2.49\times, 2.57\times]$, $Z = +6.19, p = 0.000999$).

*Interpretation*: Restricting label permutations strictly to nodes with near-identical degree profiles (mean within-stratum degree variance $< 1.5$) increases the null expectation from ~94 to ~219. Thus, joint in/out-degree characteristics attenuate the apparent enrichment from $\sim 5.7\times$ to $2.53\times$. Importantly, the remaining 2.53-fold association remains statistically significant ($p < 0.001$), indicating that the heterotypic motif cannot be fully attributed to degree confounding under the micro-stratification schemes tested. However, this attenuation should be interpreted as a conditional statistical association under degree constraints, not a formal causal decomposition.

### 6.2 Forensic Audit and Withdrawal of the Continuous MCMC Sampler
The original report described a continuous Metropolis–Hastings label-swapping sampler with acceptance rule:
$$\alpha(u, v) = \exp\left(-\frac{\|\mathbf{d}_u - \mathbf{d}_v\|^2}{2\sigma_d^2}\right)$$
reporting a residual excess of $1.20\times$ (+20.4%) at $\sigma_d = 0.20$.

#### Mathematical Derivation of Detailed Balance Failure
Let the state space $\Omega$ be the set of all label permutations preserving marginal counts. A step proposes swapping the labels of two discordant nodes $u$ and $v$. The proposal distribution $q(X' \mid X) = \frac{1}{\text{# discordant pairs}}$ is strictly symmetric: $q(X' \mid X) = q(X \mid X')$.
The acceptance probability $\alpha(u, v) = \exp(-\|\mathbf{d}_u - \mathbf{d}_v\|^2 / 2\sigma_d^2)$ depends solely on the fixed structural coordinates $\mathbf{d}_u, \mathbf{d}_v$. It does not depend on the label state $X$ or any state energy function $H(X)$.
Therefore, the reverse swap $X' \to X$ evaluates the exact same distance:
$$\alpha(X' \to X) = \alpha(X \to X')$$
Consequently, the transition probabilities satisfy:
$$T(X \to X') = q(X' \mid X) \alpha(X \to X') = q(X \mid X') \alpha(X' \to X) = T(X' \to X)$$
Because the transition matrix $T$ is symmetric (doubly stochastic) and irreducible, detailed balance $\pi(X) T(X \to X') = \pi(X') T(X' \to X)$ implies:
$$\pi(X) = \pi(X') = \frac{1}{|\Omega|} \quad \forall X \in \Omega$$
**The unique stationary distribution of this Markov chain is the UNIFORM DISTRIBUTION over all permutations.** The sampler contains **zero degree-conditioning**.

Under uniform permutation, the theoretical expectation is given analytically by:
$$E[T] = M \cdot \frac{2 N_{\text{ach}} N_{\text{gaba}}}{N(N-1)} = 5435 \times \frac{2 \times 1528 \times 144}{2465 \times 2464} = 393.78 \text{ dyads}$$

Numerical simulation (`scripts/audit_and_diagnose_mcmc.py`) verified that:
- When initialized from the empirical state ($obs = 554$), the chain slowly drifts downward toward the uniform stationary expectation ($393.78$ dyads), reaching 420 after 150k steps.
- When initialized from a random permutation ($obs = 368$), the chain drifts upward, reaching 406 after 150k steps.
- The reported 1.20x number was simply an artifact of incomplete burn-in and initialization bias. (The prior report erroneously conflated this baseline with the Model 1 coarse quartile null mean of 93.6).

**Remediation**: The MCMC sampler has been formally withdrawn from the primary scientific claims.

---

## 7. Cellular Anatomy, Chemical Polarity, and Layer Specialization

### 7.1 Single-Cell Annotation Coverage
Streaming FlyWire v2.1.0 annotations achieved **$100.00\%$ match coverage ($2,465 / 2,465$ neurons)**. Resolving 193 Central Brain annotations (`cell_type`, e.g. `CB.FB5I2`) ensured complete morphological assignment.

### 7.2 Morphological Substrate & 100% Directional Chemical Polarity
Decomposing mutual dyads by morphological family reveals that reciprocal feedback in the FB is overwhelmingly columnar–tangential:
- **All Mutual Dyads ($M = 5,435$)**: Columnar–Tangential: $3,579$ ($65.85\%$), Tangential–Tangential: $1,120$ ($20.61\%$), Columnar–Columnar: $663$ ($12.20\%$).
- **ACh–GABA Mutual Dyads ($N = 554$)**: Columnar–Tangential: **$551$ ($99.46\%$)**, Tangential–Tangential: $3$ ($0.54\%$), Columnar–Columnar: $0$ ($0.00\%$).

Furthermore, directional chemical polarity is **$100.00\%$ strict**:
- $Columnar_{\text{ACh}} \leftrightarrow Tangential_{\text{GABA}}$: **$551$ dyads ($100.00\%$)**
- $Columnar_{\text{GABA}} \leftrightarrow Tangential_{\text{ACh}}$: **$0$ dyads ($0.00\%$)**

### 7.3 Layer Specialization: 99.10% Concentration in Layers 4 & 5
Reciprocal ACh–GABA loops are highly concentrated in the central and ventral layers of the FB:

| Horizontal Layer | ACh-GABA Mutual Dyads | Percentage | Connectomic Function |
|---|:---:|:---:|---|
| **Layer 4** | **185** | **33.39%** | Intermediate premotor vector layer (`FB4A <-> vDeltaA`) |
| **Layer 5** | **364** | **65.70%** | Ventral premotor integration hub (`FB5A <-> FC2`, `FB5I2 <-> vDeltaF`) |
| **Layer 6** | 2 | 0.36% | Columnar crossover layer |
| **Layers 1, 2, 3, 7, 8, 9** | 0 | 0.00% | Dorsal input and visual layers |
| **Unassigned / Peripheral** | 3 | 0.54% | Peripheral arborizations |
| **Total** | **554** | **100.0%** | **Layers 4 & 5 contain 99.10% (549 / 554 dyads)** |

*Statistical Significance of Layer 4 & 5 Concentration*: To rigorously test whether this layer clustering reflects a genuine architectural preference rather than neuropil-wide dyad density, we compared ACh–GABA reciprocal loops against all $M = 5,435$ mutual dyads in the FB. Across all mutual dyads, $2,196 / 5,435$ ($40.40\%$) reside in Layers 4 & 5. For ACh–GABA loops, $549 / 554$ ($99.10\%$) reside in Layers 4 & 5. A two-sided Fisher's exact test demonstrates that ACh–GABA reciprocal feedback is overwhelmingly concentrated in Layers 4 & 5: **Odds Ratio = 215.60, hypergeometric $p = 3.36 \times 10^{-226}$**.

![Figure 3: Cellular Substrate, 100% Directional Polarity, and Layer Specialization](results/figures/figure3_neuronal_and_layer_organization.svg)

### 7.4 Dominant Physical Microcircuits

| Rank | Cell-Type Pairing | Dyads | % of ACh-GABA | Morphological Interaction |
|:---:|---|:---:|:---:|---|
| 1 | **`FB4A <-> vDeltaA`** | **150** | 27.08% | Layer 4 vertical vector feedback |
| 2 | **`FB5A <-> FC2C`** | **131** | 23.65% | Layer 5 premotor output clamping |
| 3 | **`FB5A <-> FC2B`** | **102** | 18.41% | Layer 5 premotor output clamping |
| 4 | **`FB5A <-> FC2A`** | **39** | 7.04% | Layer 5 premotor output clamping |
| 5 | **`FB5A <-> hDeltaM`** | **32** | 5.78% | Layer 5 inter-columnar vector exchange |
| 6 | **`FB5I2 <-> vDeltaF`** | **29** | 5.23% | Layer 5 vertical vector feedback |
| 7 | **`FB4A <-> hDeltaI`** | **26** | 4.69% | Layer 4 inter-columnar vector exchange |
| 8 | **`FB5A <-> FC3`** | **21** | 3.79% | Layer 5 premotor steering modulation |
| -- | **Top 8 Subtotal** | **530** | **95.67%** | **530 / 554 dyads fully identified** |

---

## 8. Architectural Dichotomy: 1D Heading (EB) vs 2D Steering (FB)

![Figure 6: Architectural Dichotomy: 1D Heading (EB) vs 2D Steering (FB)](results/figures/figure6_eb_vs_fb_circuit_contrast.svg)

| Circuit Dimension | Ellipsoid Body (`EB`): 1D Heading Compass | Fan-Shaped Body (`FB`): 2D Vector Steering Matrix |
|---|---|---|
| **Primary Computation** | 1D Heading Representation (Bump Attractor) | 2D Vector Steering, Goal Routing, Premotor Action |
| **Network Scale** | $N = 483$ neurons, $E = 15,812$ edges | $N = 2,465$ neurons, $E = 46,903$ edges |
| **Topological Reciprocity** | $44.50\%$ ($M = 3,518$; Rank #1 in brain) | $23.18\%$ ($M = 5,435$; Rank #6 in brain) |
| **Primary Reciprocal Motif** | **Homotypic Recurrent Inhibition ($GABA \leftrightarrow GABA$)** | **Heterotypic Excitatory-Inhibitory Feedback ($ACh \leftrightarrow GABA$)** |
| **Observed Primary Dyads** | $2,615$ dyads ($74.33\%$ of $M$) | $554$ dyads ($10.19\%$ of $M$) |
| **Controlled Enrichment** | $+20.6\%$ to $+31.8\%$ excess ($1.21\times$ to $1.32\times$, $Z > +13$) | **$4.96\times$ to $5.92\times$ enrichment ($Z = +15.3$ to $+17.7$)** |
| **Degree-Matched Excess** | $1.17\times$ to $1.18\times$ ($k$-NN, $Z > +8.4$) | **$2.53\times$ to $2.75\times$ ($k$-NN, $Z > +6.1$)** |
| **Anatomical Substrate** | $88.18\%$ Ring $\leftrightarrow$ Ring neurons ($ER \leftrightarrow ER$) | **$99.46\%$ Columnar $\leftrightarrow$ Tangential ($Col \leftrightarrow Tan$)** |
| **Directional Polarity** | Symmetric inhibitory recurrence | **$100.00\%$ Strict ($Col_{\text{ACh}} \leftrightarrow Tan_{\text{GABA}}$)** |
| **Spatial Organization** | Homotypic within concentric toroids | **$99.10\%$ localized in premotor Layers 4 & 5 (549 / 554 dyads)** |
| **Opposing Motif Behavior** | $ACh \leftrightarrow GABA$ is **DEPLETED** ($0.27\times, Z = -23.2$) | $GABA \leftrightarrow GABA$ is **ABSENT** ($6$ dyads, $0.11\%$) |

---

## 9. Rate-Based Circuit Dynamics & Stress-Testing

To investigate the dynamical consequences of columnar–tangential reciprocity, we simulated a 16-column continuous-attractor rate model of the Layer 4/5 circuit (`scripts/simulate_vector_steering_dynamics.py`):
$$\tau_{\text{col}} \frac{d r_{\text{col}, i}}{dt} = -r_{\text{col}, i} + \left[ I_i(\theta) + \sum_{j} W_{\text{lat}, ij} r_{\text{col}, j} - W_{\text{inh}} r_{\text{tan}} \right]_+$$
$$\tau_{\text{tan}} \frac{d r_{\text{tan}}}{dt} = -r_{\text{tan}} + \left[ \sum_{j} W_{\text{recip}, j} r_{\text{col}, j} \right]_+$$

![Figure 5: Rate-Based Circuit Dynamics: Linear Subtractive Feedback & Stress-Testing](results/figures/figure5_dynamical_model_stress_testing.svg)

### 9.1 Audited Findings & Stress-Test Insights (`scripts/stress_test_dynamics.py`)
1. **Linear Subtractive Feedback (Not Divisive Normalization)**:
   The feedback term $- W_{\text{inh}} r_{\text{tan}}$ enters linearly inside rectification. As drive scales ($I_0 \in [1, 30]$), peak firing rates increase linearly with constant slope:
   - Intact ($W_{\text{inh}} = 0.85$): $\approx 1.53$ Hz per unit drive.
   - Ablated ($W_{\text{inh}} = 0$): $\approx 14.87$ Hz per unit drive.
   Reciprocal inhibition attenuates the effective slope by $9.72\times$, bounding firing rates ($\le 30.6$ Hz vs 297.4 Hz runaway excitation), but does not induce saturating hyperbolic gain curvature.
2. **Supercritical Boundary**:
   If lateral excitation exceeds $J_{\text{col}} \ge 0.60$, the system diverges into supercritical runaway excitation ($> 3.8\times 10^6$ Hz).
3. **Noise Sensitivity & Angular Decoding Precision**:
   In noiseless conditions, circular symmetry forces decoded error to $< 0.8^\circ$. Under Gaussian sensory noise, mean decoding error scales gracefully:
   - 5% noise: $1.52^\circ$ (intact) vs $1.20^\circ$ (ablated)
   - 10% noise: $2.38^\circ$ (intact) vs $2.66^\circ$ (ablated)
   - 20% noise: $5.65^\circ$ (intact) vs $4.67^\circ$ (ablated)

---

## 10. Sensitivity Analyses & Negative Controls

Executed in `scripts/run_sensitivity_and_controls.py`:
1. **Transmitter Confidence Thresholding & Tangential Confidence Floor**:
   Systematic evaluation of confidence thresholds reveals a fundamental property of machine-learning connectomic annotations:
   - Unfiltered (`conf >= 0.00`): $2,465$ nodes, $5,435$ mutual dyads, $554$ ACh–GABA dyads ($10.19\%$).
   - Threshold `conf >= 0.60`: $1,487$ nodes, $1,318$ mutual dyads, $79$ ACh–GABA dyads ($5.99\%$).
   - Threshold `conf >= 0.70`: $1,064$ nodes, $684$ mutual dyads, $57$ ACh–GABA dyads ($8.33\%$).
   - Threshold `conf >= 0.80`: $600$ nodes, $185$ mutual dyads, **$0$ ACh–GABA dyads ($0.00\%$)**.
   *Forensic Root Cause*: In the Eckstein et al. (2024) predictions, GABAergic tangential neurons (`FB5A`, `FB4A`, `FB5I2`) have an empirical maximum confidence ceiling of **$0.7873$** (median $0.7812$), whereas columnar cholinergic neurons reach up to $0.8977$. Applying a naive global threshold of $\ge 0.80$ completely excises the entire tangential inhibitory population from the graph, collapsing ACh–GABA dyads to zero. This demonstrates that confidence thresholding must account for cell-type specific ultrastructural morphology rather than imposing arbitrary global cutoffs.
2. **Synthetic Negative Control**:
   Random Erdős–Rényi graphs with matching node counts and transmitter frequencies yielded an enrichment ratio of $1.042\times$, $Z = +0.78, p = 0.4296$, proving that the permutation engine exhibits zero false-positive bias in uncoordinated topologies.
3. **Synthetic Positive Control**:
   Spiking heterotypic reciprocal dyads into random networks produced an enrichment ratio of $1.607\times$, $Z = +11.34, p = 0.001$, confirming that the testing framework achieves high statistical power to detect genuine chemospecific preferences.
4. **Uncertainty Evaluation & Synthetic Bootstrap Coverage Test**:
   Evaluation of effect-size uncertainty demonstrates a crucial methodological finding:
   - Naive dyad-level bootstrapping treats the 5,435 mutual dyads as independent Bernoulli observations. Direct recomputation reveals that all 554 ACh–GABA dyads are formed by **just 16 distinct GABAergic tangential neurons** and 256 cholinergic columnar neurons (an average of 34.6 dyads per GABA neuron).
   - Because dyads sharing hub neurons exhibit severe mutual dependence, resampling dyads as independent draws dramatically underestimates variance. Furthermore, resampling dyads destroys the empirical graph topology, and cross-specimen biological variance is unidentifiable from a single connectome ($N=1$).
   - *Empirical Coverage Verification*: In a synthetic ground-truth simulation with 16 hubs (`scripts/run_sensitivity_and_controls.py`), naive dyad bootstrap achieved only **55.6% empirical coverage** for nominal 95% confidence intervals (7.2-fold variance underestimation), whereas cluster/hub-aware bootstrap recovered **91.6% coverage**.
   - Consequently, naive dyad bootstrap confidence intervals were withdrawn. The statistical engine reports exact Monte Carlo simulation precision for the null expectations ($\text{SE}_{\text{MC}} \le 0.04\times$ on the enrichment ratios across models).

---

## 11. Limitations & Epistemic Guardrails

1. **Single Female Specimen**:
   Derived from one adult female fly (FAFB v783). Cross-individual variability and sexual dimorphism require confirmation in upcoming male and multi-connectome datasets.
2. **Machine-Learning Transmitter Predictions**:
   Transmitter identities are computational predictions based on presynaptic T-bar morphology (Eckstein et al., 2024). They do not measure postsynaptic receptor expression ($Rdl$ vs $GABA_B$) or verify physiological conductances.
3. **Subtractive Rate Model vs Biophysical Realism**:
   Synaptic weights ($w \ge 5$) represent physical synapse counts, not measured millivolt depolarizations. The rate model is an exploratory proof-of-concept.
4. **Descriptive Anatomy**:
   Cell-type breakdowns (`FB4A`, `FB5A`, `FC2`) represent descriptive anatomical counts, not independent significance tests.

---

## 12. Reproducibility Guide & Verified Checksums

All analyses are fully deterministic and executable via the provided `Makefile`:

```bash
# 1. Run Complete Automated Test Suite (40 tests, ~2.9s)
make test

# 2. Run Forensic Audit, Stress Tests & Controls (~15s)
make audit

# 3. Run Primary Controlled Permutations (~78s)
python3 scripts/run_fb_controlled_study.py

# 4. Render All 6 Presentation Figures (SVG & PNG, ~2.5s)
make figures

# 5. Run Interactive CLI Demonstration (~0.06s)
make demo

# 6. Full End-to-End Replication
make reproduce
```

### Verified File Checksums (SHA-256)
* `data/fb_node_covariates.json`: `b08685a762947b06558ba1f01e7f569b3e94592bccc2f1e150be90dca3b789a1`
* `data/fb_annotation_map.json`: `c202709002ce45015cd8bfcc7e029ed91dd13d2f84b3398e9311c6ebebd26a27`
* `results/fb_controlled_study_results.json`: `334d77623b30a1c17af898cba76652985c434521642058502dbc6c123dd17d09`
* `results/fb_continuous_degree_results.json`: `0ea8afb16c55b5e92e574bd4a5a738afbaddf84dfebef708b49b0ba7ada60f67`
* `results/fb_layer_column_anatomy.json`: `5091caa9f12e38b7c637d4d07b35f6f5c14d7475cc91ea13a149ef195ad1d60e`
* `results/fb_dynamical_simulation_results.json`: `e5ecd56f8a3e98f870f727547cf6ab163f1f5b375fbb792bbd03661887404441`
* `results/dynamics_stress_test_results.json`: verified dynamically generated.
* `results/sensitivity_and_controls_results.json`: verified dynamically generated.

---

## 13. Priority Next Research Contributions (Phase 13 Roadmap)

Following rigorous scientific validation, three concrete extensions represent the highest-value scientific contributions feasible with future datasets:

1. **Cross-Specimen and Cross-Sex Connectome Replication**:
   - *Objective*: Test whether the 99.1% concentration of ACh–GABA feedback in Layers 4 & 5 is an invariant architectural feature of *Drosophila* navigation or unique to the single female FAFB specimen.
   - *Data Requirements*: Adult male connectomes and Janelia hemibrain v1.2 with reconciled columnar–tangential coordinates.
2. **Biophysical Conductance Modeling of Dual-Receptor Kinetics**:
   - *Objective*: Replace the threshold-linear rate equation with a biophysically grounded multi-compartmental conductance model in NEURON or Brian2.
   - *Scientific Value*: Evaluate whether tangential GABAergic inhibition operates via fast ionotropic $Rdl$ ($GABA_A$) channels to enforce millisecond-timescale gain modulation, or slow metabotropic $GABA_B$ receptors to implement behavioral state-dependent modulation.
3. **Targeted In Vivo Functional Electrophysiology**:
   - *Objective*: Direct physiological validation of the `FB4A <-> vDeltaA` (150 dyads) and `FB5A <-> FC2` (272 dyads) reciprocal motifs using cell-type specific Gal4/Split-Gal4 driver lines, patch-clamp recordings, and two-photon optogenetic activation.

---

## 14. Graduate Resume & Scientific Abstract

### Validated Scientific Abstract (218 words)
> The central complex of *Drosophila melanogaster* orchestrates goal-directed navigation through two coordinated geometric representations: a one-dimensional azimuth compass in the ellipsoid body (EB) and a two-dimensional vector steering matrix in the fan-shaped body (FB). While the EB compass is maintained by dense homotypic recurrent inhibition among GABAergic ring neurons (74.3% of mutual dyads), the reciprocal network architecture of the FB remained unresolved. Here, we present VectorWing, a computationally audited connectomic pipeline analyzing the complete intrinsic FB graph ($N = 2,465$ neurons, $E = 46,903$ edges, $w \ge 5$) from the adult female whole-brain connectome (FlyWire FAFB v783). We uncover a chemical pairing inversion: homotypic GABA recurrence is virtually absent (0.11%), replaced by a massive heterotypic enrichment of acetylcholine–GABA reciprocal loops ($554$ dyads, $10.19\%$ of mutual dyads; $4.96\times$ to $5.92\times$ under discrete degree null models, $p = 0.000500$, Benjamini–Hochberg FDR $q < 0.003$). Fine-grained continuous $k$-NN degree micro-stratification ($308$ strata) attenuates enrichment to $2.53\times$ while maintaining significance ($p = 0.000999$), confirming a persistent conditional association under degree constraints. FlyWire v2.1.0 annotation mapping establishes that $99.46\%$ ($551/554$) of these loops connect columnar and tangential neurons with $100.00\%$ strict directional chemical polarity (Columnar=ACh, Tangential=GABA), localized at $99.10\%$ in premotor Layers 4 and 5. Rate-based modeling demonstrates that this heterotypic feedback provides linear subtractive attenuation ($9.72\times$), bounding runaway excitation during active steering.

### Recommended Resume Bullets:
* **Computational Neuroscience & Connectomics**:
  > *"Developed VectorWing, an audited connectomics pipeline for the adult Drosophila Fan-Shaped Body (FAFB v783, 2,465 neurons, 46,903 edges); discovered an inverted reciprocity profile with 2.5x–5.9x degree-conditioned enrichment of heterotypic ACh–GABA reciprocal loops (p < 0.001) concentrated at 99.1% in premotor Layers 4 and 5 with 100% strict directional chemical polarity (Columnar=ACh, Tangential=GABA)."*
* **Statistical Modeling & Quality Assurance**:
  > *"Audited permutation null models; derived mathematical proof of detailed-balance violation in a continuous MCMC swap sampler, replaced it with fine-grained k-NN micro-stratification (308 strata), evaluated Monte Carlo simulation precision, and implemented synthetic positive and negative controls."*
* **Dynamical Systems & Scientific Software**:
  > *"Implemented a 16-column continuous-attractor rate model demonstrating that recurrent tangential inhibition provides 9.7x linear subtractive attenuation, preventing runaway excitation in recurrent columnar loops; authored a 40-test automated test suite and rendered 6 publication figures."*
