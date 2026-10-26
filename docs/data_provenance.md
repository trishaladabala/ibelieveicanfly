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
  - `v783`: Updated proofread public benchmark release (Female Adult Fly Brain, FAFB).
- **Official Access & Portals**:
  - FlyWire Codex: [https://codex.flywire.ai](https://codex.flywire.ai)
  - Codex API / Downloads: [https://codex.flywire.ai/api/download](https://codex.flywire.ai/api/download)
  - Zenodo Archive: [https://zenodo.org/records/10676866](https://zenodo.org/records/10676866) (DOI: `10.5281/zenodo.10676866`)
  - Community Guidelines: [https://flywire.ai/guidelines](https://flywire.ai/guidelines)
- **Licensing & Terms**:
  - **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.
  - *Strict Non-Commercial Restriction*: Data cannot be used for commercial purposes without explicit permission.
  - *Mandatory Attribution*: Requires explicit citation of Dorkenwald et al. (2024), *Nature*, DOI: `10.1038/s41586-024-07558-y` and the Zenodo release DOI `10.5281/zenodo.10676866`.

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

## 4. Acquired Biological Dataset Audit (FAFB v783)

The official FlyWire aggregated proofread connections table was successfully acquired and verified on 2026-10-19:

- **Local Path**: `data/raw/fafb_v783/proofread_connections_783.feather`
- **File Format**: Apache Arrow IPC / Feather (V2)
- **Exact File Size**: `852,022,274 bytes` (812.55 MiB / 852.02 MB)
- **SHA-256 Checksum**: `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`
- **Total Physical Records**: `16,847,997 rows` (258 Arrow record batches of 65,536 rows each)
- **Source Direct URL**: `https://zenodo.org/api/records/10676866/files/proofread_connections_783.feather/content`
- **Source Record**: Zenodo Record `10676866` (DOI: `10.5281/zenodo.10676866`)
- **Access Date**: 2026-10-19
- **Licence**: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
- **Primary Citation**: Dorkenwald et al. (2024), *Nature*, DOI: `10.1038/s41586-024-07558-y`
- **Release Version**: FlyWire FAFB v783.0 (Zenodo Record `10676866`, DOI: `10.5281/zenodo.10676866`)
- **Excluded Large Files**: `flywire_synapses_783.feather` (~9.5 GB raw synapse cloud) was strictly excluded per hardware constraints.
- **Git Tracking Status**: Fully excluded by `.gitignore` (`data/raw/`).

---

## 5. Acquired Proofread Root IDs Array (`proofread_root_ids_783.npy`)

- **Local Path**: `data/raw/fafb_v783/proofread_root_ids_783.npy`
- **File Format**: NumPy binary array (`.npy`, uint64, shape `(139255,)`)
- **Exact File Size**: `1,114,168 bytes` (1.1 MB)
- **SHA-256 Checksum**: `7c7b7e818e9232e5ab64793d52ba20574dbe9da3a6509fbc74193b0f259a01be`
- **Source Direct URL**: `https://zenodo.org/api/records/10676866/files/proofread_root_ids_783.npy/content`
- **Total Proofread Neurons in Array**: `139,255`
- **Neuron Universe Reconciliation**:
  - Represented in `proofread_connections_783.feather`: `138,639` unique neurons (100% are proofread; 0 non-proofread IDs present).
  - Presynaptic active neurons: `138,005`
  - Postsynaptic active neurons: `137,090`
  - Bidirectionally connected: `136,456`
  - Pure source neurons (outgoing only): `1,549`
  - Pure target neurons (incoming only): `634`
  - Proofread neurons with zero connections in aggregated table: `616` (0.442% of population). These represent proofread somata/fragments lacking detected chemical synapses within the thresholded release.

