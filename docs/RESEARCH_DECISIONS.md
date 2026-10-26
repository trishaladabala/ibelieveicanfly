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
*"Under fine-grained k-NN degree micro-stratification (k=8, 308 strata), degree characteristics account for ~50% of the apparent signal (reducing enrichment from ~5.7x to ~2.5x), but an irreducible 2.53-fold biological excess persists (Z = +6.19, p = 0.000999, 95% Bootstrap CI: [2.34x, 2.73x])."*

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

## Decision 3: Replacing Misleading Null Simulation Intervals with Bootstrap Confidence Intervals for Biological Effect Sizes

### 1. Original Issue
In Table 5.2 of the original report, the column labeled `95% Empirical CI` displayed intervals like `[48, 157]`. Because the observed count was 554, this interval represented the central 95% range of the *null distribution* under $H_0$, but was confusingly presented as if it were a confidence interval for the biological effect.

### 2. What the Evidence Showed
Reviewers and committee members would immediately notice that an effect of 554 with a "confidence interval" of $[48, 157]$ is a contradiction. The range $[48, 157]$ quantifies Monte Carlo simulation variability under the null hypothesis, not uncertainty in the true biological enrichment ratio.

### 3. The Correction
1. Relabeled the null quantile column to `95% Null Simulation Range` ($[q_{0.025}, q_{0.975}]$).
2. Implemented non-parametric bootstrap resampling of mutual dyads ($B = 2,000$ resamples) in `scripts/run_sensitivity_and_controls.py` to construct genuine 95% confidence intervals for the observed biological enrichment ratios:
   - Model 1 (Mutual Quartiles): Point Est = 5.92x, 95% Bootstrap CI: $[5.48\times, 6.40\times]$
   - Model 2 (Joint Tertiles): Point Est = 5.69x, 95% Bootstrap CI: $[5.27\times, 6.15\times]$
   - Model 3 (Joint Medians): Point Est = 5.45x, 95% Bootstrap CI: $[5.04\times, 5.89\times]$
   - Model 4 (Total Quintiles): Point Est = 4.96x, 95% Bootstrap CI: $[4.59\times, 5.36\times]$
   - k-NN ($k=16$): Point Est = 2.75x, 95% Bootstrap CI: $[2.54\times, 2.97\times]$
   - k-NN ($k=8$): Point Est = 2.53x, 95% Bootstrap CI: $[2.34\times, 2.73\times]$

### 4. Scientific Rationale
Distinguishing between the null distribution's quantiles under $H_0$ and the estimator's sampling uncertainty under $H_1$ is a foundational requirement of research statistics.

### 5. Effect on Conclusions
The statistical results now present both the null expectation and the sampling uncertainty of the effect size with mathematical rigor.

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
