# Comprehensive Scientific & Methodological Audit: VectorWing Connectomics

**Target Project**: VectorWing: Layer-Resolved Columnar-Tangential Reciprocity and Chemospecific Feedback in the Adult *Drosophila* Fan-Shaped Body Connectome  
**Auditor**: Senior Computational Neuroscientist, Research Statistician & Scientific Software Engineer  
**Date**: October 26, 2026  
**Primary Dataset**: Adult female *Drosophila melanogaster* whole-brain connectome (FlyWire FAFB v783; Zenodo DOI: `10.5281/zenodo.10676866`), annotations v2.1.0 (Schlegel et al., 2024; DOI: `10.1038/s41586-024-07686-5`), neurotransmitter predictions (Eckstein et al., 2024; DOI: `10.1016/j.cell.2024.03.016`).  
**Baseline Directory**: `/home/trishal/ibelieveicanfly/fb_vector_reciprocity/`  

---

## 1. Executive Summary of Forensic Findings

A forensic audit of the VectorWing codebase, statistical methodology, numerical claims, and scientific interpretations was conducted. The core empirical graph extraction and cellular anatomy findings are sound and reproducible. However, critical methodological flaws were uncovered in the statistical claims, MCMC sampling mechanics, and dynamical model interpretation:

1. **Fatal Methodological Flaw in Continuous MCMC Null Model**:
   - The reported Metropolis–Hastings label-swapping sampler with acceptance probability $\alpha(u, v) = \exp(-\|d_u - d_v\|^2 / 2\sigma_d^2)$ has symmetric proposal and acceptance probabilities: $T(X \to X') = T(X' \to X)$.
   - Consequently, its unique stationary distribution is the **uniform distribution over all permutations**, containing **zero degree-conditioning**.
   - The reported $1.20\times$ (+20.4%) residual excess is entirely an artifact of slow mixing (incomplete diffusion away from the empirical initial state $obs=554$) after 1.55M steps with a 93.3% proposal rejection rate.
   - **Correction**: This sampler does not sample a degree-conditioned target distribution. It must be formally classified as methodologically invalid and removed from the primary scientific defense of degree-independence.

2. **Mischaracterization of Dynamical Model as "Divisive Gain Control"**:
   - The 16-column rate model implements linear **subtractive feedback inhibition** ($\max(0, I + \text{lat} - W_{\text{inh}} r_{\text{tan}})$), **not divisive normalization** (which requires division by total activity, e.g., $I / (\sigma + \sum I)$).
   - The reported directional decoding error ($< 0.8^\circ$) is mathematically trivial due to circular symmetry in the cosine tuning curve, cosine lateral weights, and uniform tangential pooling.
   - **Correction**: Reclassify the dynamical simulation as an exploratory proof-of-concept demonstrating that recurrent inhibitory feedback prevents runaway excitation in a recurrent columnar network, but withdraw claims of having proven biological divisive normalization or decoding fidelity.

3. **Mislabeling of Null Simulation Ranges as Effect-Size Confidence Intervals**:
   - The report repeatedly labels the central 95% quantile range of randomized null statistics (e.g., $[48, 157]$) as a "95% Empirical Confidence Interval".
   - **Correction**: That range is the central 95% quantile of the null distribution under $H_0$, indicating what counts are expected by chance under the null hypothesis. It is NOT a confidence interval for the biological enrichment ratio or effect size.

4. **Validated Strong Empirical Findings**:
   - At threshold $w \ge 5$, the FB connectome comprises $N = 2,465$ active neurons, $E = 46,903$ directed edges, and $M = 5,435$ mutual dyads ($R_{\text{edge}} = 23.18\%$).
   - Heterotypic ACh–GABA reciprocity ($554$ dyads, $10.19\%$ of all mutual dyads) is enriched $5.45\times$ to $5.92\times$ under degree-stratified null models (quartiles, tertiles, quintiles; $p = 0.000500$, Benjamini–Hochberg FDR $q < 0.003$).
   - Under fine-grained greedy $k$-NN micro-stratification ($k=16$ [154 strata] and $k=8$ [308 strata]), enrichment remains substantial at $2.53\times$ to $2.75\times$ ($p = 0.000999$).
   - Single-cell FlyWire v2.1.0 annotation mapping confirms that $99.46\%$ ($551 / 554$) of ACh–GABA mutual dyads connect Columnar and Tangential neurons.
   - Directional chemical polarity is $100.00\%$ strict: all 551 are $Columnar_{\text{ACh}} \leftrightarrow Tangential_{\text{GABA}}$, with $0$ reverse dyads.
   - Spatial localization is extremely clustered: $99.10\%$ ($549 / 554$) of ACh–GABA loops reside in Layers 4 and 5 (Layer 5: 364 dyads, $65.70\%$; Layer 4: 185 dyads, $33.39\%$).

---

## 2. Systematic Forensic Classification of All Claims

| Claim ID | Claim Description | Status | Evidence & Forensic Analysis |
|---|---|---|---|
| **C1** | $N=2,465$ active FB neurons, $E=46,903$ directed edges, $M=5,435$ mutual dyads, $S=598,942$ synapses at $w \ge 5$. | **Verified by direct recomputation** | Extracted from `proofread_connections_783.feather` with zero discrepancies. Edge reciprocity $R_{\text{edge}} = 2M/E = 23.18\%$, dyad reciprocity $R_{\text{dyad}} = M/(E-M) = 13.11\%$. |
| **C2** | Autapse exclusion ($pre \neq post$) and duplicate edge merging. | **Verified by direct recomputation** | Checked across all 46,903 directed edges and 5,435 mutual dyads; zero self-loops exist. Endpoints are strictly canonically ordered ($u < v$) for dyads. |
| **C3** | 64-bit root ID precision without floating-point truncation. | **Verified by direct recomputation** | All active root IDs are 64-bit integers $> 7.2 \times 10^{17}$, safely exceeding standard JavaScript / IEEE-754 double-precision safe integer limit ($2^{53} - 1$). |
| **C4** | Whole-brain consensus neurotransmitter assignment and confidence scores. | **Reproduced but qualified** | Weighted consensus from 16.8M synapses accurately reproduces assignments. Caveat: assignments are deep-learning predictions (Eckstein et al., 2024), not direct physiological measurements. |
| **C5** | 554 mutual dyads are ACh <-> GABA ($10.19\%$ of total $M$). | **Verified by direct recomputation** | Recomputed directly from cached covariates and consensus assignments. Homotypic GABA-GABA is nearly absent ($6$ dyads, $0.11\%$). |
| **C6** | 5.45x–5.92x enrichment under degree-stratified null models (Models 1–4). | **Verified by direct recomputation** | 2,000 permutations per model confirm $Z = +15.3$ to $+17.7$, empirical $p = 0.000500$, FDR $q < 0.003$. Quantile ranges correctly reproduce. |
| **C7** | "95% Empirical Confidence Interval" in Table 5.2. | **Methodologically invalid as described** | The report conflates the 95% null simulation interval under $H_0$ with a confidence interval for the true effect size. Must be relabeled as "95% Null Expectation Interval". |
| **C8** | Continuous degree k-NN micro-stratification (154 and 308 strata). | **Plausible but qualified** | Shows $2.75\times$ ($k=16$) and $2.53\times$ ($k=8$) enrichment. Caveat: greedy clustering has arbitrary tie-breaking; at $k=8$, numerous micro-strata become label-homogeneous ("frozen"), reducing permutable entropy. |
| **C9** | Continuous Metropolis–Hastings MCMC sampler ($\sigma_d = 0.20$). | **Methodologically invalid as currently implemented** | Proposal and acceptance are symmetric with respect to label states: $T(X \to X') = T(X' \to X)$. Stationary distribution is uniform over all permutations. 1.20x excess is a mixing failure artifact. |
| **C10** | 100% FlyWire v2.1.0 annotation coverage ($2,465 / 2,465$). | **Verified by direct recomputation** | Confirmed by streaming `Supplemental_file1_neuron_annotations.tsv`. 193 unmapped nodes properly rescued via `cell_type` (`CB.FB...`). |
| **C11** | 99.46% (551 / 554) Columnar–Tangential pairing for ACh–GABA dyads. | **Verified by direct recomputation** | Broad morphological categorization strictly confirms $551$ dyads connect columnar and tangential neurons, with 3 tangential–tangential and 0 columnar–columnar. |
| **C12** | 100.00% strict directional chemical polarity (Col=ACh, Tan=GABA). | **Verified by direct recomputation** | Confirmed: all 551 columnar–tangential dyads have Columnar=ACh and Tangential=GABA. Zero dyads exhibit reverse polarity ($Columnar_{\text{GABA}} \leftrightarrow Tangential_{\text{ACh}}$). |
| **C13** | 99.10% (549 / 554) localized in Layers 4 & 5. | **Verified by direct recomputation** | Confirmed: Layer 5 has 364 dyads ($65.70\%$), Layer 4 has 185 dyads ($33.39\%$), combined 549 dyads ($99.10\%$). Unassigned dyads drop to 3 ($0.54\%$). |
| **C14** | Top cell-type pairings: `FB4A <-> vDeltaA` (150), `FB5A <-> FC2` (272), `FB5I2 <-> vDeltaF` (29). | **Verified by direct recomputation** | Confirmed across all 554 dyads. |
| **C15** | Rate-based model: "9.72x divisive gain suppression". | **Methodologically flawed / Misinterpreted** | The model implements linear subtractive inhibition, not divisive normalization. Firing rate attenuation is subtractive thresholding. |
| **C16** | Rate-based model: "< 0.8° directional steering decoding error". | **Artifact of circular symmetry** | Circular cosine input + circular cosine lateral connections + uniform global inhibition guarantees symmetry-preserving bump centroids. Does not prove decoding fidelity under biological noise. |
| **C17** | Contrast between EB (1D Ring Attractor) and FB (2D Steering Matrix). | **Plausible scientific hypothesis** | Supported by the dramatic difference in homotypic GABA recurrence (EB: 74.3% vs FB: 0.11%) and heterotypic reciprocity (EB: depleted 0.27x vs FB: enriched 5.7x). Must be framed as an anatomical hypothesis, not established in vivo fact. |

---

## 3. Discrepancies and Inconsistencies Discovered

1. **Terminology Conflation (Null Distribution Quantile vs Effect CI)**:
   - In `PROJECT_REPORT.md` Section 5.2, column 6 is labeled `95% Empirical CI` with values like `[48, 157]`.
   - The observed count is 554, which lies entirely outside this interval!
   - This interval is the 2.5th to 97.5th percentile of the *null distribution*, not a confidence interval for the observed count or the enrichment ratio.

2. **The MCMC Fallacy**:
   - In `PROJECT_REPORT.md` Section 5.3 and `README.md`, the MCMC procedure was presented as an independent validation proving that the motif survives continuous degree penalties.
   - In reality, the sampler does not target a probability distribution penalized by degree distance; it merely retards swap transitions between degree-distant nodes while preserving symmetric transition rates between permutations.
   - Its stationary distribution is unconstrained uniform permutation.

3. **Rate Model Parameter Equivalence**:
   - The report implies that synaptic weights and coupling parameters ($W_{\text{recip}} = 0.15, W_{\text{inh}} = 0.85, J_{\text{col}} = 0.25$) are empirically derived biophysical quantities.
   - In fact, they are arbitrary dimensionless coefficients chosen to obtain convenient rate ranges in an illustrative ODE.

---

## 4. Remediation Plan

1. **Statistical Framework**:
   - Formally withdraw the continuous degree MCMC sampler from the primary claims. Document its mathematical derivation and failure in the audit report.
   - Clarify the difference between null distribution quantiles and effect-size confidence intervals.
   - Retain the discrete degree-stratified models (Models 1–4) and the fine-grained $k$-NN micro-stratification ($k=16, k=8$) as the valid statistical evidence.
   - Compute bootstrap confidence intervals for the observed enrichment ratios across models.

2. **Dynamical Modeling**:
   - Correct the mathematical description: replace "divisive gain control" with "recurrent subtractive inhibitory feedback".
   - State clearly that the angular decoding precision is a mathematical consequence of circular symmetry in the noise-free simulation, not an empirical discovery of fly neurophysiology.
   - Reframe the model as an exploratory rate-based proof-of-concept illustrating how reciprocal inhibitory feedback prevents runaway excitation.

3. **Software & Test Suite**:
   - Add real algorithmic unit tests for:
     * Graph construction, dyad counting, and degree sum invariants.
     * Correct empirical p-value computation ($p = (b + 1) / (B + 1)$).
     * Benjamini-Hochberg monotonicity and edge cases.
     * Synthetic network recovery where ground-truth transmitter association is known.
     * MCMC symmetry proof and failure diagnosis.
     * Rate model numerical stability and parameter sensitivity.
   - Replace tests that merely assert precomputed JSON values with tests of actual computation.

4. **Documentation & Reporting**:
   - Update `PROJECT_REPORT.md` to be an honest, rigorous, scientifically defensible manuscript.
   - Deliver `docs/PROJECT_OVERVIEW.md`, `docs/INTERVIEW_GUIDE.md`, `docs/RESEARCH_DECISIONS.md`, and `docs/VALIDATION_REPORT.md`.
