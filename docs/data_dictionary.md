# Data Dictionary: Fly Connectomics Schemas

This document defines the schema, field types, semantic interpretations, and validation constraints for connectivity tables.

## 1. Aggregated Neuron-to-Neuron Connectivity Schema

Standard format: Comma-separated values (`.csv`) or Tab-separated values (`.tsv`).

| Column Name | Target Data Type | Allow Null? | Semantic Description | Technical / Numerical Constraints |
|---|---|---|---|---|
| `pre_root_id` | String / UInt64 | No | Identifier of the presynaptic (source) neuron. | In FlyWire, root IDs are 18-digit integers (e.g. `720575940614123456`). **CRITICAL**: Never parse as standard float (`float64`). IEEE 754 double precision loses exact integer representation beyond $2^{53} \approx 9.007 \times 10^{15}$, corrupting IDs. Treat as Python `int` or `str`. |
| `post_root_id` | String / UInt64 | No | Identifier of the postsynaptic (target) neuron. | Same precision requirements as `pre_root_id`. |
| `syn_count` (or `weight`) | UInt32 / Integer | No | Count of anatomical chemical synapses formed from `pre` to `post`. | Must be strictly positive integer ($\ge 1$). A zero value indicates non-connectivity and should not exist in sparse edge lists. |
| `nt_type` *(optional)* | Categorical / String | Yes | Predicted neurotransmitter phenotype. | Standard FlyWire categories: `acetylcholine` (ACh, excitatory), `gaba` (GABA, inhibitory), `glutamate` (GLUT, typically inhibitory in fly central brain), `dopamine`, `serotonin`, `octopamine`. |
| `neuropil` *(optional)* | String | Yes | Brain neuropil region where synaptic contacts occur (e.g., `AL_R`, `EB`, `MB_CA_R`). | Standard insect brain nomenclature. |

---

## 2. Cell Metadata & Annotation Schema

| Column Name | Target Data Type | Allow Null? | Semantic Description | Technical Constraints |
|---|---|---|---|---|
| `root_id` | String / UInt64 | No | Canonical neuron root ID matching connection endpoints. | Must maintain exact 64-bit integer integrity. |
| `super_class` | String | Yes | Broad anatomical classification. | Typical values: `central`, `sensory`, `motor`, `ascending`, `descending`, `visual_projection`, `visual_centrifugal`. |
| `cell_type` | String | Yes | Specific reconstructed morphological cell type (e.g., `DNp01`, `KCg`). | Free text or standardized taxonomy. |
| `hemisphere` | String | Yes | Somatic hemisphere (`left`, `right`, or `central`). | Case-insensitive token. |
| `flow` | String | Yes | Signal directionality category (`intrinsic`, `afferent`, `efferent`). | Informative for feeding input/output subgraphs. |

---

## 3. Data Integrity & Validation Rules

When processing connectivity tables, the pipeline enforces:
1. **No NaN / Missing Endpoints**: Any row with missing `pre_root_id` or `post_root_id` is recorded as a malformed record and excluded.
2. **Positive Synapse Counts**: Any row with `syn_count <= 0` or non-integer count is rejected.
3. **Directed Multi-edge Handling**: If identical pairs `(pre, post)` appear multiple times across chunks, the pipeline reports duplicates and sums or aggregates synapse counts depending on run parameters.
4. **Self-Loop Detection**: Where `pre_root_id == post_root_id`, records are tracked explicitly as autapses (self-connections), which exist biologically in insect neurons but require distinct consideration in network models.
