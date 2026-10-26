# VectorWing Mission Log: Fan-Shaped Body Reciprocal Architecture and Vector Steering Connectomics

**Project**: VectorWing — Layer-Resolved Columnar-Tangential Reciprocity in the Adult *Drosophila* Fan-Shaped Body  
**Working Directory**: `/home/trishal/ibelieveicanfly/fb_vector_reciprocity`  
**Parent Workspace**: `/home/trishal/ibelieveicanfly`  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04.5 LTS)  
**Software Environment**: Python 3.12, PyArrow 26.0.0, Cairo (`.venv`)  
**Mission Started**: October 25, 2026  

---

## 1. Project Formulation & Objectives

### Background & Research Context
In earlier phases of the *Drosophila* connectomics pipeline (`ibelieveicanfly`, Phases 1–8), we rigorously resolved the reciprocity architecture of the Ellipsoid Body (`EB`), proving that:
1. Classical edge-swap configuration models suffer catastrophic reciprocity collapse ($4.61\times$), producing artificial motif ratios.
2. When evaluated under conditional degree-stratified label permutations, the EB exhibits a robust $+20.6\%$ to $+31.8\%$ excess of homotypic GABA–GABA mutual dyads, underpinned by all-to-all recurrence among ring neurons ($88.18\%$ of GABA–GABA dyads).
3. Reciprocal cross-transmitter communication between compass neurons and ring neurons ($ACh \leftrightarrow GABA$) is strongly suppressed ($0.27\times$).

### The Unexplored Opportunity: The Fan-Shaped Body (FB)
The Fan-Shaped Body (`FB`) is the central navigational matrix of the insect brain, computing 2D vector navigation, translating compass heading into body-centric steering angles, and integrating internal motivational states across 9 horizontal layers and 9 vertical columns.

In Phase 6 exploratory analyses, the FB showed a striking, completely inverted pattern compared to the EB:
- Homotypic GABA–GABA mutual dyads are virtually absent (only 6 out of 5,435 mutual dyads, $0.11\%$).
- Heterotypic $ACh \leftrightarrow GABA$ mutual dyads are massively enriched ($554$ dyads, $5.89\times$ enrichment, $Z = +17.76$, $p = 0.0005$, FDR $q = 0.0026$).

### Core Research Questions:
1. **Robustness & Null Sensitivity**: Does the $5.89\times$ $ACh \leftrightarrow GABA$ enrichment in the FB survive joint directed in/out degree stratification (tertiles and medians)?
2. **Continuous Degree Matching**: Does exact continuous degree-matched label permutation alter the enrichment?
3. **Anatomical Substrate**: Which exact cell types and morphological classes (columnar vs tangential) form these 554 reciprocal dyads?
4. **Layer-Specific Architecture**: How are reciprocal dyads partitioned across the 9 horizontal layers of the FB (FB1 to FB9)?
5. **Comparative Connectomics**: What are the fundamental topological and chemical design principles distinguishing 1D ring attractors (EB) from 2D vector navigation matrices (FB)?

---

## 2. Chronological Action Plan

- [x] Step 0: Problem formulation and mission log initialization.
- [x] Step 1: Subgraph extraction and caching (`scripts/extract_fb_subgraph.py` -> `data/fb_node_covariates.json`).
- [x] Step 2: Controlled null model evaluation across multiple strata specifications (`scripts/run_fb_controlled_study.py`).
- [x] Step 3: Exact continuous degree-matched label permutation model (`scripts/run_continuous_degree_model.py`).
- [x] Step 4: Single-cell annotation mapping, layer-column decomposition, and motif classification (`scripts/analyze_layer_column_anatomy.py`).
- [x] Step 5: Automated test suite verification (`tests/test_fb_vector_reciprocity.py`).
- [x] Step 6: Presentation-quality vector figures rendering (`scripts/generate_fb_figures.py`).
- [x] Step 7: Standalone interactive demonstration script (`demo.py`).
- [x] Step 8: Rate-based dynamical simulation of divisive gain control (`scripts/simulate_vector_steering_dynamics.py`).
- [x] Step 9: Comprehensive `PROJECT_REPORT.md` and repository `README.md`.
- [x] Step 10: Critical audit, bug fixes (cairo imports, cell_type extraction, MCMC sampler), and test expansion.

---

## 3. Critical Review, Bug Fixes & Scientific Enhancements

1. **Bug Fix — Cairo Virtualenv Isolation**:
   - `scripts/generate_fb_figures.py` failed under `.venv/bin/python3` due to missing system package path. Added `/usr/lib/python3/dist-packages` to `sys.path` prior to cairo import.

2. **Methodological Correction — Single-Cell Annotation Classification**:
   - `scripts/analyze_layer_column_anatomy.py` previously only checked `hemibrain_type` and ignored `cell_type`. This left 193 active FB neurons unclassified and misattributed 29 Layer 5 mutual dyads to `"Unknown <-> vDeltaF"` and `"Unassigned_Layer"`.
   - Updated `classify_morphology` to parse `cell_type` (e.g. `CB.FB5I2`) when `hemibrain_type` is blank.
   - Result: Layer 5 dyads increased from 335 (60.5%) to **364 (65.7%)**; combined Layers 4 & 5 concentration increased from 93.9% to **99.10% (549 / 554)**; unassigned dyads plummeted from 32 to **3 (0.54%)**; and `FB5I2 <-> vDeltaF` (29 dyads, 5.23%) was identified as the 6th largest specific microcircuit.

3. **Algorithm Implementation — Continuous Metropolis-Hastings MCMC Sampler**:
   - Implemented the degree-distance penalized MCMC sampler in `scripts/run_continuous_degree_model.py` with penalty factor $\sigma_d = 0.20$.
   - Confirmed persistence of the signal: FB ACh <-> GABA exhibits $1.20\times$ (+20.4%) excess ($Z = +2.80, p = 0.01587$), and EB GABA <-> GABA exhibits $1.60\times$ (+59.8%) excess ($Z = +5.92, p = 0.025$).

4. **New Scientific Feature — Rate-Based Dynamical Circuit Model**:
   - Implemented `scripts/simulate_vector_steering_dynamics.py` modeling the 16-column FB Layers 4 & 5 steering circuit under empirical reciprocal synaptic weights.
   - Demonstrated that reciprocal GABAergic feedback provides **$9.72\times$ divisive gain suppression**, clamping peak firing to $\le 30.6$ Hz and maintaining sharp directional tuning (FWHM = 90.0° vs 135.0° when ablated) across varying velocity/sensory drive levels ($I_0 \in [1, 20]$).
   - Rendered Figure 4 vector SVG and 300dpi PNG showcasing gain curves and spatial bump profiles.

5. **Test Suite Expansion**:
   - Expanded `tests/test_fb_vector_reciprocity.py` from 16 to 21 automated unit tests, validating 99.1% layer concentration, `FB5I2 <-> vDeltaF` microcircuit identification, and dynamical feedback invariants.

---

## 4. Forensic Audit, Rigorous Corrections & Scientific Defense (Phases 11–14)

1. **Withdrawal of MCMC Sampler as Degree-Conditioned Null Model**:
   - Proved mathematically that transition kernel $T(X \to X') = T(X' \to X)$ satisfies detailed balance for the uniform distribution over permutations.
   - Diagnosed reported 1.20x excess as a transient slow-mixing artifact from empirical initialization ($obs=554$) with 93.3% proposal rejection rate.
   - Formally withdrew MCMC sampler from scientific defense; established fine-grained continuous degree $k$-NN micro-stratification ($k=8, k=16$) as primary continuous degree control ($2.53\times$ excess, $p = 0.000999$).

2. **Dynamical Model Reclassification**:
   - Reclassified "divisive gain control" as linear subtractive feedback attenuation (slope scales from 14.87 to 1.53 Hz/unit drive; 9.72x rate reduction).
   - Qualified steering precision claims ($<0.8^\circ$ in noiseless simulation is an artifact of circular symmetry; rises to $5.65^\circ$ under 20% sensory noise).
   - Identified supercritical runaway instability boundary at $J_{\text{col}} \ge 0.60$.

3. **Tangential GABA Confidence Ceiling**:
   - Discovered that tangential GABA neurons in FB have a maximum predicted confidence ceiling of 0.7873 (median 0.7812) in Eckstein et al. (2024).
   - Proved that global confidence threshold $\ge 0.80$ excises all tangential neurons, dropping ACh–GABA dyads to 0, explaining the apparent sensitivity cliff.

4. **Synthetic Negative & Positive Controls**:
   - Implemented synthetic random and spiked control generators in `scripts/run_sensitivity_and_controls.py`.
   - Verified negative controls yield $1.04\times$ ($p = 0.43$) and positive spiked controls yield $1.61\times$ ($p = 0.001$).

5. **Publication Figure Suite & Rigorous Test Suite**:
   - Expanded programmatic Cairo renderer to 6 distinct figures (Figures 1–6) in vector SVG and 300dpi PNG.
   - Built `tests/test_scientific_rigor.py`, expanding the automated unit test suite to 37 passing tests across graph invariants, null models, synthetic controls, and dynamical stability.

