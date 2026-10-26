# Project Portfolio Summary: Adult *Drosophila* Connectomics Pipeline

**Project Title**: "I Believe I Can Fly" — Quantitative Analysis of Synaptic Reciprocity and Neurotransmitter Motifs in the Adult *Drosophila* Central Complex  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Author**: Computational Biology Research Team  
**Focus Area**: Computational Biology, Connectomics, Network Science  
**Status**: Portfolio Release Candidate  

---

## 1. One-Sentence Project Description

An audited computational connectomics pipeline evaluating synaptic reciprocity and reciprocal neurotransmitter motifs in the adult *Drosophila* central complex using the FlyWire FAFB v783 dataset and version-pinned cell-type annotations.

---

## 2. Executive Summary (Suitable for CV / Portfolio Website)

This project investigates the topological and neurochemical organization of synaptic feedback loops in the adult fruit fly (*Drosophila melanogaster*) brain. Working under strict memory and resource constraints on commodity laptop hardware, we developed an out-of-core, chunked streaming pipeline using Python and Apache Arrow to process the 13.4-million-connection FlyWire FAFB v783 connectome.

Our primary research focus was the Ellipsoid Body (`EB`), a toroidal neuropil in the central complex essential for visual navigation and spatial heading representation. When evaluating reciprocal synaptic connections between GABAergic neurons, classical degree-preserving edge-swap rewiring initially suggested a dramatic $\sim 6.78\times$ enrichment. However, an in-depth methodological audit revealed that edge swapping collapsed empirical edge reciprocity by $4.61\times$ (from $44.50\%$ to $9.66\%$), confounding physical reciprocity with chemical transmitter pairing. To resolve this, we designed a protected conditional label-permutation model that holds the empirical mutual dyad graph ($M = 3,518$) invariant while exchanging labels strictly within degree strata.

Under this controlled framework, a modest conditional excess of $+20.6\%$ to $+31.8\%$ GABA–GABA mutual dyads persisted across mutual-degree quartiles, directed in/out tertiles, and directed in/out medians ($Z > +13$, empirical $p = 0.000500$). By integrating version-pinned FlyWire v2.1.0 annotations, we traced this signal to its anatomical substrate: $88.18\%$ of all GABA–GABA mutual dyads are formed between ring neurons, with $77.48\%$ connecting neurons sharing the exact same reported ER base type (e.g., ER2–ER2, ER3d–ER3d). This project highlights the critical importance of decoupling network topology from label composition when analyzing biological connectomes.

---

## 3. The Scientific Question

Does the adult *Drosophila* central complex exhibit statistically significant partner preference for reciprocal inhibition—specifically between neurons of the same predicted neurotransmitter ($\text{GABA} \leftrightarrow \text{GABA}$)—when properly conditioning on physical network reciprocity and directed degree distributions?

---

## 4. The Principal Methodological Challenge

### Topological Confounding in Classical Rewiring
In network biology, configuration models generated via degree-preserving edge swapping (Markov Chain Monte Carlo edge-swapping) are the standard baseline for motif analysis. However, in dense, spatially compartmentalized neuropils like the Ellipsoid Body:
1. Empirical edge reciprocity is exceptionally high ($R_{\text{edge}} = 44.50\%$, $M = 3,518$ mutual dyads).
2. Edge swapping preserves node in-degrees and out-degrees but randomizes edge pairings, causing edge reciprocity to collapse to $9.66\% \pm 0.17\%$ ($M_{\text{null}} \approx 764$).
3. This $4.61\times$ destruction of reciprocal dyads artificially inflated unconditioned motif counts, conflating physical reciprocity with transmitter-level partner selection.

### The Solution: Conditional Label Permutation
We formulated a two-tier null model architecture:
* **Tier 1 (Topological Null)**: Evaluates whether empirical reciprocity exceeds degree-matched random graphs.
* **Tier 2 (Chemical Conditional Null)**: Holds the empirical mutual dyad graph $\mathcal{M}$ invariant and permutes predicted whole-neuron transmitter labels within joint degree strata (e.g., a $3 \times 3$ grid of directed in-degree and out-degree tertiles). This preserves both the physical dyad scaffold and the correlation between connectivity and neurotransmitter class.

---

## 5. Calibrated Quantitative Findings

All primary metrics are verified at threshold $w \ge 5$ in the Ellipsoid Body ($N = 483$ active neurons, $E = 15,812$ directed edges, $M = 3,518$ mutual dyads):

1. **Observed Reciprocal Inhibition**:
   - $2,615$ consensus $\text{GABA} \leftrightarrow \text{GABA}$ mutual dyads ($74.33\%$ of all mutual dyads).
2. **Conditional Enrichment Across Null Models ($B = 2,000$ permutations)**:
   - **Mutual-Degree Quartiles (4 strata)**: Null Mean = $2,167.11 \pm 29.31$ | Enrichment = **$1.2067\times$ (+20.7%)** | $Z = +15.28$, $p = 0.000500$ (FDR $q = 0.001749$).
   - **Directed In $\times$ Out Tertiles (9 strata)**: Null Mean = $2,037.96 \pm 35.86$ | Enrichment = **$1.2831\times$ (+28.3%)** | $Z = +16.09$, $p = 0.000500$.
   - **Directed In $\times$ Out Medians (4 strata)**: Null Mean = $1,984.76 \pm 48.05$ | Enrichment = **$1.3175\times$ (+31.8%)** | $Z = +13.12$, $p = 0.000500$.
3. **Anatomical Substrate Breakdown (FlyWire v2.1.0 Annotations)**:
   - $100.00\%$ of active EB neurons ($483 / 483$) and mutual dyads ($3,518 / 3,518$) matched annotation rows.
   - **$88.18\%$ of GABA–GABA dyads** ($2,306 / 2,615$) connect ring neurons to ring neurons.
   - **$77.48\%$ of GABA–GABA dyads** ($2,026 / 2,615$) connect neurons sharing the exact same reported ER base type among the top 8 subclasses (ER2: 458, ER3d: 445, ER4d: 274, ER3w: 243, ER5: 191, ER3a: 174, ER3p: 129, ER3m: 112).
   - Reciprocal compass loops (`EPG <-> PEN_a`, `EPG <-> PEN_b`) account for $305$ dyads ($8.67\%$ of total mutual dyads), forming a separate, non-GABAergic columnar feedback loop.

---

## 6. Key Methodological Limitations

1. **Single Connectome Scope**: All findings derive from a single adult female *Drosophila* brain (FAFB v783). Cross-individual variability cannot be evaluated from this dataset alone.
2. **Computational Transmitter Predictions**: Neurotransmitter classifications are computationally predicted consensus phenotypes from deep-learning models, not direct in vivo measurements of post-synaptic conductance or receptor binding ($Rdl$ vs. others).
3. **Discrete Degree Stratification**: Sensitivity models bin neurons into discrete tertiles/quartiles rather than preserving exact continuous joint degree sequences.
4. **Descriptive Nature of Cell-Type Counts**: Cell-type distributions are descriptive anatomy, not an independent significance test of cell-type preference.
5. **Static Circuit Anatomy**: Structural connectomics identifies physical synaptic adjacency, not continuous physiological dynamics or confirmed bump attractor stability.

---

## 7. Technologies and Methods Used

- **Programming & Analysis**: Python 3.12, PyArrow (Apache Arrow Feather IPC streaming), NetworkX graph concepts, Cairo / PyCairo.
- **Statistical Methods**: Monte Carlo label-permutation ensembles ($B = 2,000$), finite-sample empirical $p$-values, Benjamini-Hochberg False Discovery Rate (FDR) control, degree stratification.
- **Graph Algorithms**: Directed graph reciprocity ($R_{\text{edge}}$, $R_{\text{dyad}}$), weakly connected component analysis, autapse segregation, Markov Chain Monte Carlo edge-swap rewiring.
- **Data Engineering**: Memory-constrained processing ($< 250\text{ MB}$ peak RAM on an 8 GB laptop), 64-bit integer ID preservation, SHA-256 data provenance tracking.
- **Scientific Visualization**: Standalone, editable vector graphics (SVG) and raster exports (PNG) generated programmatically.

