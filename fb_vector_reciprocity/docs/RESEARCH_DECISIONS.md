# VectorWing: Record of Scientific Research Decisions

**Document**: Chronological and Methodological Log of Audit Decisions  
**Repository**: `/home/trishal/ibelieveicanfly/fb_vector_reciprocity/`  
**Date**: October 26, 2026  

---

## Decision 1: Formal Withdrawal of the Degree-Penalized MCMC Sampler

### 1. Original Issue
The report claimed that an unconstrained continuous Metropolis–Hastings label-swapping sampler with acceptance probability $\alpha(u, v) = \exp(-\|d_u - d_v\|^2 / 2\sigma_d^2)$ ($\sigma_d = 0.20$, 1.55M steps) confirmed that the ACh–GABA reciprocal excess retained a $1.20\times$ (+20.4%) margin under continuous degree penalization ($Z = +2.80, p = 0.01587$).

### 2. What the Evidence Showed
Mathematical derivation proved that the proposal distribution $q(X' \mid X)$ and the acceptance probability $\alpha(X \to X') = \exp(-\|d_u - d_v\|^2 / 2\sigma_d^2)$ depend solely on the fixed node degree coordinates $d_u, d_v$, and not on the state $X$ or the change in any energy function $H(X)$.
Because $T(X \to X') = T(X' \to X)$, the transition matrix is doubly stochastic. By the fundamental theorem of Markov chains, its unique stationary distribution is the **uniform distribution over all permutations**.
Numerical simulation (`scripts/audit_and_diagnose_mcmc.py`) showed that:
- When initialized from the empirical state ($obs = 554$), the chain slowly wanders downward (reaching 420 at 150k steps).
- When initialized from a random permutation ($obs = 368$), the chain wanders upward (reaching 406 at 150k steps).
- The reported null mean of ~460 was simply the transient state of an incompletely mixed chain after 1.55M steps with a 93.3% proposal rejection rate.

### 3. The Correction
Formally withdrew the MCMC sampler from the primary scientific claims. Excluded its estimates from the headline tables in the research report, README, and demo. Retained the failed method in `docs/SCIENTIFIC_AUDIT.md` and `scripts/audit_and_diagnose_mcmc.py` as an audited methodological lesson.

### 4. Scientific Rationale
A researcher must never report a number as evidence of continuous degree conditioning when the underlying sampler actually targets an unconditioned uniform distribution and merely suffers from slow mixing.

### 5. Effect on Conclusions
The headline claim changes from *"resilient to degree conditioning down to 1.20x under MCMC"* to the scientifically defensible claim:
*"Under fine-grained k-NN degree micro-stratification (k=8, 308 strata), degree constraints attenuate enrichment from ~5.7x to 2.53x, but a robust conditional association persists (Z = +6.19, p = 0.000999, 95% Monte Carlo CI: [2.49x, 2.57x])."*

### 6. Remaining Limitations
Exact continuous conditioning on degree sequence remains an open problem in network permutation testing due to the curse of dimensionality; discrete micro-stratification ($k=8$) is the most defensible bounded-variance approximation feasible on commodity hardware.

---

## Decision 2: Reclassification of Dynamical Model from "Divisive Gain Control" to "Recurrent Subtractive Inhibitory Feedback"

### 1. Original Issue
The report claimed that a 16-column continuous-attractor rate model proved that intact reciprocal feedback provides "9.72x divisive gain suppression" and enables "sub-degree directional steering decoding (< 0.8°) across flight velocities."

### 2. What the Evidence Showed
1. The mathematical differential equation:
   $$\tau_{\text{col}} \frac{dr_i}{dt} = -r_i + \left[ I_i + \text{lateral} - W_{\text{inh}} r_{\text{tan}} \right]_+$$
   subtracts $W_{\text{inh}} r_{\text{tan}}$ linearly from the input inside rectification. Firing rate curves plotted in `scripts/stress_test_dynamics.py` scale linearly with input drive $I_0 \in [1, 30]$ (constant slope), lacking the saturating hyperbolic curvature of divisive normalization ($\frac{I}{\sigma + \sum I}$).
2. The sub-degree angular decoding precision ($< 0.8^\circ$) was an artifact of noiseless circular symmetry in the input, lateral weights, and global inhibition. Under 20% sensory noise, mean decoding error rises to $5.65^\circ$.
3. When lateral excitation exceeds $J_{\text{col}} \ge 0.60$, the system diverges into supercritical runaway excitation ($> 3.8\times 10^6$ Hz).

### 3. The Correction
Reclassified the simulation as an exploratory rate-based proof-of-concept demonstrating that recurrent subtractive feedback prevents rate explosion and bounds spatial tuning width ($90.0^\circ$ FWHM) in recurrent columnar circuits. Withdrew claims of having proven biological divisive normalization or decoding precision.

### 4. Scientific Rationale
Conflating subtractive threshold-linear feedback with divisive normalization is mathematically incorrect. Connectomic synapse counts are uncalibrated structural proxies, not direct physiological conductances.

### 5. Effect on Conclusions
The dynamical model is properly framed as a computational illustration consistent with the anatomical feedback architecture, rather than empirical proof of in vivo neurophysiology.

---

## Decision 3: Resolving Null Quantiles, Auditing the Dyad Bootstrap, and Reporting Monte Carlo Precision

### 1. Original Issue
In Table 5.2 of the original report, the column labeled `95% Empirical CI` displayed intervals like `[48, 157]`. Because the observed count was 554, this interval represented the central 95% range of the *null distribution* under $H_0$, but was confusingly presented as if it were a confidence interval for the biological effect. Subsequently, a naive dyad-level bootstrap was proposed to estimate confidence intervals for the enrichment ratio.

### 2. What the Evidence Showed
1. Conflating null quantiles with effect CIs: Reviewers would immediately identify that an effect of 554 with an interval of $[48, 157]$ represents the null simulation spread under $H_0$, not uncertainty in the true biological ratio.
2. Naive dyad bootstrap failure: Detailed recomputation revealed that all 554 ACh–GABA mutual dyads are formed by **just 16 distinct GABAergic tangential neurons** and 256 cholinergic columnar neurons (an average of 34.6 dyads per GABA neuron). Dyads sharing hub neurons are strongly mutually dependent. Treating dyads as independent Bernoulli observations severely violates the fundamental exchangeability assumption of the bootstrap.
3. Single-specimen limitation: With only $N=1$ connectome, population-level sampling variability across fruit flies is mathematically unidentifiable. Resampling dyads also destroys the empirical graph topology.

### 3. The Correction
1. Relabeled the null quantile column to `95% Null Simulation Range` ($[q_{0.025}, q_{0.975}]$).
2. Formally withdrew the naive dyad bootstrap confidence intervals from the headline results and figures.
3. Evaluated exact Monte Carlo simulation precision for the null means ($\text{SE}_{\text{MC}} = s_{\text{null}} / \sqrt{B} \le 0.04\times$ on the ratios) and reported the corresponding Monte Carlo precision intervals:
   - Model 1 (Mutual Quartiles): Point Est = 5.92x, 95% Monte Carlo CI: $[5.85\times, 5.99\times]$
   - Model 2 (Joint Tertiles): Point Est = 5.69x, 95% Monte Carlo CI: $[5.62\times, 5.76\times]$
   - Model 3 (Joint Medians): Point Est = 5.45x, 95% Monte Carlo CI: $[5.39\times, 5.51\times]$
   - Model 4 (Total Quintiles): Point Est = 4.96x, 95% Monte Carlo CI: $[4.90\times, 5.02\times]$
   - k-NN ($k=16$): Point Est = 2.75x, 95% Monte Carlo CI: $[2.70\times, 2.79\times]$
   - k-NN ($k=8$): Point Est = 2.53x, 95% Monte Carlo CI: $[2.49\times, 2.57\times]$

### 4. Scientific Rationale
Rigorous science does not report an invalid bootstrap interval merely because it looks like a standard confidence interval. Documenting why dyad-level bootstrapping fails in hub-dominated networks demonstrates methodological integrity.

### 5. Effect on Conclusions
The statistical results clearly separate the null distribution dispersion under $H_0$, the Monte Carlo simulation precision, and the single-specimen nature of the connectomic dataset.

---

## Decision 4: Incorporating Negative and Positive Controls

### 1. Original Issue
The original repository had unit tests that merely loaded precomputed JSON files and checked whether numbers matched hardcoded constants, without testing whether the algorithms could detect known ground truth or reject synthetic null networks.

### 2. What the Evidence Showed
The test suite did not verify algorithmic validity on synthetic graphs.

### 3. The Correction
Added `scripts/run_sensitivity_and_controls.py` and `tests/test_scientific_rigor.py`:
- Synthetic Negative Control: Random Erdős–Rényi graphs with matching transmitter proportions yielded enrichment ratio $1.04\times$, $Z = +0.78, p = 0.43$, verifying zero false-positive bias.
- Synthetic Positive Control: Synthetic graphs with spiked ACh–GABA pairs yielded enrichment ratio $1.61\times$, $Z = +11.34, p = 0.001$, verifying high statistical power.

### 4. Scientific Rationale
Negative controls demonstrate that an algorithm does not report spurious associations in random data.

### 5. Effect on Conclusions
Provides prospective reviewers with concrete evidence of pipeline specificity and sensitivity.

---

## Decision 5: Standardization of Complete 6-Figure Presentation Suite (Phase 10)

### 1. Original Issue
The prior attempt only produced 4 figures with mismatched numbering, completely missing Figure 1 (Network and Pipeline Overview) and Figure 4 (Statistical Robustness comparison across valid null models with visible disagreement and MCMC diagnostic drift).

### 2. What the Evidence Showed
Phase 10 explicitly specified 5 prioritized figures:
- Figure 1: Network & Pipeline Overview
- Figure 2: Observed Transmitter-Pair Associations
- Figure 3: Neuronal & Anatomical Organization
- Figure 4: Statistical Robustness
- Figure 5: Dynamical Model & Stress Testing
In addition, Figure 6 provides the architectural dichotomy between EB (1D compass) and FB (2D steering).

### 3. The Correction
Rewrote `scripts/generate_fb_figures.py` to programmatically render all 6 publication figures into vector SVG and 300dpi PNG formats, while maintaining backward-compatible aliases for legacy scripts.

### 4. Scientific Rationale
A portfolio-ready scientific repository must provide visual figures that directly map to the research narrative and explicitly expose model differences and diagnostic failures.

---

## Decision 6: Identification of Tangential GABA Prediction Confidence Floor

### 1. Original Issue
Transmitter prediction confidence sensitivity testing indicated that at threshold $\ge 0.80$, ACh–GABA mutual dyads dropped to 0, but the root cause was undocumented.

### 2. What the Evidence Showed
Forensic analysis of whole-neuron confidence distributions in `data/fb_node_covariates.json` revealed that GABAergic tangential neurons (`FB5A`, `FB4A`, `FB5I2`) have an empirical maximum confidence ceiling of $0.7873$ (median $0.7812$) in Eckstein et al. (2024), whereas columnar cholinergic neurons reach $0.8977$. Applying a naive global threshold of $\ge 0.80$ completely excises the entire tangential inhibitory population from the graph.

### 3. The Correction
Documented the 0.7873 ceiling in the report, validation trail, interview guide, and added automated unit tests verifying the confidence floor in `tests/test_scientific_rigor.py`.

### 4. Scientific Rationale
Connectomics researchers must understand that machine-learning confidence scores are non-uniform across cell types with distinct arborization geometries.

---

## Decision 7: Elimination of Lingering Inconsistencies in Automated Test Suite

### 1. Original Issue
The legacy test file `tests/test_fb_vector_reciprocity.py` still contained `test_continuous_mcmc_benchmark` asserting that the invalid MCMC model "preserves statistical significance", and `test_divisive_gain_control_suppression` claiming divisive normalization. Furthermore, `tests/test_scientific_rigor.py` promised synthetic controls in its docstring but never implemented the test class.

### 2. What the Evidence Showed
Lingering contradictions between audited text and passing unit tests create severe credibility risks during code inspection by prospective supervisors.

### 3. The Correction
1. Refactored `tests/test_fb_vector_reciprocity.py` to test that k-NN continuous degree micro-stratification is the valid benchmark and renamed the dynamical test to reflect subtractive inhibitory attenuation.
2. Implemented `TestSyntheticControls` (negative & positive controls), `TestConfidenceSensitivityAndFloor`, and `TestPublicationFigureArtifacts` in `tests/test_scientific_rigor.py`, expanding the test suite to 40 comprehensive unit tests.

### 4. Scientific Rationale
Code, tests, and documentation must be 100% consistent and mutually reinforcing.

---

## Decision 8: Correction of MCMC Stationary Null Expectation (393.78 dyads vs 93.6)

### 1. Original Issue
The prior audit correctly identified that the MCMC transition matrix is doubly stochastic, but asserted that the chain was converging toward the "unconditioned null mean ~94" (conflating it with Model 1 Mutual Quartiles mean 93.6). Figure 4 plotted a dashed baseline at 94.

### 2. What the Evidence Showed
The theoretical unconditioned uniform stationary distribution over label permutations has exact expectation:
$$E[T] = M \cdot \frac{2 N_{\text{ach}} N_{\text{gaba}}}{N(N-1)} = 5435 \times \frac{2 \times 1528 \times 144}{2465 \times 2464} = 393.78 \text{ dyads}$$
Forensic MCMC simulations verified that empirical initialization (554) drifts down to 420, while random initialization (368) drifts up to 406 after 150k steps.

### 3. The Correction
Corrected theoretical stationary expectation to 393.78 dyads across scripts, test suite (`test_theoretical_uniform_stationary_expectation`), documentation, and Figure 4 Panel B.

### 4. Scientific Rationale
Conflating distinct null baselines undermines mathematical credibility. A rigorous audit must state the exact analytic stationary distribution.

---

## Decision 9: Synthetic Ground-Truth Bootstrap Coverage Verification

### 1. Original Issue
The naive dyad bootstrap was withdrawn on theoretical grounds (hub clustering among 16 GABA neurons), but lacked empirical verification of coverage failure.

### 2. What the Evidence Showed
Simulating 200 synthetic realizations with 16 hub neurons matching the FB topology demonstrated that naive dyad bootstrap nominal 95% confidence intervals achieve only **55.6% empirical coverage** (a 7.2-fold variance underestimation), whereas hub/cluster-aware block bootstrap recovers **91.6% coverage**.

### 3. The Correction
Integrated `run_synthetic_bootstrap_coverage_test` into `scripts/run_sensitivity_and_controls.py` and added `test_synthetic_bootstrap_coverage_failure` in `tests/test_scientific_rigor.py`.

### 4. Scientific Rationale
Provides rigorous, quantitative proof demonstrating why naive dyad resampling fails under hub-dominated graph structures.

---

## Decision 10: Statistical Concentration of Layer 4 & 5 Reciprocity and DOI Corrections

### 1. Original Issue
The 99.10% concentration of ACh–GABA loops in Layers 4 & 5 was described purely descriptively without testing against background mutual dyads, and citations for Turner-Evans et al. (2020) and Lin et al. (2024) contained broken DOIs.

### 2. What the Evidence Showed
Across all $M = 5,435$ mutual dyads, $2,196$ ($40.40\%$) reside in Layers 4 & 5. For ACh–GABA loops, $549 / 554$ ($99.10\%$) reside in Layers 4 & 5. Fisher's exact test yields Odds Ratio = 215.60, hypergeometric $p = 3.36 \times 10^{-226}$. Turner-Evans (2020) is published in *Neuron* (`10.1016/j.neuron.2020.08.006`), and Lin et al. (2024) is `10.1038/s41586-024-07968-y`.

### 3. The Correction
Integrated Fisher's exact test into `scripts/analyze_layer_column_anatomy.py`, added `test_layer_4_5_fisher_exact_enrichment` in `tests/test_scientific_rigor.py`, and verified and updated all literature citations.

### 4. Scientific Rationale
Elevates descriptive anatomy into a statistically validated discovery while ensuring flawless literature provenance.
