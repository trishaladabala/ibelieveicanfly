# Phase 4: Controlled Statistical Design & Hypothesis Pre-Specification

**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Whole-Brain Connectomics  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Date**: October 20, 2026  
**Status**: Formal Statistical Design & Protocol Specification  

---

## 1. Scientific Objective & The Core Methodological Dilemma

Previous preliminary phases observed an extreme statistical enrichment of $GABA \leftrightarrow GABA$ reciprocal dyads in the Ellipsoid Body (EB) when compared against directed degree-preserving edge-swap null models ($Z > 140, p < 0.01$). 

However, Phase 3 mixing diagnostics established that the standard edge-swap null fundamentally alters the underlying graph topology:
- In the empirical EB ($w \ge 5$), there are $M = 3,518$ mutual dyads (edge reciprocity $R_{\text{edge}} = 44.50\%$).
- Under the degree-preserving edge-swap null, the mutual dyad count drops precipitously to $M_{\text{null}} = 763.4 \pm 22.0$ ($R_{\text{edge}} \approx 9.66\%$) — a **$4.61\times$ suppression of reciprocity**.
- Consequently, comparing raw empirical motif counts against the edge-swap null conflates two distinct scientific questions:
  1. **Topological Question**: Does the neuropil exhibit more reciprocal loops than predicted by its directed in- and out-degree sequences?
  2. **Chemical Selectivity Question**: Given the observed reciprocal loops, do specific neurotransmitter pairs form reciprocal partnerships more often than expected by chance?

This protocol defines a rigorous two-tier statistical framework to decouple these phenomena.

---

## 2. Two-Tier Null Model Architecture

```
                                    FAFB v783 Directed Graph (w >= 5)
                                                   │
                  ┌────────────────────────────────┴────────────────────────────────┐
                  ▼                                                                 ▼
      TIER 1: TOPOLOGICAL NULL MODEL                                 TIER 2: CONDITIONAL CHEMICAL NULL
   (Maslov-Sneppen MCMC Edge Swaps)                               (Degree-Stratified Label Permutations)
                  │                                                                 │
    Preserves:                                                        Preserves:
    - Exact in-degree sequence d_in(v)                                - Exact empirical mutual dyads (M fixed)
    - Exact out-degree sequence d_out(v)                              - Exact reciprocal graph topology
    - Total edge count |E|                                            - Empirical degree-transmitter correlation
    - Forbids self-loops and multi-edges                              - Neuropil node universe & label marginals
                  │                                                                 │
    Relaxes:                                                          Relaxes:
    - Reciprocal dyad structure (M varies)                            - Specific pairing between node labels
                  │                                                                 │
    Tests:                                                            Tests:
    "Is reciprocal connectivity M enriched                            "Given observed M, is transmitter pairing
     beyond degree expectations?"                                      enriched beyond degree-stratified chance?"
```

### Tier 1: Topological Reciprocity Null Model
* **Algorithm**: Directed edge-swap MCMC preserving in-degree and out-degree sequences.
* **Burn-in & Budget**: $20\times |E|$ swaps per permutation, verified by Phase 3 diagnostics to reach stationary equilibrium ($\tau_{\text{int}} \le 0.63$).
* **Primary Metric**: Total mutual dyads $M = \sum_{u < v} \mathbb{I}((u, v) \in E \land (v, u) \in E)$.
* **Hypothesis Tested**:
  $$H_{0}^{\text{topo}}: \mathbb{E}[M_{\text{obs}}] = M_{\text{swap\_null}}$$
  $$H_{1}^{\text{topo}}: \mathbb{E}[M_{\text{obs}}] > M_{\text{swap\_null}}$$

### Tier 2: Conditional Chemical Pairing Null Model
* **Algorithm**: Degree-stratified label permutations on the observed reciprocal graph.
* **Topology**: Held strictly constant ($M = 3,518$ in EB, $M = 5,442$ in FB, $M = 137$ in PB).
* **Degree Stratification**:
  - In EB, active nodes are partitioned into 4 equal-sized strata based on their mutual degree $d_{\text{mutual}}(v)$ in the empirical graph.
  - Transmitter labels are randomly permuted strictly *within* each degree stratum.
  - *Rationale*: In EB, GABAergic neurons exhibit significantly higher mutual degrees (mean $18.6$) than cholinergic neurons (mean $10.5$) or dopaminergic neurons (mean $1.9$). Unstratified shuffling destroys this empirical correlation and artificially deflates the null baseline. Stratification ensures that high-degree nodes exchange labels only with other high-degree nodes.
* **Primary Metric**: Count of target unordered transmitter pairings in observed mutual dyads:
  $$C(t_1, t_2) = \sum_{\{u, v\} \in \text{MutualDyads}} \mathbb{I}(\{NT(u), NT(v)\} = \{t_1, t_2\})$$
* **Hypothesis Tested**:
  $$H_{0}^{\text{chem}}: \mathbb{E}[C(t_1, t_2)] = C_{\text{strat\_null}}$$
  $$H_{1}^{\text{chem}}: \mathbb{E}[C(t_1, t_2)] \ne C_{\text{strat\_null}}$$

---

## 3. Pre-Specification of Primary and Secondary Endpoints

To prevent $p$-hacking and multiple-testing distortion across 21 possible transmitter pairs, endpoints are strictly pre-specified:

### Primary Endpoint
* **Neuropil**: Ellipsoid Body (`EB`)
* **Threshold**: Synapse weight $w \ge 5$ (standard high-confidence cutoff)
* **Target Pairing**: $GABA \leftrightarrow GABA$ mutual dyads
* **Test Model**: Tier 2 Degree-Stratified Conditional Null ($B = 2,000$ permutations)
* **Statistical Measure**:
  - Observed count $C_{\text{obs}}$
  - Conditional null mean $\mu_{\text{null}}$ and standard deviation $\sigma_{\text{null}}$
  - True Conditional Enrichment Ratio: $E_{\text{cond}} = C_{\text{obs}} / \mu_{\text{null}}$
  - Exact finite-sample empirical two-tailed $p$-value:
    $$p = \frac{1 + \sum_{b=1}^B \mathbb{I}(|C_b - \mu_{\text{null}}| \ge |C_{\text{obs}} - \mu_{\text{null}}|)}{B + 1}$$

### Pre-Defined Secondary Endpoints
1. **Fan-Shaped Body (`FB`) ACh–GABA Pairing**:
   - Threshold $w \ge 5$, Target: $ACh \leftrightarrow GABA$ under Tier 2 conditional null.
2. **Protocerebral Bridge (`PB`) ACh–ACh Pairing**:
   - Threshold $w \ge 5$, Target: $ACh \leftrightarrow ACh$ under Tier 2 conditional null.
3. **Topological Reciprocity Excess Across Central Complex**:
   - Tier 1 edge-swap null testing total mutual dyads $M$ in EB, FB, and PB at $w \ge 5$ ($B = 200$ permutations, $20\times |E|$ swaps).
4. **Threshold Sensitivity ($w \ge 3$ vs $w \ge 5$)**:
   - Evaluation of primary and secondary endpoints at $w \ge 3$.
5. **Transmitter Classification Robustness**:
   - Primary endpoint evaluated under:
     - All active neurons vs. high-confidence neurons (confidence $\ge 0.80$).
     - Neuron consensus labels vs. connection-level probabilistic expectation.

### Multiple-Testing Adjustment
- The primary hypothesis is tested at nominal $\alpha = 0.05$.
- Secondary chemical hypotheses (FB, PB, and other major motifs) are adjusted using the Benjamini-Hochberg False Discovery Rate (FDR) procedure at $q = 0.05$.

---

## 4. Sampling Budget and Computational Feasibility

| Stage / Analysis | Target Permutations ($B$) | Swaps / Operations per Permutation | Estimated Runtime | Peak RAM Budget |
|---|---|---|---|---|
| **Tier 1: Topological MCMC Null** | $B = 200$ | $20\times |E|$ swaps ($316\text{k}$ swaps/perm in EB) | $\sim 20\text{--}30\text{ min}$ | $< 500\text{ MB}$ |
| **Tier 2: Primary Conditional Null** | $B = 2,000$ | Stratified array shuffle (483 nodes) | $\sim 1\text{--}2\text{ min}$ | $< 300\text{ MB}$ |
| **Tier 2: Secondary FB & PB Null** | $B = 2,000$ | Stratified array shuffle (FB: 2,465 nodes) | $\sim 3\text{--}5\text{ min}$ | $< 400\text{ MB}$ |
| **Robustness Sensitivity ($w \ge 3$)** | $B = 2,000$ | Stratified array shuffle | $\sim 3\text{--}5\text{ min}$ | $< 400\text{ MB}$ |

*Feasibility*: Because the Tier 2 conditional null operates directly on node arrays and empirical dyad lists, $B = 2,000$ permutations can be computed rapidly while meeting the hardware RAM limit ($< 2.5\text{ GiB}$) and delivering high statistical resolution ($p_{\text{min}} = 1 / 2,001 \approx 0.000499$).

---

## 5. Non-Negotiable Interpretation Standards

1. **Topological vs. Compositional Distinction**:
   Every report and figure must explicitly state both the **Topological Reciprocity Ratio** ($M_{\text{obs}} / M_{\text{swap\_null}}$) and the **Conditional Chemical Enrichment** ($C_{\text{obs}} / C_{\text{strat\_null}}$).
2. **No Dynamic or Physiological Claims**:
   - A high frequency of $GABA \leftrightarrow GABA$ mutual dyads indicates structural recurrent feedback between GABAergic neurons (e.g. ring neurons).
   - It **does not** prove functional inhibition, attractor stabilization, or gain control in vivo. Those require electrophysiological or optical validation.
3. **Classification Caution**:
   Consensus phenotypes represent whole-cell aggregate predictions from Eckstein et al. (2024); connection-level probabilities must be reported alongside consensus metrics.

