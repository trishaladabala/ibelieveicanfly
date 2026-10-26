# VectorWing: Technical Interview & Defense Guide

**Target Audience**: Computational Neuroscience, Connectomics, and Network Biology Interviewers (PhD / Master's Committee, Potential Supervisors)  
**Author**: Antigravity Research System  
**Date**: October 26, 2026  

---

## 1. Fast Spoken Pitches

### 60-Second Elevator Pitch
> *"In insect navigation, the brain coordinates two distinct spatial coordinate systems: a 1D heading compass in the Ellipsoid Body (EB) and a 2D vector steering matrix in the Fan-Shaped Body (FB). While the 1D compass is known to rely on homotypic recurrent inhibition between ring neurons to stabilize a heading bump, how the 2D vector steering circuit is reciprocally wired was functionally unresolved.
>
> Using the adult female FlyWire connectome (FAFB v783, 16.8M connection records), I investigated all 5,435 mutual dyads in the Fan-Shaped Body. By implementing degree-stratified conditional null models that hold physical reciprocity strictly invariant, I discovered a striking architectural inversion: homotypic recurrent inhibition is virtually absent (0.11%), replaced by a massive 5.7x to 5.9x enrichment of heterotypic excitatory-inhibitory (ACh–GABA) reciprocal loops. When degree variation is constrained to near-zero under continuous k-nearest-neighbor micro-stratification (k=8, 308 strata), an irreducible 2.5x biological excess persists (p < 0.001).
>
> Single-cell annotation mapping revealed that 99.5% of these loops connect columnar neurons to tangential neurons with 100% strict chemical polarity—columnar neurons are always cholinergic and tangential neurons are always GABAergic. Furthermore, 99.1% of these reciprocal loops are concentrated in premotor Layers 4 and 5. Rate-based dynamical modeling shows that this recurrent inhibition provides linear subtractive attenuation, preventing runaway excitation in recurrent columnar channels. This establishes an anatomical and computational foundation for how inhibitory state signals gate columnar vector steering."*

---

### Five-Minute Technical Deep Dive

1. **Motivation & Biological Question**:
   The central complex of *Drosophila* must solve vector navigation: tracking an internal compass heading while steering toward arbitrary goals in 2D space. The Ellipsoid Body (`EB`) implements a classic 1D continuous-attractor network (ring attractor) where homotypic GABAergic recurrent inhibition between ring neurons isolates an excitatory compass bump. We hypothesized that the Fan-Shaped Body (`FB`), with 16 columnar channels across 9 horizontal layers, requires a fundamentally different wiring logic to support vector arithmetic and state-dependent steering.

2. **Connectome Data Ingestion & Filtering**:
   We streamed the official FlyWire FAFB v783 connectome using PyArrow IPC, scanning 16,847,997 connection records. We filtered for intrinsic Fan-Shaped Body connections at a synapse weight threshold $w \ge 5$ (primary) with strict autapse exclusion ($pre \neq post$). Consensus neurotransmitter identities were computed across 138,005 whole-brain neurons by weighting synapse counts by presynaptic vesicle classification probabilities (Eckstein et al., 2024). This identified $N = 2,465$ active FB neurons, $E = 46,903$ directed edges, and $M = 5,435$ mutual dyads ($R_{\text{edge}} = 23.18\%$).

3. **Statistical Engine & Controlled Null Models**:
   Standard edge-swapping (Maslov–Sneppen configuration models) destroys spatial clustering and collapses empirical reciprocity by $4.61\times$, which artificially inflates reciprocal motif enrichment. To solve this, we formulated a conditional label-permutation framework: the empirical reciprocal graph topology ($M = 5,435$) is held strictly invariant, while cell-level neurotransmitter labels are permuted exclusively within discrete and continuous degree strata.
   - Discrete degree models (mutual quartiles, joint in/out tertiles, joint medians, total quintiles) demonstrated a $4.96\times$ to $5.92\times$ enrichment of ACh–GABA mutual dyads ($554$ dyads, $Z = +15.3$ to $+17.7$, empirical $p = 0.000500$, Benjamini–Hochberg FDR $q < 0.003$).
   - Continuous degree $k$-NN micro-stratification ($k=16$ [154 strata] and $k=8$ [308 strata]) showed that when joint $(d_{\text{in}}, d_{\text{out}})$ variation within strata is restricted to near-zero (mean degree variance $< 1.5$), ACh–GABA retains an irreducible $2.53\times$ to $2.75\times$ enrichment (95% Bootstrap CI: $[2.34\times, 2.97\times]$, $Z > +6.1, p = 0.000999$).

4. **Cellular Anatomy & Layer Localization**:
   Mapping to FlyWire v2.1.0 annotations achieved $100.0\%$ coverage ($2,465 / 2,465$ nodes). We found:
   - $99.46\%$ ($551 / 554$) of ACh–GABA loops connect columnar and tangential neurons.
   - Directional chemical polarity is $100.00\%$ strict: Columnar is always ACh, Tangential is always GABA. Reverse polarity is $0.00\%$.
   - $99.10\%$ ($549 / 554$ dyads) reside in Layers 4 and 5 (Layer 5: 364 dyads, $65.7\%$; Layer 4: 185 dyads, $33.4\%$).
   - Dominant physical microcircuits: `FB4A <-> vDeltaA` ($150$ dyads), `FB5A <-> FC2` ($272$ dyads across `FC2C`, `FC2B`, `FC2A`), and `FB5I2 <-> vDeltaF` ($29$ dyads).

5. **Dynamical Rate Modeling & Stress-Testing**:
   We built a 16-column rate model simulating Layers 4 and 5. Recurrent inhibition from tangential fans provides linear subtractive attenuation, bounding columnar rates to $\le 30.6$ Hz (vs. 297.4 Hz runaway excitation when ablated) and stabilizing spatial tuning width ($90.0^\circ$ FWHM). Stress-testing revealed that if lateral excitation exceeds $J_{\text{col}} \ge 0.60$, the system diverges into supercritical instability. Furthermore, sub-degree angular decoding precision ($<0.8^\circ$) in the noiseless model was proved to be a mathematical consequence of circular symmetry; under 20% sensory noise, mean decoding error is $5.65^\circ$.

---

## 2. Hard Technical Interview Questions & Defensible Answers

### Q1: Why did you use conditional label permutations instead of standard degree-preserving edge swapping?
**Answer**:
"In network neuroscience, standard Maslov–Sneppen edge-swapping algorithms preserve in- and out-degree sequences, but they rewire edges uniformly at random across the node universe. In dense spatial neuropils, physical proximity and neuropil boundary constraints create high natural reciprocity. When you rewire edges globally, reciprocity collapses—in our earlier whole-brain benchmarks, edge swapping reduced empirical reciprocity by over $4.6\times$. As a result, any calculation of motif excess under edge swapping conflates physical reciprocity (which is an anatomical property of spatial neuropils) with chemical pairing preference.
By fixing the empirical mutual dyad graph invariant ($M = 5,435$ constant) and permuting only whole-neuron chemical identities within degree strata, we condition on the exact reciprocal topology. This isolates the pure statistical question: *Given that two neurons form a physical reciprocal loop, do they pair heterotypically (ACh–GABA) more often than expected from their degree characteristics?*"

---

### Q2: What was the flaw in your original MCMC sampler, and why did you withdraw it?
**Answer**:
"The original implementation in `run_continuous_degree_model.py` proposed swapping labels between two discordant nodes $u$ and $v$ with acceptance probability:
$$\alpha(u, v) = \exp\left(-\frac{\|\mathbf{d}_u - \mathbf{d}_v\|^2}{2\sigma_d^2}\right)$$
During our forensic audit, we analyzed the detailed balance condition. Notice that $\mathbf{d}_u$ and $\mathbf{d}_v$ are fixed degree coordinates of nodes $u$ and $v$; they do not depend on the label assignment state $X$ or the proposed state $X'$.
Because the proposal mechanism is symmetric ($q(X' \mid X) = q(X \mid X')$) and the acceptance rule depends only on the distance between the two chosen nodes, the reverse transition $X' \to X$ evaluates the exact same distance $\|\mathbf{d}_u - \mathbf{d}_v\|$. Thus, $\alpha(X' \to X) = \alpha(X \to X')$, and the transition kernel $T(X \to X') = T(X' \to X)$ is symmetric (doubly stochastic).
Any symmetric, irreducible Markov transition matrix has the **uniform distribution over all permutations as its unique stationary distribution** ($\pi(X) = 1/|\Omega|$).
The degree penalty did not condition the stationary distribution on degree at all; it merely acted as a kinetic friction factor that severely retarded mixing. Because the sampler was initialized at the empirical state ($obs = 554$), taking 1,000 samples over 1.55M steps with a 93.3% rejection rate simply recorded the transient trajectory of a chain slowly diffusing toward the unconditioned null mean (~94).
When we tested this by initializing the chain from a random permutation, the sample mean remained at ~380–400, proving that the reported 1.20x number was an artifact of incomplete burn-in. We formally withdrew the MCMC claim from the paper's scientific defense."

---

### Q3: Why does the enrichment ratio drop from ~5.7x under coarse stratification to ~2.5x under k-NN micro-stratification?
**Answer**:
"In coarse stratification (such as quartiles or tertiles), wide degree bins contain substantial residual degree variation. Because cholinergic columnar neurons and GABAergic tangential neurons occupy distinct parts of the $(d_{\text{in}}, d_{\text{out}})$ degree distribution, coarse binning allows labels to be swapped between neurons that differ moderately in their connectivity profiles.
When we apply fine-grained greedy $k$-NN micro-stratification ($k=8$, creating 308 tight strata), neurons can only swap labels with neighbors that have almost identical normalized in- and out-degrees (within-stratum degree variance $< 1.5$). Because degree-matched nodes already share high connectivity, the null expectation rises from $97.4 \pm 28.1$ to $219.1 \pm 54.1$.
Crucially, however, the observed count of 554 is still **2.53 times higher than the degree-matched null expectation of 219 ($Z = +6.19, p = 0.000999$, 95% Bootstrap CI: $[2.34\times, 2.73\times]$)**. This shows that approximately half of the raw 5.7x excess reflects degree characteristics, but an irreducible 2.5-fold biological enrichment remains that cannot be explained by degree confounding."

---

### Q4: You claim '100% directional polarity'—all 551 columnar-tangential loops have Columnar=ACh and Tangential=GABA. Could this be an artifact of cell-type level predictions?
**Answer**:
"The neurotransmitter predictions from Eckstein et al. (Cell 2024) were trained on individual presynaptic T-bar EM images, not on cell-type labels. However, in our pipeline, we aggregated whole-brain synapse predictions to produce a single consensus label per neuron.
When we inspected the underlying cell types, we found:
1. Columnar neurons in these loops belong predominantly to vertical columnar interneurons (`vDeltaA`, 281/312 ACh) and columnar outputs (`FC2C`, 36/38 ACh), which are consistently predicted as cholinergic.
2. Tangential partners belong to `FB5A` (4/4 GABA) and `FB4A` (where 6 neurons with extensive columnar arborizations are GABAergic).
Importantly, within cell classes that have mixed predictions (e.g. `FB4A` contains 25 glutamatergic, 6 GABAergic, and 3 serotonergic neurons), the reciprocal dyads that pair with cholinergic `vDeltaA` are formed disproportionately by the GABAergic individuals.
We tested confidence sensitivity: when requiring prediction confidence $\ge 0.70$, 57 dyads remain (dominated by `FB5A <-> FC2`, where `FB5A` has confidence 0.784), confirming that the signal is not driven by ambiguous predictions."

---

### Q5: Is your rate model implementing divisive normalization or subtractive inhibition?
**Answer**:
"It implements linear subtractive feedback inhibition. The differential equation is:
$$\tau_{\text{col}} \frac{dr_{\text{col}, i}}{dt} = -r_{\text{col}, i} + \left[ I_i(\theta) + \sum_j W_{\text{lat}, ij} r_{\text{col}, j} - W_{\text{inh}} r_{\text{tan}} \right]_+$$
The term $- W_{\text{inh}} r_{\text{tan}}$ is subtracted linearly from the net input inside the rectification bracket.
In our stress tests, we plotted peak firing rate against input drive $I_0 \in [1, 30]$: the response scales linearly with drive (constant slope $\approx 1.53$ Hz/unit drive under $W_{\text{inh}} = 0.85$, vs. $14.87$ Hz/unit drive under $W_{\text{inh}} = 0$). True divisive normalization (e.g. Heeger/Carandini models) requires dividing the excitation by a normalizing term ($\frac{I}{\sigma + \sum I}$), producing saturating hyperbolic gain curves.
Therefore, calling this 'divisive gain control' was a misnomer in the original report. It is more accurately described as **recurrent subtractive inhibitory feedback that scales the effective slope and bounds peak firing rates**, preventing runaway excitation in recurrent columnar loops."

---

### Q6: Why did you get < 0.8° directional steering decoding error in your dynamical simulation?
**Answer**:
"In the original simulation, the sensory input was a noiseless cosine: $I_i = I_0 \cdot \max(0, \cos(\theta_{\text{target}} - \phi_i))$. The lateral recurrent connectivity was a noiseless symmetric cosine: $J_{\text{col}} \cos(\phi_i - \phi_j)$. And tangential inhibition pooled activity uniformly across all 16 columns: $r_{\text{tan}} \propto \sum r_i$.
Because every component of the differential equations was perfectly symmetric about $\theta_{\text{target}}$, the population vector centroid $\text{atan2}(v_y, v_x)$ is mathematically guaranteed by circular symmetry to equal $\theta_{\text{target}}$, up to the spatial discretization of the 16 columns.
When we added Gaussian sensory noise to column inputs, we found that under 10% noise, decoding error increases to $2.38^\circ$, and under 20% noise, it increases to $5.65^\circ$. Sub-degree precision was a mathematical consequence of noise-free circular symmetry, not an empirical proof of sensory decoding fidelity in a noisy biological brain."

---

### Q7: What is the primary biological difference between the Ellipsoid Body and Fan-Shaped Body?
**Answer**:
"The architectural dichotomy reflects their different computational roles:
1. **Ellipsoid Body (1D Heading Compass)**:
   - Needs to maintain a single, compact activity bump representing azimuth that persists even in darkness.
   - Reciprocity is dominated by **homotypic recurrent inhibition** ($88.2\%$ of GABA–GABA dyads connect ring neurons to ring neurons).
   - Cross-talk between excitatory compass neurons and inhibitory ring neurons ($ACh \leftrightarrow GABA$) is heavily suppressed ($0.27\times$, $Z = -23.2$), isolating the compass channel from premature feedback.
2. **Fan-Shaped Body (2D Vector Steering Matrix)**:
   - Needs to compute 2D vector shifts, translate coordinate frames, and route motor goals.
   - Homotypic GABA recurrence is virtually absent ($6$ dyads, $0.11\%$).
   - Instead, the network exhibits an intense enrichment of **heterotypic excitatory-inhibitory feedback ($ACh \leftrightarrow GABA$)**, concentrated at $99.1\%$ in premotor Layers 4 and 5 where columnar steering outputs (`vDelta`, `FC2`) interact reciprocally with inhibitory tangential fans (`FB4A`, `FB5A`)."

---

### Q8: What would be your next scientific step if given funding or an internship in my lab?
**Answer**:
"Three concrete next steps:
1. **Cross-Specimen and Cross-Sex Replication**: Replicate the Layer 4 & 5 ACh–GABA concentration in the Janelia hemibrain connectome and upcoming male FAFB reconstructions to test for sexual dimorphism or individual developmental variability.
2. **Biophysical Conductance Modeling**: Extend our rate model into a multi-compartmental NEURON or Brian2 simulation incorporating ionotropic $Rdl$ ($GABA_A$) vs metabotropic $GABA_B$ receptor kinetics, testing whether slow vs fast inhibition provides dynamic gain modulation.
3. **Optogenetic Functional Validation**: Collaborate with an experimental lab to perform patch-clamp electrophysiology from `vDeltaA` or `FC2` neurons during optogenetic stimulation of `FB4A`/`FB5A` tangential neurons, testing whether physical synaptic dyads produce bidirectional physiological conductances in vivo."
