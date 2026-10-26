# Connectomics Research Question Shortlist

**Project:** "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics Pipeline  
**Dataset:** FlyWire FAFB v783 Aggregated Proofread Connections (`proofread_connections_783.feather`)  
**Environment:** Dell Inspiron 5558 (Intel Core i5-4210U, 8 GB RAM, Ubuntu 24.04 LTS)  
**Date:** October 2026

---

## Executive Summary

Based on our verified streaming benchmarks of the 16.8-million-row FlyWire FAFB v783 dataset and our memory-bounded integer graph engine, we evaluate three candidate research questions. Each candidate is biologically grounded, computationally feasible on 8 GB RAM hardware (<2.5 GiB active memory), scientifically tractable, and supported by concrete experimental controls.

```
+--------------------------------------------------------------------------------------------------+
| CANDIDATE 1: Neuropil Reciprocity Gradient (Sensory -> Associative -> Premotor)                 |
| Focus: Circuit architecture variation along information processing hierarchy                     |
+--------------------------------------------------------------------------------------------------+
| CANDIDATE 2: Neurotransmitter Pairing & E/I Balance in Reciprocal Dyads                         |
| Focus: Synaptic stabilization of feedback loops (ACh, GABA, Glutamate)                          |
+--------------------------------------------------------------------------------------------------+
| CANDIDATE 3: Hub Resilience and In Silico Knockout Vulnerability in Premotor Steering Centers   |
| Focus: Network tolerance to targeted damage in LAL / AVLP descending pathways                   |
+--------------------------------------------------------------------------------------------------+
```

---

## Candidate Project 1: Asymmetry of Recurrent Feedback Across the Sensory-to-Motor Hierarchy

### 1. Research Question
Does the prevalence and synaptic weight of reciprocal feedback loops ($\rho$) increase systematically along the functional hierarchy from primary sensory input (Antennal Lobe, Optic Lobe) to associative integration (Mushroom Body) to motor and steering neuropils (Central Complex, Lateral Accessory Lobe)?

### 2. Biological Motivation
Theoretical neuroscience posits that sensory processing requires rapid, high-fidelity feedforward routing with local lateral inhibition to prevent temporal blurring, whereas working memory, navigation, and motor coordination depend upon persistent recurrent state maintenance (e.g. ring attractors in heading direction circuits, Seelig & Jayaraman, 2015). Demonstrating an anatomical gradient in reciprocal feedback across standardized neuropils would provide physical proof of this architectural specialization across a complete whole-brain connectome.

### 3. Relevant Existing Literature
- Dorkenwald et al. (2024), *Nature*: Overview of brain-wide connectivity and hub hierarchy.
- Scheffer et al. (2020), *eLife*: Hemibrain central complex recurrence analysis.
- Schlegel et al. (2024), *Nature*: Functional annotations of sensory vs central vs motor neuropils.
- Song, S. et al. (2005), *PLoS Biology*: "Highly nonrandom features of synaptic connectivity in local cortical circuits" (early demonstration of over-represented reciprocal dyads).

### 4. What Is Already Known
- The adult fly connectome exhibits a brain-wide reciprocity of ~3.8–5.7%, which is roughly 100 times greater than expected by chance in an Erdős–Rényi random graph of identical size and density ($\rho_{ER} \approx 0.04\%$).
- Central complex neuropils (e.g., Ellipsoid Body `EB`, Protocerebral Bridge `PB`) host recurrent ring-attractor circuits.

### 5. What Remains Uncertain
- Whether the elevated reciprocity is uniformly distributed across the brain or concentrated primarily in motor and central neuropils.
- Whether sensory neuropils (e.g., Antennal Lobe `AL_L`, `AL_R`) exhibit significantly lower reciprocal density once local interneuron autapses and multi-glomerular cross-talk are controlled.

### 6. Data Required
- `proofread_connections_783.feather` (already acquired and verified).
- Partitioning of edges by neuropil tag (79 regions detected).

### 7. Methods Required
- Extract subgraphs induced by intra-neuropil edges for canonical sensory neuropils (`AL_L`, `AL_R`, `ME_R`), associative neuropils (`MB_CA_R`, `MB_PED_R`), and premotor/navigation neuropils (`EB`, `FB`, `LAL_R`, `AVLP_R`).
- Compute normalized reciprocity $\rho_{\text{neuropil}}$ and weight-asymmetry ratio $\log(w_{uv} / w_{vu})$.
- Construct configuration null models (degree-preserving edge swaps) for each neuropil to calculate the statistical z-score of reciprocal dyad over-representation.

### 8. Necessary Controls
- **Null Model:** Maslov-Sneppen degree-preserving randomized directed graph to control for degree distribution skewness.
- **Synaptic Threshold Sensitivity:** Validate invariance across $w \ge 1, 2, 3, 5, 10$ to ensure differences are not artifacts of single-synapse noise.
- **Inter- vs Intra-Neuropil Disambiguation:** Strictly separate internal local feedback from projection connections crossing neuropil boundaries.

### 9. Expected Computational Cost
- Processing time: ~10–15 seconds per neuropil subgraph.
- RAM overhead: < 150 MB (far below the 2.5 GiB ceiling).

### 10. Potential Confounding Factors
- Neuropil volume and synapse density disparities: Optic lobes and large neuropils have more neurons, potentially inflating dyad opportunity.
- Compartment boundary definition: Some neurons arborize across adjacent neuropils (e.g. `LAL` and `AVLP`).

### 11. What Result Would Count as Meaningful Evidence
A statistically significant monotonic increase in reciprocal dyad enrichment ($z_{\rho}$) from primary sensory (< 5-fold over random) to associative (15–30-fold) to premotor navigation hubs (> 80-fold over random), persisting across synapse thresholds $w \ge 3$.

### 12. How the Proposed Analysis Could Fail
If reciprocity is uniformly ~4–5% across all 79 neuropils, or if variations correlate purely with average local degree rather than functional tier, disproving a hierarchical gradient.

### 13. Why the Question Is Not Merely an Introductory Exercise
Standard introductory graph tutorials compute a single scalar reciprocity across an unannotated graph. This study couples anatomical taxonomy (Ito et al., 2014) and rigorous configuration null models to test a foundational hypothesis regarding the division of labor in neural circuits.

### 14. A Realistic Next Experiment
Implement `scripts/analyze_neuropil_reciprocity_hierarchy.py` to calculate intra-neuropil reciprocity across the 10 largest neuropils and execute 100 degree-preserving edge-swap permutations.

---

## Candidate Project 2: Neurotransmitter Pairing and E/I Balance in Reciprocal Dyads

### 1. Research Question
In reciprocal neuron pairs ($u \leftrightarrow v$), what is the relative prevalence of Excitatory-Excitatory (ACh-ACh), Inhibitory-Inhibitory (GABA-GABA), and Push-Pull / Feedback-Inhibitory (ACh-GABA, ACh-Glutamate) dyads, and does reciprocal excitation show evidence of structural synaptic damping?

### 2. Biological Motivation
Reciprocal excitation (ACh $\to$ ACh) generates positive feedback, which can destabilize neural dynamics or cause seizure-like runaway excitation unless tightly regulated. Conversely, reciprocal inhibition (GABA $\to$ GABA) mediates winner-take-all competition, and push-pull feedback (ACh $\to$ GABA $\to$ ACh) provides stabilization and oscillatory rhythm generation. Using deep-learning neurotransmitter predictions (Eckstein et al., 2024), we can map the chemical phenomenology of structural feedback loops.

### 3. Relevant Existing Literature
- Eckstein, Bates et al. (2024), *Cell*: EM-based neurotransmitter predictions in *Drosophila*.
- Schlegel et al. (2024), *Nature*: Transmitter distributions across cell classes.
- Isaacson, J. S. & Scanziani, M. (2011), *Neuron*: "How inhibition shapes cortical activity" (principles of E/I balance in recurrent microcircuits).

### 4. What Is Already Known
- Whole-brain chemical synapse composition is ~46% Acetylcholine (excitatory), ~25% GABA (inhibitory), ~17% Glutamate (primarily inhibitory in insects via GluCl channels, though can be excitatory), and <12% neuromodulators (verified in our Phase C benchmarks).
- Reciprocal loops exist in abundance (~200,000+ mutual dyads across the brain).

### 5. What Remains Uncertain
- Whether mutual dyads exhibit homophilic transmitter pairing (ACh-ACh, GABA-GABA) more or less frequently than expected under random independent assortment.
- Whether reciprocal excitatory dyads have systematically lower synaptic weights than reciprocal inhibitory dyads to prevent runaway excitation.

### 6. Data Required
- `proofread_connections_783.feather` columns `ach_avg`, `gaba_avg`, `glut_avg`.
- Predicted dominant transmitter assigned to each neuron via its presynaptic consensus.

### 7. Methods Required
- Assign each neuron $u$ a primary transmitter identity based on its average presynaptic synapse scores across all outgoing connections.
- For all identified mutual dyads $(u, v)$, classify the dyad as:
  - `ACh - ACh` (Reciprocal Excitatory)
  - `GABA - GABA` (Reciprocal Inhibitory)
  - `Glut - Glut` (Reciprocal Glutamatergic)
  - `ACh - GABA` (Feedback / Push-Pull)
  - `Mixed / Modulatory`
- Compare observed dyad frequencies against the multinomial null distribution $P(T_u, T_v) = 2 P(T_u) P(T_v)$.

### 8. Necessary Controls
- **Transmitter Prediction Confidence Filter:** Filter out neurons where the top transmitter probability is < 0.60 to avoid ambiguous assignments.
- **Synapse Weight Scaling:** Compare mean synapse counts across dyad classes to control for connection size.

### 9. Expected Computational Cost
- Processing time: ~20–30 seconds.
- RAM overhead: < 350 MB.

### 10. Potential Confounding Factors
- Multi-transmitter co-transmission in certain insect neurons.
- Post-synaptic receptor ambiguity (e.g. Glutamate acting via inhibitory GluCl vs excitatory DmGluRA).

### 11. What Result Would Count as Meaningful Evidence
Depletion of high-weight reciprocal ACh-ACh dyads relative to null expectation, accompanied by significant enrichment of ACh-GABA push-pull loops, demonstrating anatomical structural damping of positive feedback.

### 12. How the Proposed Analysis Could Fail
If neurotransmitter classification certainty is too low across sparse interneurons, or if dyad pairing reflects purely random independent sampling of regional transmitter proportions.

### 13. Why the Question Is Not Merely an Introductory Exercise
It directly bridges graph topology with physical neurochemistry and physiological stability principles, addressing how real nervous systems maintain dynamic balance.

### 14. A Realistic Next Experiment
Develop `scripts/analyze_reciprocal_transmitter_pairing.py` to assign transmitter consensus to the top 20,000 neurons and compute dyad contingency tables.

---

## Candidate Project 3: Hub Resilience and In Silico Knockout Vulnerability in Premotor Steering Centers

### 1. Research Question
To what extent is structural communication between sensory input streams and descending premotor commands dependent on a sparse core of "super-hubs" in the Lateral Accessory Lobe (`LAL`) and Anterior Ventrolateral Protocerebrum (`AVLP`), versus resilient, degenerate parallel pathways?

### 2. Biological Motivation
Biological neural circuits must withstand structural degradation, developmental variability, and physical injury. In *Drosophila*, locomotion and flight steering depend heavily on premotor integration centers (`LAL`, `AVLP`) that funnel brain-wide activity into descending neurons (DNs) reaching the ventral nerve cord (Namiki et al., 2018). Determining whether this routing network exhibits a "scale-free" vulnerability (where targeted removal of the top 1% hubs fragments the network) or an ultra-resilient degenerate mesh illuminates insect behavioral fault tolerance.

### 3. Relevant Existing Literature
- Albert, R., Jeong, H., & Barabási, A. L. (2000), *Nature*: "Error and attack tolerance of complex networks."
- Namiki, S. et al. (2018), *eLife*: "The functional organization of descending motor output in *Drosophila*."
- Scheffer et al. (2020), *eLife*: Hub classification in the central complex.

### 4. What Is Already Known
- Degree distributions in the fly brain have long tails, with individual hubs having in/out-degrees exceeding 500–1,000 partners (confirmed in our benchmarks).
- Premotor regions like `AVLP_R` and `LAL_R` represent the highest-volume synaptic centers outside the optic lobes.

### 5. What Remains Uncertain
- How the giant connected component (GCC) and average shortest path length degrade under sequential in silico ablation of top out-degree hubs vs top in-degree hubs vs random node removal.
- Whether alternative detour pathways maintain functional reachability between sensory projection neurons and descending motor neurons when major hubs are disabled.

### 6. Data Required
- `proofread_connections_783.feather`.
- Subgraphs spanning sensory-to-premotor pathways (`AL` $\to$ `LAL` / `AVLP`).

### 7. Methods Required
- Target subgraphs of 5,000–15,000 neurons in premotor centers.
- Simulate progressive node ablation (0% to 20% in steps of 1%):
  - Strategy A: Targeted removal of highest out-degree hubs.
  - Strategy B: Targeted removal of highest in-degree hubs.
  - Strategy C: Targeted removal of highest synapse strength hubs.
  - Strategy D: Random node ablation (100 Monte Carlo iterations).
- Track percolation metrics: GCC size, network diameter, and pair reachability.

### 8. Necessary Controls
- Random removal control (Erdős–Rényi percolation).
- Synapse thresholding control ($w \ge 1$ vs $w \ge 5$).

### 9. Expected Computational Cost
- Processing time: ~40–60 seconds using DisjointSet recalculation.
- RAM overhead: < 250 MB.

### 10. Potential Confounding Factors
- Missing neurons or incomplete proofreading in peripheral tracts.
- Static graph reachability does not capture dynamic synaptic weighting or polysynaptic timing.

### 11. What Result Would Count as Meaningful Evidence
Demonstration of a critical percolation threshold $f_c$ where removal of a specific small fraction (< 3%) of premotor hubs collapses sensory-to-motor path reachability, identifying biological single-points-of-failure in insect motor control.

### 12. How the Proposed Analysis Could Fail
If high pathway degeneracy renders the network equally resilient to targeted and random removal, or if the giant component remains intact up to 30% node removal due to dense mesh-like neuropil neuropil cross-talk.

### 13. Why the Question Is Not Merely an Introductory Exercise
It addresses concrete neuroethological questions regarding damage vulnerability in premotor flight and walking control circuits, with direct relevance to bio-inspired robotics and resilient neuromorphic architecture.

### 14. A Realistic Next Experiment
Implement `scripts/simulate_premotor_hub_ablation.py` on the `LAL`/`AVLP` premotor subgraph.

---

## 4. Priority Recommendation and Roadmap

| Project | Biological Impact | Tractability on 8 GB RAM | Scientific Novelty | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate 1: Neuropil Reciprocity Gradient** | Very High | **Immediate (< 1 min)** | High | **Primary Focus for Sprint** |
| **Candidate 2: Reciprocal Transmitter Pairing** | High | High (< 2 min) | High | **Secondary Investigation** |
| **Candidate 3: Premotor Hub Ablation** | High | High (< 2 min) | Medium | **Follow-up / Extension** |

**Selected Immediate Task:** Implement Candidate 1 as a focused, high-value pilot to examine structural reciprocity variation across canonical sensory, associative, and premotor neuropils.

