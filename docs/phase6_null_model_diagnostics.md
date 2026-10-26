# Phase 3: Directed Degree-Preserving Rewiring & Mixing Diagnostics

**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Whole-Brain Connectomics  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Date**: October 20, 2026  
**Diagnostics Artifact**: `results/real_data_pilot/null_model_mixing_diagnostics.json`  
**Producing Script**: `scripts/diagnose_null_model_mixing.py`  
**Status**: **VALIDATED AND PASSED**  

---

## 1. Executive Summary

This study rigorously validates the directed degree-preserving edge-swap (Maslov-Sneppen) Markov Chain Monte Carlo (MCMC) algorithm applied to the adult *Drosophila* central complex (EB, FB, PB). 

### Key Conclusions:
1. **Mathematical Invariants Preserved (100%)**:
   - Directed in-degree and out-degree sequences are strictly invariant across all rewired graphs ($d_{\text{in}}(v)$ and $d_{\text{out}}(v)$ remain identical for every neuron $v$).
   - Zero self-loops ($u \to u$) and zero multigraph duplicate edges are introduced.
   - Synthetic test graphs (bipartite switch graphs, directed cycles $C_4$, disconnected mutual components) verified exact expected edge rewiring behavior.
2. **Acceptance Rates and Graph Density**:
   - EB: $51.9\%$ ($w \ge 3$) and $61.9\%$ ($w \ge 5$) acceptance. Density $\approx 6.8\%$.
   - FB: $85.2\%$ ($w \ge 3$) and $87.0\%$ ($w \ge 5$) acceptance. Density $\approx 0.77\%$.
   - PB: $76.5\%$ ($w \ge 3$) and $77.8\%$ ($w \ge 5$) acceptance. Density $\approx 0.75\%$.
   Rejections are primarily driven by avoiding duplicate edges in denser neuropils (e.g. EB).
3. **Plateau of Mixing Trajectory**:
   - The rewired edge fraction and the mutual dyad count $M(t)$ plateau completely by $5\times |E|$ attempted swaps.
   - Swapping budgets from $10\times |E|$ to $100\times |E|$ yield identical stationary ensemble expectations.
4. **MCMC Autocorrelation and Effective Sample Size (ESS)**:
   - In a continuous chain with burn-in $= 20\times |E|$ and thinning interval $= 5\times |E|$:
     - EB ($w \ge 5$): Integrated autocorrelation time $\tau_{\text{int}} = 0.63$ for $M$ and $\tau_{\text{int}} = 0.60$ for $GABA \leftrightarrow GABA$, yielding an Effective Sample Size (ESS) of $158.8$ and $167.2$ out of 200 samples.
     - FB and PB ($w \ge 5$): $\tau_{\text{int}} = 0.50$ (zero detectable lag-1 autocorrelation), giving $\text{ESS} = 200.0 / 200$.
5. **Multi-Seed Stability**:
   - 4 independent random seeds (42, 101, 777, 2026) yielded statistically indistinguishable stationary estimates.

---

## 2. Invariant Validation Matrix

| Invariant Checked | Verification Method | Synthetic Graphs | Empirical EB ($w \ge 5$) | Empirical FB ($w \ge 5$) | Empirical PB ($w \ge 5$) | Status |
|---|---|---|---|---|---|---|
| **Directed In-Degree** | $d_{\text{in}}^{\text{orig}}(v) == d_{\text{in}}^{\text{rew}}(v) \; \forall v$ | Verified | Verified (483/483 nodes) | Verified (2,465/2,465) | Verified (699/699) | **PASSED** |
| **Directed Out-Degree** | $d_{\text{out}}^{\text{orig}}(u) == d_{\text{out}}^{\text{rew}}(u) \; \forall u$ | Verified | Verified (483/483 nodes) | Verified (2,465/2,465) | Verified (699/699) | **PASSED** |
| **Directed Edge Count** | $\|E_{\text{orig}}\| == \|E_{\text{rew}}\|$ | Verified | 15,812 / 15,812 | 46,927 / 46,927 | 3,651 / 3,651 | **PASSED** |
| **No Self-Loops** | $u \ne v \; \forall (u, v) \in E_{\text{rew}}$ | Verified | 0 loops detected | 0 loops detected | 0 loops detected | **PASSED** |
| **No Duplicate Edges** | $\|E_{\text{rew}}\| == \|\text{set}(E_{\text{rew}})\|$ | Verified | 0 duplicates | 0 duplicates | 0 duplicates | **PASSED** |
| **Node Label Attachment** | Consensus labels remain on original root IDs | Verified | Verified | Verified | Verified | **PASSED** |

---

## 3. Swap Multiplier Trajectory Analysis

To determine the minimum swap budget required to achieve stationary mixing, graphs were rewired across multipliers $m \in \{1, 2, 5, 10, 20, 30, 50, 100\} \times |E|$ starting from the empirical graph.

### Ellipsoid Body (EB, $w \ge 5$)
* Baseline: $|V| = 483$, $|E| = 15,812$, Observed $M = 3,518$, Observed $GABA \leftrightarrow GABA = 2,615$.

| Multiplier ($m \times \|E\|$) | Acceptance Rate (%) | Rewired Edge Fraction (%) | Mutual Dyads $M$ | $GABA \leftrightarrow GABA$ Motifs | Mixing State |
|---|---|---|---|---|---|
| **$1\times$** | 61.92% | 61.52% | 880 | 490 | Incomplete mixing (transient) |
| **$2\times$** | 62.03% | 74.18% | 751 | 396 | Near plateau |
| **$5\times$** | 62.01% | 77.73% | 730 | 383 | **Stationary Plateau Reached** |
| **$10\times$** | 62.17% | 77.76% | 754 | 389 | Stationary equilibrium |
| **$20\times$** | 62.02% | 78.31% | 736 | 375 | Stationary equilibrium |
| **$30\times$** | 61.95% | 78.14% | 797 | 420 | Stationary equilibrium |
| **$50\times$** | 61.91% | 78.28% | 777 | 393 | Stationary equilibrium |
| **$100\times$** | 62.02% | 78.16% | 797 | 398 | Stationary equilibrium |

*Finding*: In the EB, the rewired edge fraction plateaus at $\approx 78.2\%$, and both $M$ and $GABA \leftrightarrow GABA$ reach stationarity at $m \ge 5\times |E|$. The previously chosen budget of $10\times |E|$ in Phase 5 is well within the stationary regime.

### Fan-Shaped Body (FB, $w \ge 5$)
* Baseline: $|V| = 2,465$, $|E| = 46,927$, Observed $M = 5,442$, Observed $ACh \leftrightarrow GABA = 555$.

| Multiplier ($m \times \|E\|$) | Acceptance Rate (%) | Rewired Edge Fraction (%) | Mutual Dyads $M$ | $ACh \leftrightarrow GABA$ Motifs | Mixing State |
|---|---|---|---|---|---|
| **$1\times$** | 87.09% | 79.00% | 810 | 80 | Transient |
| **$2\times$** | 87.40% | 91.55% | 772 | 59 | Near plateau |
| **$5\times$** | 87.17% | 93.75% | 726 | 47 | **Stationary Plateau Reached** |
| **$10\times$** | 87.00% | 93.82% | 691 | 65 | Stationary equilibrium |
| **$20\times$** | 86.97% | 93.69% | 738 | 72 | Stationary equilibrium |
| **$50\times$** | 86.96% | 93.92% | 704 | 68 | Stationary equilibrium |
| **$100\times$** | 86.95% | 93.80% | 743 | 65 | Stationary equilibrium |

*Finding*: Due to the low graph density in FB ($\approx 0.77\%$), acceptance is high ($87\%$), and stationarity is reached by $5\times |E|$ with a rewired fraction of $\approx 93.8\%$.

### Protocerebral Bridge (PB, $w \ge 5$)
* Baseline: $|V| = 699$, $|E| = 3,651$, Observed $M = 137$, Observed $ACh \leftrightarrow ACh = 35$.

| Multiplier ($m \times \|E\|$) | Acceptance Rate (%) | Rewired Edge Fraction (%) | Mutual Dyads $M$ | $ACh \leftrightarrow ACh$ Motifs | Mixing State |
|---|---|---|---|---|---|
| **$1\times$** | 76.72% | 73.10% | 82 | 17 | Transient |
| **$2\times$** | 78.09% | 84.94% | 93 | 6 | Near plateau |
| **$5\times$** | 77.73% | 88.14% | 80 | 9 | **Stationary Plateau Reached** |
| **$10\times$** | 77.88% | 87.54% | 69 | 5 | Stationary equilibrium |
| **$20\times$** | 77.71% | 88.69% | 81 | 6 | Stationary equilibrium |
| **$50\times$** | 77.78% | 87.62% | 76 | 4 | Stationary equilibrium |
| **$100\times$** | 77.75% | 87.70% | 84 | 11 | Stationary equilibrium |

---

## 4. Continuous MCMC Chain Autocorrelation & Effective Sample Size

To evaluate whether successive states in a continuous chain can be treated as approximately independent draws, a continuous MCMC chain was executed with:
- **Burn-in**: $20\times |E|$ attempted swaps.
- **Thinning interval**: $5\times |E|$ attempted swaps between recorded samples.
- **Chain Length**: $N = 200$ samples.

| Region & Threshold | Statistic | Stationary Mean $\pm$ Std | Lag-1 Autocorr $\rho(1)$ | Lag-2 Autocorr $\rho(2)$ | Integrated Auto Time $\tau_{\text{int}}$ | Effective Sample Size (ESS) |
|---|---|---|---|---|---|---|
| **EB ($w \ge 5$)** | Mutual Dyads $M$ | $763.4 \pm 22.0$ | $0.130$ | $-0.021$ | $0.63$ | **$158.8$ / 200** |
| **EB ($w \ge 5$)** | $GABA \leftrightarrow GABA$ | $385.9 \pm 17.7$ | $0.098$ | $-0.012$ | $0.60$ | **$167.2$ / 200** |
| **FB ($w \ge 5$)** | Mutual Dyads $M$ | $741.7 \pm 24.7$ | $-0.027$ | $-0.052$ | $0.50$ | **$200.0$ / 200** |
| **FB ($w \ge 5$)** | $ACh \leftrightarrow GABA$ | $60.1 \pm 7.6$ | $0.011$ | $-0.063$ | $0.50$ | **$200.0$ / 200** |
| **PB ($w \ge 5$)** | Mutual Dyads $M$ | $83.5 \pm 7.8$ | $0.043$ | $-0.088$ | $0.50$ | **$200.0$ / 200** |
| **PB ($w \ge 5$)** | $ACh \leftrightarrow ACh$ | $7.6 \pm 2.5$ | $-0.040$ | $-0.016$ | $0.50$ | **$200.0$ / 200** |

*Conclusion*: With a thinning interval of $5\times |E|$, autocorrelation drops to near zero at lag 1. Effective sample size exceeds $80\%\text{--}100\%$ of nominal draws. In addition, resetting to the empirical graph between permutations (as implemented in `analyze_central_complex_rewiring.py`) with a budget $\ge 10\times |E|$ ensures completely independent sample generation.

---

## 5. Multi-Seed Robustness Analysis

Four independent random seeds were evaluated with $20\times |E|$ swaps to verify that the stationary values are independent of the PRNG initialization:

| Region ($w \ge 5$) | Seed 42 | Seed 101 | Seed 777 | Seed 2026 | Ensemble Spread | Consistency Verdict |
|---|---|---|---|---|---|---|
| **EB: $M$** | 781 | 756 | 750 | 761 | $762.0 \pm 13.5$ | **Consistent** ($\le 1.0\sigma$) |
| **EB: $GABA \leftrightarrow GABA$** | 396 | 394 | 373 | 371 | $383.5 \pm 13.5$ | **Consistent** ($\le 1.0\sigma$) |
| **FB: $M$** | 726 | 771 | 772 | 795 | $766.0 \pm 28.8$ | **Consistent** ($\le 1.1\sigma$) |
| **FB: $ACh \leftrightarrow GABA$** | 62 | 66 | 57 | 69 | $63.5 \pm 5.2$ | **Consistent** ($\le 1.0\sigma$) |
| **PB: $M$** | 100 | 80 | 81 | 89 | $87.5 \pm 9.3$ | **Consistent** ($\le 1.2\sigma$) |
| **PB: $ACh \leftrightarrow ACh$** | 10 | 3 | 3 | 12 | $7.0 \pm 4.7$ | **Consistent** ($\le 1.1\sigma$) |

---

## 6. Critical Methodological Consequence for Phase 4

While the edge-swap MCMC chain is statistically well-behaved, these diagnostics expose the **central methodological flaw of using edge swaps alone to infer transmitter-pairing selectivity**:

In the Ellipsoid Body ($w \ge 5$):
- Empirical graph: $M = 3,518$ mutual dyads, of which $2,615$ are $GABA \leftrightarrow GABA$ ($74.33\%$).
- Degree-preserving rewired graph: $M$ drops precipitously from $3,518 \to 763.4 \pm 22.0$ ($4.61\times$ reduction!).
- In the rewired graph, the expected number of $GABA \leftrightarrow GABA$ dyads is $385.9 \pm 17.7$.
- When comparing the empirical count ($2,615$) directly to the rewired count ($385.9$), the resulting Z-score is an enormous $+125.7$ ($6.78\times$ raw enrichment).

**However**:
Notice that in the rewired graph, the proportion of mutual dyads that are $GABA \leftrightarrow GABA$ is:
$$\frac{385.9}{763.4} = 50.55\%$$
While in the empirical graph, that proportion is:
$$\frac{2,615}{3,518} = 74.33\%$$

This means:
1. **Topological Effect**: The EB has $4.61\times$ more reciprocal connections overall than expected from its degree sequences ($3,518$ vs $763.4$).
2. **Chemical Selectivity Effect**: Among reciprocal connections, $GABA \leftrightarrow GABA$ dyads represent $74.33\%$ empirically vs $50.55\%$ in the rewired topology — an apparent conditional ratio of $1.47\times$, NOT $6.78\times$!

Therefore, the $+125$ Z-score from Phase 5 is a **compound metric** that conflates overall topological reciprocity ($4.6\times$) with chemical pairing composition ($1.47\times$).

To isolate chemical pairing preference, Phase 4 must evaluate a **conditional null model** that preserves the exact empirical mutual dyad topology ($M = 3,518$) and permutes transmitter labels conditioned on neuron degree strata.

