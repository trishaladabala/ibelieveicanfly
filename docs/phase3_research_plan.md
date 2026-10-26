# Research Protocol & Experimental Plan: Phase 3 Validation & Biological Discovery
**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics Pipeline  
**Dataset**: FlyWire FAFB v783.0 (`proofread_connections_783.feather`, `proofread_root_ids_783.npy`)  
**Investigator**: Computational Biology Research Mentee  
**Date**: October 2026  
**Status**: Active / Validated  

---

## 1. Executive Summary & Research Mandate

This protocol establishes the formal experimental architecture, methodological definitions, and computational verification procedures for Phase 3 of the *Drosophila melanogaster* whole-brain connectomics investigation. 

Transitioning from preliminary software pilots and synthetic testing to whole-connectome biological discovery, this research program addresses three primary objectives:
1. **Reconciliation of Methodological Discrepancies**: Fully resolve numerical divergences identified in preliminary reports (specifically the 3.82% sampled reciprocity vs. full-connectome topology, and the 138,639 active connected neurons vs. 139,255 proofread root IDs).
2. **Whole-Brain Macro-Topological Audits**: Execute full-connectome evaluations across all 16,847,997 connection records, establishing multi-threshold sensitivity benchmarks ($w \in \{1, 2, 3, 5, 10, 20\}$), complete-case neurotransmitter distributions across 4 denominator formulations, and an exhaustive 79-neuropil reciprocity ranking with bilateral hemispheric symmetry testing.
3. **Hypothesis-Driven Biological Discovery**: Investigate the recurrent organizational logic of the fly brain by testing whether reciprocal feedback connections ($u \leftrightarrow v$) exhibit non-random neurotransmitter pairing ($T_u, T_v$). Using both analytical multinomial null models and degree-preserving permutation null models, we evaluate whether homotypic feedback inhibition ($GABA \leftrightarrow GABA$) and feedback gain control ($ACh \leftrightarrow GABA$) are statistically enriched, with dedicated stratification in the Central Complex (Ellipsoid Body, Fan-shaped Body) to assess mechanistic circuit models of ring attractors.

---

## 2. Hardware Environment & Bounded-Memory Computational Engineering

The investigation is executed entirely on local commodity hardware under strict computational bounds:
- **Host System**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2 physical cores, 4 threads).
- **Primary Memory**: 8 GB RAM (7.7 GiB visible; OS baseline memory ~3.8 GiB).
- **Secondary Storage**: 1 TB 5400 RPM mechanical HDD (ext4).
- **Operating Constraints**:
  - Additional process-memory budget strictly capped at **$\le 2.5\text{ GiB}$**.
  - Single-worker sequential execution to prevent thrashing and out-of-memory (OOM) kernel panics.
  - Prohibition of dense whole-brain adjacency matrices ($138,639 \times 138,639 \times 8\text{ bytes} \approx 153.8\text{ GB}$, which exceeds physical RAM by $>19\times$).
  - Bounded streaming via Apache Arrow IPC record batches (65,536 records/batch), processing stream iterators without materializing uncompressed tabular columns into memory.
  - Compact memory structures: bit-packed 64-bit edge keys `(u << 32) | v` mapping 32-bit compact neuron IDs, 8-bit unsigned byte arrays (`array('B')`) for categorical phenotypes, and disjoint-set forests for linear-time connected components.

---

## 3. Mathematical & Network Theoretical Definitions

### 3.1 Network Representation
Let the connectome be represented as a weighted directed graph $G = (V, E, W)$, where:
- $V$ is the set of proofread fly-brain neurons.
- $E \subseteq V \times V$ is the set of directed chemical synaptic connections $(u, v)$ from presynaptic neuron $u$ to postsynaptic neuron $v$, with $u \ne v$ for dyads and $u = v$ for autapses.
- $W: E \to \mathbb{Z}^+$ assigns each directed edge an anatomical synaptic weight $w(u, v)$ equal to the number of detected T-bar / PSD pairs.
- For an anatomical threshold $t \in \mathbb{Z}^+$, the thresholded subgraph is $G_t = (V_t, E_t)$, where $E_t = \{(u, v) \in E \mid w(u, v) \ge t\}$ and $V_t$ is the set of active vertices incident to at least one edge in $E_t$.

### 3.2 Reciprocity Formulations
Reciprocity quantifies the tendency of directed connections to form mutual, bidirectional feedback loops. We evaluate two mathematically rigorous definitions:

1. **Edge-Based Reciprocity ($R_{\text{edge}}$)**:
   The proportion of directed edges in the network that participate in mutual dyads:
   $$R_{\text{edge}} = \frac{2 \cdot M}{E}$$
   where $M = |\{\{u, v\} \subset V \mid (u, v) \in E \land (v, u) \in E, u < v\}|$ is the number of mutual dyads, and $E = |E|$ is the total number of directed edges.

2. **Dyad-Based Reciprocity ($R_{\text{dyad}}$)**:
   The proportion of connected neuron pairs that are bidirectional:
   $$R_{\text{dyad}} = \frac{M}{M + U}$$
   where $U = E - 2M - A$ is the number of asymmetric (unidirectional) dyads, and $A = |\{(u, u) \in E\}|$ is the number of autapses. Here, $M + U$ represents the total number of distinct connected node pairs.

### 3.3 Giant Connected Component (GCC)
Let $\mathcal{C}_1, \mathcal{C}_2, \dots, \mathcal{C}_k$ be the connected components of the undirected graph formed by treating all edges in $E_t$ as undirected. The Giant Connected Component (GCC) fraction is:
$$\text{GCC Fraction} = \frac{\max_i |\mathcal{C}_i|}{|V_t|}$$
evaluated via Disjoint-Set (Union-Find) with path compression and union by rank in $O(|V_t| + |E_t| \cdot \alpha(|V_t|))$ time.

### 3.4 Consensus Neurotransmitter Assignment
For each presynaptic neuron $u \in V$, the deep-learning model (Eckstein, Bates et al. 2024) predicts probabilities across six canonical classes:
$$\mathcal{K} = \{\text{ach, gaba, glut, da, oct, ser}\}$$
We compute the synapse-weighted total probability mass emitted by neuron $u$:
$$M_{u, k} = \sum_{j \in \text{out}(u)} w(u, j) \cdot P_k(u, j)$$
The consensus neurotransmitter phenotype $T_u$ and prediction confidence $C_u$ are assigned as:
$$T_u = \arg\max_{k \in \mathcal{K}} M_{u, k}, \quad C_u = \frac{\max_{k \in \mathcal{K}} M_{u, k}}{\sum_{k \in \mathcal{K}} M_{u, k}}$$

---

## 4. Null Models & Statistical Testing

### 4.1 Null Model 1: Analytical Marginal Expectation Null
Let $V_{\text{recip}}$ be the set of neurons participating in at least one reciprocal dyad at threshold $t$, with $|V_{\text{recip}}| = N_{\text{recip}}$.
The marginal frequency of neurotransmitter class $k$ among reciprocal neurons is:
$$p_k = \frac{1}{N_{\text{recip}}} \sum_{i \in V_{\text{recip}}} \mathbb{I}(T_i = k)$$
Under the null hypothesis that reciprocal pairing occurs as independent multinomial draws proportional to marginal frequencies, the expected probability of an unordered dyad $\{T_u, T_v\} = \{k, l\}$ is:
$$P_0(k, l) = \begin{cases} p_k^2 & \text{if } k = l \\ 2 \cdot p_k \cdot p_l & \text{if } k \ne l \end{cases}$$
The expected count in a network of $M$ reciprocal dyads is:
$$E_0(k, l) = M \cdot P_0(k, l)$$
We quantify enrichment or depletion via:
- **Enrichment Ratio**: $\text{Ratio}(k, l) = \frac{O(k, l)}{E_0(k, l)}$
- **Standardized Residual**: $R_{\text{std}}(k, l) = \frac{O(k, l) - E_0(k, l)}{\sqrt{E_0(k, l)}}$
- **Total Goodness-of-Fit**: $\chi^2 = \sum_{k \le l} \frac{(O(k, l) - E_0(k, l))^2}{E_0(k, l)}$ with $\text{df} = 20$.

### 4.2 Null Model 2: Degree- and Dyad-Preserving Permutation Null
To account for complex topological correlations, non-uniform degree distributions, and clustering, we employ an exact permutation test:
1. Fix the empirical reciprocal dyad topology $D = \{\{u_1, v_1\}, \{u_2, v_2\}, \dots, \{u_M, v_M\}\}$.
2. Perform $B$ iterations (e.g. $B = 200$ to $500$). In iteration $b$, randomly shuffle the neurotransmitter assignments $T$ across $V_{\text{recip}}$, preserving the exact network topology, dyad graph, and node degree sequences.
3. In each shuffle, count the resulting dyad frequencies $O_b(k, l)$.
4. Compute the empirical null mean $\mu_{\text{perm}}(k, l)$ and standard deviation $\sigma_{\text{perm}}(k, l)$:
   $$z(k, l) = \frac{O(k, l) - \mu_{\text{perm}}(k, l)}{\sigma_{\text{perm}}(k, l)}$$
   with two-tailed empirical $p$-value:
   $$p_{\text{emp}}(k, l) = \frac{1 + \sum_{b=1}^B \mathbb{I}(|O_b - \mu_{\text{perm}}| \ge |O - \mu_{\text{perm}}|)}{B + 1}$$

### 4.3 Bilateral Symmetry Statistics
For all bilateral neuropil pairs $(L, R)$ (e.g., $\text{AL\_L}$ vs $\text{AL\_R}$), we evaluate:
1. **Cohen's $h$ Effect Size**:
   $$h = 2 \cdot \arcsin(\sqrt{p_L}) - 2 \cdot \arcsin(\sqrt{p_R})$$
   interpreted as Negligible ($|h| < 0.2$), Small ($0.2 \le |h| < 0.5$), Medium ($0.5 \le |h| < 0.8$), or Large ($|h| \ge 0.8$).
2. **Two-Proportion Pooled $z$-Test**:
   $$z = \frac{p_L - p_R}{\sqrt{\hat{p}(1 - \hat{p}) \left(\frac{1}{E_L} + \frac{1}{E_R}\right)}}, \quad \hat{p} = \frac{2M_L + 2M_R}{E_L + E_R}$$

---

## 5. Experimental Phases & Verification Checkpoints

| Phase | Description | Computational Method | Output Artifact | Status |
|---|---|---|---|---|
| **Phase 1** | Results Audit & Cataloging | Structural review of prior claims | `docs/phase3_results_audit.md` | Verified |
| **Phase 2** | Whole-Brain Reciprocity & Thresholds | Streaming Arrow IPC ($w \in \{1, 2, 3, 5, 10, 20\}$) | `results/real_data_pilot/verified_threshold_sensitivity.json` | Verified |
| **Phase 3** | Neuron Universe Reconciliation | Binary NPY header & uint64 stream parsing | `results/real_data_pilot/neuron_universe_reconciliation.json` | Verified |
| **Phase 4** | Neurotransmitter Distribution Audit | Probability mass streaming across 4 denominators | `results/real_data_pilot/verified_neurotransmitter_summary.json` | Verified |
| **Phase 5** | All-79 Neuropils Reciprocity & Symmetry | Regional graph partitioning & Cohen's $h$ audit | `results/real_data_pilot/verified_regional_metrics.json` | Verified |
| **Phase 6/7**| Reciprocal NT Motifs & Null Models | Consensus phenotype assignment & permutation test | `results/real_data_pilot/verified_reciprocal_transmitters.json` | In Execution |
| **Phase 8** | Literature Benchmarking | Comparative review against Lin, Dorkenwald, Eckstein | `docs/phase3_literature_and_positioning.md` | Verified |
| **Phase 9** | Methodological Review & Reproducibility | Verification checklist & hardware audit | `docs/phase3_checkpoint.md` | In Execution |
| **Phase 10**| Validation Report & Synthesis | Publication-grade comprehensive synthesis report | `results/real_data_pilot/phase3_validation_report.md` | Pending |

