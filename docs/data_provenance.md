# Data Provenance and Connectome Scientific Context

## 1. Primary Fly Connectome Sources

Two major open-access electron microscopy (EM) reconstruction datasets represent modern *Drosophila melanogaster* connectomics:

### A. FlyWire Adult Whole-Brain Connectome
- **Organism**: *Drosophila melanogaster* (adult female, 7-day-old).
- **Consortium**: FlyWire Consortium (Princeton University, MRC Laboratory of Molecular Biology, Cambridge, et al.).
- **Key Publications**:
  - Dorkenwald et al. (2024), *Nature*, "Neuronal wiring diagram of an adult brain".
  - Schlegel et al. (2024), *Nature*, "Whole-brain annotation and multi-connectome marker catalog".
- **Scale**: ~139,255 reconstructed neurons and ~50 million synapses across the entire central brain and optic lobes.
- **Versions**:
  - `v630`: Initial static release.
  - `v783`: Updated proofread public benchmark release.
- **Official Access & Portal**: [FlyWire Codex](https://codex.flywire.ai) and the Princeton FlyWire data dump repository.
- **Licensing**: Creative Commons Attribution 4.0 International (CC-BY 4.0).

### B. Janelia Hemibrain
- **Organism**: *Drosophila melanogaster* (central brain only).
- **Institution**: Janelia Research Campus, Howard Hughes Medical Institute (HHMI).
- **Key Publication**: Scheffer et al. (2020), *eLife*, "A connectome and analysis of the adult *Drosophila* central brain".
- **Scale**: ~25,000 neurons, ~20 million synapses.
- **Portal**: [neuPrint](https://neuprint.janelia.org).
- **Licensing**: Open access with citation requirement.

---

## 2. Structural Types of Connectomics Data Files

When acquiring or working with connectome releases, three distinct file formats are typically distributed:

| Dataset Layer | Typical Size (Uncompressed) | Key Fields | Suitability for Dell Inspiron 5558 |
|---|---|---|---|
| **1. Aggregated Connections** | ~100 MB – 400 MB (CSV) | `pre_root_id`, `post_root_id`, `syn_count`, `nt_type` | **Optimal for preliminary research**. Readily streamable; memory footprint can be restricted to < 500 MiB. |
| **2. Cell Metadata / Catalog** | ~10 MB – 30 MB (CSV) | `root_id`, `cell_type`, `super_class`, `hemisphere` | **Optimal**. Essential for grouping connectivity by biological function (sensory, motor, central). |
| **3. Raw Synapse Cloud** | ~3 GB – 15 GB (CSV/Parquet) | `synapse_id`, `pre_pt_x`, `pre_pt_y`, `pre_pt_z`, coordinates | **High Risk on 8 GB RAM / HDD**. Scanning 50M rows on a 5400 RPM drive causes severe I/O bottlenecks and risks swap thrashing. |

---

## 3. Essential Scientific Distinctions on "Weights"

In computational biology and network science, the term "weight" is frequently overloaded. We explicitly enforce the following distinctions:

1. **Anatomical Synapse Count ($n_{ij}$)**:
   - What connectomics data measure: The physical count of identifiable chemical synapses (active zones/T-bars with adjacent postsynaptic densities) between neuron $i$ and neuron $j$.
   - Mathematical nature: Non-negative integer ($n_{ij} \in \mathbb{N}_0$).
   - Biological meaning: Indicates anatomical connectivity redundancy. While often correlated with physiological coupling strength, a high synapse count does not guarantee high post-synaptic depolarization.

2. **Physiological Connection Strength ($w_{ij}^{phys}$)**:
   - What electrophysiology measures: The amplitude of the post-synaptic potential (PSP in mV) or conductance change ($g_{syn}$ in nS).
   - Biological determinants: Presynaptic vesicle release probability, quantal size, neurotransmitter identity (excitatory e.g. acetylcholine vs inhibitory e.g. GABA/glutamate), receptor subtype and density, and active dendritic integration.
   - *Cannot be equated directly to synapse count without biophysical modeling.*

3. **Artificial Neural Network (ANN) Weights ($W_{ij}$)**:
   - What machine learning models use: Continuous real-valued parameters ($W_{ij} \in \mathbb{R}$) trained via loss function minimization and gradient descent.
   - Conceptual difference: Biological brains do not pass scalar activations through static linear matrix multiplications. Connectome graphs are biological communication networks, not unconstrained feedforward neural networks.

---

## 4. Dataset Acquisition Protocol

Under our research safety constraints:
- **No automatic downloading** of multi-gigabyte files.
- When ready for real Drosophila data:
  1. Target the **FlyWire v783 aggregated connections table** (compressed CSV/gzip or Parquet, ~50-80 MB download).
  2. Target the **FlyWire cell classification table** (~5 MB download).
  3. Validate cryptographic checksums (SHA256) upon acquisition.
