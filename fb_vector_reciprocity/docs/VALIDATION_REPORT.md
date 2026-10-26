# VectorWing: Validation & Forensic Audit Trail

**Document**: Scientific and Computational Validation Report  
**Project**: VectorWing Connectomics (`fb_vector_reciprocity`)  
**Hardware Executed**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04 LTS)  
**Date**: October 26, 2026  

---

## 1. Audit Trail: Commands Executed & Runtimes

| Phase / Operation | Command Executed | Runtime | RAM | Result / Status |
|---|---|:---:|:---:|---|
| **Raw Connectome Ingestion** | `python3 scripts/extract_fb_subgraph.py --threshold 5` | 194.34 s | 272 MB | **Passed**: 16,847,997 records processed; extracted 2,465 active nodes, 46,903 edges, 5,435 mutual dyads ($R_{\text{edge}} = 23.18\%$). |
| **Controlled Permutation Study** | `python3 scripts/run_fb_controlled_study.py` | 78.42 s | 312 MB | **Passed**: 4 degree-stratified models (B=2,000 each); ACh-GABA enrichment 4.96x–5.92x (q < 0.003). |
| **Continuous Degree k-NN & MCMC** | `python3 scripts/run_continuous_degree_model.py` | 20.11 s | 375 MB | **Passed (k-NN)**: k=16 (2.75x) and k=8 (2.53x, p=0.000999). **Audited (MCMC)**: uniform stationarity diagnosed. |
| **Cellular & Layer Anatomy** | `python3 scripts/analyze_layer_column_anatomy.py` | 1.48 s | 240 MB | **Passed**: 100% annotation match (2,465 nodes); 99.46% Col-Tan; 100% directional polarity; 99.10% in L4/5. |
| **Dynamical Model Simulation** | `python3 scripts/simulate_vector_steering_dynamics.py` | 1.15 s | 120 MB | **Passed**: 16 columns across 9 drive levels; intact vs ablated comparison. |
| **MCMC Forensic Diagnosis** | `python3 scripts/audit_and_diagnose_mcmc.py` | 2.10 s | 130 MB | **Passed**: Proven transition symmetry; uniform stationarity verified. |
| **Dynamical Stress Testing** | `python3 scripts/stress_test_dynamics.py` | 3.82 s | 125 MB | **Passed**: Linear subtractive gain diagnosed; supercritical instability at $J_{\text{col}} \ge 0.60$ found; noise decoding quantified. |
| **Sensitivity & Negative Controls** | `python3 scripts/run_sensitivity_and_controls.py` | 4.82 s | 140 MB | **Passed**: Confidence sensitivity mapped; negative control passed ($p=0.43$); bootstrap CIs computed. |
| **Figure Generation** | `python3 scripts/generate_fb_figures.py` | 2.10 s | 175 MB | **Passed**: All 6 presentation figures (and backward-compatible aliases) rendered to vector SVG and 300dpi PNG. |
| **Interactive CLI Demo** | `python3 demo.py` | 0.06 s | 85 MB | **Passed**: Instant CLI presentation of validated findings. |
| **Legacy Invariant Suite** | `python3 -m unittest tests/test_fb_vector_reciprocity.py` | 0.28 s | 75 MB | **Passed**: 21 / 21 tests passed (audited docstrings & interpretations). |
| **Scientific Rigor Suite** | `python3 -m unittest tests/test_scientific_rigor.py` | 2.55 s | 90 MB | **Passed**: 19 / 19 tests passed (includes synthetic controls, confidence floor, figure artifacts, MCMC uniform stationarity, synthetic bootstrap coverage failure, Fisher exact test). |
| **Full Combined Test Suite** | `python3 -m unittest discover -s tests -v` | 2.95 s | 95 MB | **Passed**: 40 / 40 tests passed. |

---

## 2. Statistical Comparisons: Original Headline vs Audited Validated

| Analysis Specification | Original Headline Claim | Audited Validated Finding | Status & Scientific Rationale |
|---|---|---|---|
| **Graph Statistics** | $N=2,465$, $E=46,903$, $M=5,435$ | $N=2,465$, $E=46,903$, $M=5,435$ | **Verified**: Recomputed from raw 852 MB Feather connectome with 0 discrepancy. |
| **Edge Reciprocity** | $R_{\text{edge}} = 23.18\%$ | $R_{\text{edge}} = 23.1755\%$ | **Verified**: Formula $2M/E$ exact. Ranks #6 among 79 neuropils in fly brain. |
| **Discrete Null Models (1–4)** | $5.45\times$ to $5.92\times$ ($Z > +15, p = 0.0005$) | $4.96\times$ to $5.92\times$ ($Z = +15.3$ to $+17.7, p = 0.0005$) | **Verified**: Recomputed with B=2,000 permutations. 95% Monte Carlo CI: $[4.90\times, 5.99\times]$. |
| **Null Range Labeling** | Labeled "95% Empirical CI" | Corrected to "95% Null Simulation Range" | **Corrected**: Conflation of null distribution quantiles with effect CI fixed. |
| **k-NN Micro-Stratification** | $2.53\times$ to $2.75\times$ ($p = 0.000999$) | $2.53\times$ to $2.75\times$ ($p = 0.000999$) | **Verified & Validated**: 95% Monte Carlo CI: $[2.49\times, 2.79\times]$. Mean degree variance $< 1.5$. |
| **Continuous MCMC Sampler** | $1.20\times$ excess (+20.4%) ($Z = +2.80, p = 0.01587$) | **Methodologically Invalid** (Stationary distribution is Uniform) | **Withdrawn from Claims**: Proven symmetric transition kernel; reported 1.20x was transient slow-mixing artifact. |
| **Columnar–Tangential Ratio** | 99.46% (551 / 554) | 99.46% (551 / 554) | **Verified**: 551 Col–Tan, 3 Tan–Tan, 0 Col–Col. |
| **Directional Polarity** | 100% (Col=ACh, Tan=GABA) | 100.00% (551 / 551 dyads) | **Verified**: Zero reverse dyads ($Col_{\text{GABA}} \leftrightarrow Tan_{\text{ACh}}$). |
| **Layer 4 & 5 Clustering** | 99.10% (549 / 554 dyads) | 99.10% (549 / 554 dyads); $OR = 215.60, p = 3.36 \times 10^{-226}$ | **Verified & Validated**: Fisher's exact test confirms astronomical enrichment over neuropil baseline ($40.40\%$). |
| **Top Microcircuit Pairs** | `FB4A <-> vDeltaA` (150), `FB5A <-> FC2` (272) | Confirmed: 150 and 272 dyads | **Verified**: Recomputed from single-cell annotation mapping. |
| **Dynamical Model Gain** | "9.72x divisive gain suppression" | "9.72x subtractive inhibitory attenuation" | **Corrected**: Rate equation implements subtractive threshold-linear feedback, not divisive normalization. |
| **Dynamical Steering Decoding** | "< 0.8° steering decoding error" | Artifact of noiseless circular symmetry | **Corrected**: True error under 20% sensory noise is $5.65^\circ$. |
| **Confidence Sensitivity Ceiling** | Undocumented drop to 0 dyads at $\ge 0.80$ | Tangential GABA max confidence = 0.7873 | **Audited & Explained**: Eckstein et al. (2024) predictions ceiling for tangential neurons is 0.7873. |

---

## 3. Discovered Failures & Remediation Summary

1. **Failure 1: MCMC Detailed Balance Violation**:
   - *Discovery*: Proposal $q(X' \mid X)$ and acceptance $\alpha = \exp(-\|d_u - d_v\|^2 / 2\sigma^2)$ are symmetric across permutations: $T(X \to X') = T(X' \to X)$.
   - *Impact*: Stationary distribution is unconstrained uniform permutation.
   - *Remediation*: Formal withdrawal from primary claims; complete mathematical proof and numerical diagnosis documented in `docs/SCIENTIFIC_AUDIT.md` and `scripts/audit_and_diagnose_mcmc.py`.

2. **Failure 2: Mislabeling Divisive Gain Control**:
   - *Discovery*: Model subtracts $W_{\text{inh}} r_{\text{tan}}$ inside rectification brackets, generating linear response curves rather than hyperbolic divisive saturation.
   - *Impact*: Inaccurate biological interpretation.
   - *Remediation*: Reclassified as linear subtractive inhibitory attenuation and rate bounding; Figure 5 updated.

3. **Failure 3: Trivial Angular Decoding Precision**:
   - *Discovery*: Perfectly symmetric inputs and lateral weights mathematically forced decoded angle to target angle in noiseless conditions.
   - *Impact*: False claim of sensory decoding precision.
   - *Remediation*: Tested with Gaussian sensory noise; disclosed that error increases to $5.65^\circ$ under 20% noise.

4. **Failure 4: Conflating Null Quantiles and Failure of Naive Dyad Bootstrap**:
   - *Discovery*: Null simulation ranges like $[48, 157]$ were initially called "95% Empirical Confidence Intervals" for an observed count of 554. Subsequently, a naive dyad-level bootstrap was proposed, but audit revealed that all 554 ACh–GABA dyads are formed by just 16 GABAergic tangential neurons (34.6 dyads per neuron), violating dyad independence and underestimating variance. Synthetic coverage simulation proved naive bootstrap achieves only 55.6% coverage (7.2-fold variance underestimation). Furthermore, biological variance across flies cannot be identified from $N=1$.
   - *Impact*: Methodological error in statistical reporting and false certainty.
   - *Remediation*: Relabeled null ranges to "95% Null Simulation Range", formally withdrew naive dyad bootstrap CIs, and reported exact Monte Carlo simulation precision bounds ($\text{SE}_{\text{MC}} \le 0.04\times$).

5. **Failure 5: Test Suite Divergence from Implementation**:
   - *Discovery*: `test_scientific_rigor.py` promised synthetic controls in its docstring but had no test code; legacy tests still claimed MCMC preserves significance.
   - *Impact*: Test suite did not verify what was claimed and preserved outdated assertions.
   - *Remediation*: Implemented `TestSyntheticControls`, `TestConfidenceSensitivityAndFloor`, and `TestPublicationFigureArtifacts`, expanding test suite to 40 passing tests.

6. **Failure 6: Tangential Neuron Confidence Ceiling**:
   - *Discovery*: Naive global filtering at `conf >= 0.80` eradicated all ACh–GABA dyads.
   - *Impact*: Risk of false-negative dismissal of real microcircuits.
   - *Remediation*: Uncovered that tangential GABA neurons in FB have a maximum predicted confidence of 0.7873; documented the ultrastructural morphology reasons.

7. **Failure 7: MCMC Stationary Baseline Conflation**:
   - *Discovery*: Prior audit asserted the MCMC chain converged to "unconditioned null mean ~94", conflating it with the Model 1 coarse quartile mean (93.6). Under uniform permutation, the theoretical expectation is analytically $E[T] = M \frac{2 N_{\text{ach}} N_{\text{gaba}}}{N(N-1)} = 393.78$ dyads.
   - *Impact*: Incorrect theoretical baseline in text and Figure 4 Panel B.
   - *Remediation*: Corrected theoretical stationary mean to 393.78 dyads across scripts, test suite (`test_theoretical_uniform_stationary_expectation`), and Figure 4.

8. **Failure 8: Literature & DOI Verification Defects**:
   - *Discovery*: *Turner-Evans et al. (2020)* was cited in *Nature* under DOI `10.1038/s41586-020-2720-6` (HTTP 404). Real paper is in *Neuron*, DOI `10.1016/j.neuron.2020.08.006`. *Lin et al. (2024)* was edited to suffix `-0` (`10.1038/s41586-024-07968-0`, HTTP 404), whereas the valid Nature DOI is `10.1038/s41586-024-07968-y` (HTTP 200).
   - *Impact*: Broken citations and failed URL verification in publication manuscripts.
   - *Remediation*: Verified all DOIs via HTTP requests and corrected citations across all documentation.

---

## 4. Outstanding Validation Tasks (Future Work)

1. **Cross-Specimen Connectome Replication**:
   Requires independent processing of the Janelia hemibrain and upcoming male FAFB connectomes to verify that Layer 4 & 5 ACh–GABA clustering replicates across sexes and specimens.
2. **Biophysical Multi-Compartment Conductance Modeling**:
   Requires replacing the rate model with conductance-based simulations in NEURON or Brian2 to evaluate $Rdl$ vs $GABA_B$ kinetics.
3. **Optogenetic Functional Testing**:
   Requires in vivo patch-clamp recordings during cell-type specific optogenetic activation to measure actual physiological postsynaptic potentials.
