# VectorWing: Project Overview

**Title**: Layer-Resolved Columnar-Tangential Reciprocity and Chemospecific Feedback in the Adult *Drosophila* Fan-Shaped Body Connectome  
**Audience**: Computational Neuroscientists, Connectomics Researchers, Graduate Admissions Committees (PhD / Master's)  
**Reading Time**: ~2 minutes  

---

## 1. The Biological Question

In the insect central complex, navigation requires coordinating two distinct geometric systems:
1. **1D Heading Compass** in the Ellipsoid Body (`EB`), which maintains an internal representation of azimuth.
2. **2D Vector Steering Matrix** in the Fan-Shaped Body (`FB`), which integrates heading, translational velocity, and goal cues to compute directed motor commands.

While the Ellipsoid Body has been extensively characterized as a ring attractor dominated by **homotypic recurrent inhibition** among GABAergic ring neurons ($88.2\%$ of mutual dyads), the topological reciprocity and chemical pairing logic of the Fan-Shaped Body was functionally unresolved:
*Does the 2D vector steering matrix share the homotypic recurrent architecture of the 1D compass, or does it utilize a fundamentally different wiring logic to support vector computation?*

---

## 2. Dataset and Provenance

- **Connectome Release**: Whole-brain FlyWire FAFB v783.0 (Zenodo DOI: `10.5281/zenodo.10676866`), containing 16.8M proofread synaptic connection records from an adult female *Drosophila melanogaster*.
- **Cellular Annotations**: Official version-pinned FlyWire v2.1.0 annotations (Schlegel et al., 2024; *Nature*, DOI: `10.1038/s41586-024-07686-5`).
- **Neurotransmitter Predictions**: Consensus whole-cell predictions derived from presynaptic EM T-bar morphology across 6 classes (ACh, GABA, Glutamate, Dopamine, Octopamine, Serotonin) trained by Eckstein et al. (2024; *Cell*, DOI: `10.1016/j.cell.2024.03.016`).

---

## 3. Computational Methodology

1. **Streaming Connectome Ingestion**:
   Direct Arrow RecordBatch streaming ingests 16,847,997 records, filtering for Fan-Shaped Body connections at synapse threshold $w \ge 5$ with strict autapse exclusion ($pre \neq post$).
2. **Topological Graph Extraction**:
   Extracts $N = 2,465$ active neurons, $E = 46,903$ directed edges, and $M = 5,435$ mutual dyads, establishing an edge reciprocity of $R_{\text{edge}} = 23.18\%$ (ranks #6 among 79 brain neuropils).
3. **Controlled Conditional Null Models**:
   Holds the empirical reciprocal topology ($M = 5,435$) strictly invariant while permuting cell-level transmitter identities within degree strata:
   - Coarse degree quantiles: mutual-degree quartiles, joint in $\times$ out tertiles, joint in $\times$ out medians, total-degree quintiles ($B = 2,000$ permutations each, seed = 42).
   - Fine-grained continuous degree $k$-NN micro-stratification: $k=16$ (154 strata) and $k=8$ (308 strata) in normalized in/out degree space.
4. **Cellular and Layer Decomposition**:
   Maps all 2,465 neurons with $100.0\%$ match coverage, decomposing dyads by morphological family (Columnar vs Tangential), directional transmitter polarity, horizontal layers (Layers 1 to 9), and specific cell types (`FB4A`, `FB5A`, `vDeltaA`, `FC2`).
5. **Rate-Based Dynamical Modeling**:
   Simulates a 16-column continuous-attractor network across behavioral drives ($I_0 \in [1, 20]$), evaluating intact vs ablated inhibitory feedback.

---

## 4. Primary Validated Findings

1. **Heterotypic Excitatory-Inhibitory Inversion**:
   Homotypic GABA–GABA reciprocity is virtually absent in the FB ($6$ dyads, $0.11\%$). Instead, the network is dominated by **heterotypic ACh $\leftrightarrow$ GABA reciprocal loops ($554$ dyads, $10.19\%$ of all mutual dyads)**.
2. **Resilience to Degree Conditioning**:
   - Under coarse degree null models, ACh–GABA exhibits **$4.96\times$ to $5.92\times$ enrichment** (95% Monte Carlo CI: $[4.90\times, 5.99\times]$, $Z = +15.3$ to $+17.7$, empirical $p = 0.000500$, Benjamini–Hochberg FDR $q < 0.003$).
   - Under fine-grained $k$-NN micro-stratification ($k=8$ and $k=16$), a **$2.53\times$ to $2.75\times$ enrichment** (95% Monte Carlo CI: $[2.49\times, 2.79\times]$, $Z > +6.1$, empirical $p = 0.000999$) persists. Degree matching attenuates enrichment from ~5.7x to 2.53x, confirming that the conditional association remains statistically significant under tight degree constraints.
3. **100% Polarized Columnar-Tangential Microcircuits**:
   - $99.46\%$ ($551 / 554$) of ACh–GABA loops connect columnar neurons to tangential neurons.
   - Directional chemical polarity is **$100.00\%$ strict**: every columnar partner is cholinergic (ACh, excitatory) and every tangential partner is GABAergic (GABA, inhibitory). Reverse polarity ($Col_{\text{GABA}} \leftrightarrow Tan_{\text{ACh}}$) is $0.00\%$.
4. **Premotor Layer 4 & 5 Clustering (99.10%)**:
   ACh–GABA feedback loops are not distributed across all 9 layers; **$99.10\%$ ($549 / 554$ dyads)** reside in Layers 4 and 5 (Layer 5: 364 dyads, $65.70\%$; Layer 4: 185 dyads, $33.39\%$).
   Dominant physical microcircuits: `FB4A <-> vDeltaA` ($150$ dyads), `FB5A <-> FC2` ($272$ dyads across `FC2C`, `FC2B`, `FC2A`), and `FB5I2 <-> vDeltaF` ($29$ dyads).
5. **Inhibitory Attenuation & Firing Rate Bounding**:
   Recurrent inhibitory feedback from tangential neurons provides linear subtractive attenuation, preventing runaway excitation in recurrent columnar loops ($30.6\text{ Hz}$ vs $297.4\text{ Hz}$ saturated when ablated) and stabilizing spatial tuning width ($90.0^\circ$ FWHM).

---

## 5. Main Scientific Limitations

1. **Audited MCMC Methodological Failure**:
   A previous degree-penalized MCMC swap sampler was shown to have symmetric transition probabilities $T(X \to X') = T(X' \to X)$, meaning its stationary distribution is uniform permutation (zero degree conditioning). Its reported 1.20x number was a transient mixing artifact and has been formally withdrawn.
2. **Single Female Specimen**:
   Derived from one female connectome (FAFB v783); requires verification in multi-specimen and male datasets.
3. **Predicted Transmitters**:
   Transmitter identities are machine-learning predictions from presynaptic vesicles, not patch-clamp electrophysiology.
4. **Subtractive Rate Model vs Divisive Normalization**:
   The dynamical simulation implements subtractive feedback, not divisive gain control. Steering precision ($<0.8^\circ$) is an artifact of noiseless circular symmetry.

---

## 6. Takeaway Message

The Fan-Shaped Body operates via an inverted architectural logic compared to the Ellipsoid Body: while 1D heading relies on homotypic recurrent inhibition to isolate a compass bump, 2D vector steering employs dense, layer-localized heterotypic feedback where inhibitory tangential state inputs cross-clamp excitatory columnar steering channels at the primary premotor output layers (Layers 4 and 5).
