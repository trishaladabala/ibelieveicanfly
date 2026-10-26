# Phase 6 Project Audit and Provenance Traceability Matrix

**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Whole-Brain Connectomics  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Date of Audit**: October 20, 2026 (Phase 6 Kickoff)  
**Hardware Baseline**: Dell Inspiron 5558 (Intel Core i5-4210U @ 1.70 GHz, 2C/4T, 8 GB RAM, 1 TB 5400 RPM HDD, Ubuntu 24.04.5 LTS)  
**Execution Environment**: Project-local virtual environment (`.venv`, Python 3.12, PyArrow 26.0.0)  

---

## 1. Primary Dataset Checksums and Provenance

| Logical Dataset | Actual File Path | File Size (Bytes) | SHA-256 Checksum | Ingestion Status | Official Reference & Version |
|---|---|---|---|---|---|
| **Whole-Brain Aggregated Connections** | `data/raw/fafb_v783/proofread_connections_783.feather` | 852,022,274 | `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf` | 16,847,997 rows, 258 Arrow batches | FlyWire FAFB Release 783.0 (Zenodo: 10676866) |
| **Official Proofread Root IDs** | `data/raw/fafb_v783/proofread_root_ids_783.npy` | 1,114,168 | `7c7b7e818e9232e5ab64793d52ba20574dbe9da3a6509fbc74193b0f259a01be` | 139,255 binary uint64 IDs | FlyWire FAFB Release 783.0 (Zenodo: 10676866) |

---

## 2. Inventory of Existing Results, Scripts, and Artifacts

| Generated Artifact | File Size | Timestamp | Primary Producing Script | Execution Parameters | Memory & Time |
|---|---|---|---|---|---|
| `results/real_data_pilot/verified_threshold_sensitivity.json` | 7,850 B | 2026-10-19 20:18:38 | `scripts/run_whole_brain_threshold_sensitivity.py` | Multi-threshold $w \in \{1, 2, 3, 5, 10, 20\}$, autapses excluded | Peak RAM 1.41 GiB, 191.9 s |
| `results/real_data_pilot/neuron_universe_reconciliation.json` | 1,986 B | 2026-10-19 22:57:00 | `scripts/verify_neuron_universe.py` | Complete census: 139,255 root IDs vs connection endpoints | Peak RAM 110 MB, 12.4 s |
| `results/real_data_pilot/verified_neurotransmitter_summary.json` | 1,033 B | 2026-10-19 22:22:07 | `scripts/audit_neurotransmitters.py` | 4 denominator formulations, 16.85M rows | Peak RAM 119.4 MB, 178.1 s |
| `results/real_data_pilot/verified_regional_metrics.json` | 135,698 B | 2026-10-19 22:24:00 | `scripts/analyze_all_neuropils_reciprocity.py` | All 79 standard neuropils, $w \in \{1, 3, 5, 10\}$ | Peak RAM 1.40 GiB, 71.5 s |
| `results/real_data_pilot/verified_reciprocal_transmitters.json` | 163,958 B | 2026-10-19 22:31:39 | `scripts/analyze_reciprocal_transmitters.py` | Whole brain ($w \ge 1, 5$), regions ($w \ge 1, 3$), $B=200$ permutations | Peak RAM 2.23 GiB, 310.8 s |
| `results/real_data_pilot/central_complex_degree_preserving_null.json` | 44,569 B | 2026-10-20 00:03:52 | `scripts/analyze_central_complex_rewiring.py` | EB, FB, PB at $w \in \{3, 5\}$, $B=100$ permutations, $10\times |E|$ swaps | Peak RAM 234.5 MB, 786.5 s |

---

## 3. Systematic Claims Audit & Reproduction Matrix

| Claim | Reported Value | Source Script | Input Dataset | Graph Definition | Threshold | Reproduction Status | Outstanding Concern |
|---|---|---|---|---|---|---|---|
| **Physical Records Count** | 16,847,997 | `inspect_dataset.py`, Arrow reader | `proofread_connections_783.feather` | Tabular record count | None | **VERIFIED** | None. Exact PyArrow count verified across 258 batches. |
| **Total Synapses** | 54,492,922 | `audit_neurotransmitters.py` | `proofread_connections_783.feather` | Sum of `syn_count` column | None | **VERIFIED** | Missingness affects only 30,806 synapses ($0.0565\%$). |
| **Proofread Root IDs** | 139,255 | `verify_neuron_universe.py` | `proofread_root_ids_783.npy` | Unique proofread IDs in release | None | **VERIFIED** | Exactly 616 IDs lack chemical synapses in connection table. |
| **Connected Neurons** | 138,639 | `verify_neuron_universe.py` | `proofread_connections_783.feather` | Node set cardinality $\{pre\} \cup \{post\}$ | $w \ge 1$ | **VERIFIED** | 138,005 presynaptic, 137,090 postsynaptic, 634 pure target. |
| **Whole-Brain Edges ($w \ge 1$)** | 15,091,983 | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | Directed multi-neuropil merged edges $(u, v)$ | $w \ge 1$, autapses excluded | **VERIFIED** | Independently recomputed in `verify_thresholds_independent.py`. |
| **Mutual Dyads ($w \ge 1$)** | 2,007,259 | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | Unordered pairs $\{u, v\}$ with both $(u, v)$ and $(v, u) \ge 1$ | $w \ge 1$ | **VERIFIED** | Matches across 3 independent script implementations. |
| **Reciprocal Directed Edges ($w \ge 1$)** | 4,014,518 | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | Directed edges in mutual dyads ($2M$) | $w \ge 1$ | **VERIFIED** | Formula $2M$ strictly confirmed. |
| **Whole-Brain Edges ($w \ge 5$)** | 2,700,513 | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | Directed multi-neuropil merged edges | $w \ge 5$, autapses excluded | **VERIFIED** | Recomputed in `verify_thresholds_independent.py` ($100\%$ match). |
| **Mutual Dyads ($w \ge 5$)** | 188,724 | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | Unordered mutual dyads ($M$) | $w \ge 5$ | **VERIFIED** | Earlier draft typo labeled $2M=377,532$ as $M$; corrected. |
| **Reciprocal Directed Edges ($w \ge 5$)** | 377,448 | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | Directed reciprocal edges ($2M$) | $w \ge 5$ | **VERIFIED** | $2 \times 188,724 = 377,448$. |
| **Edge Reciprocity ($w \ge 5$)** | 13.98% | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | $R_{\text{edge}} = 2M / E$ | $w \ge 5$ | **VERIFIED** | $377,448 / 2,700,513 = 13.9769\%$. Matches Lin et al. benchmark (13.8%). |
| **Dyad Reciprocity ($w \ge 5$)** | 7.51% | `run_whole_brain_threshold_sensitivity.py` | `proofread_connections_783.feather` | $R_{\text{dyad}} = M / (E - M)$ | $w \ge 5$ | **VERIFIED** | $188,724 / (2,700,513 - 188,724) = 7.5135\%$. |
| **Whole-Brain Transmitter Mass** | ACh 48.38%, GABA 23.16%, Glut 19.25% | `audit_neurotransmitters.py` | `proofread_connections_783.feather` | Synapse-weighted probability mass across all synapses | All $w$ | **VERIFIED** | Proportions invariant within $\le 0.03\%$ across 4 denominator formulations. |
| **All-79 Neuropil Reciprocity Rank #1** | Ellipsoid Body (`EB`): $R_{\text{edge}} = 58.06\%$ ($w \ge 1$), $44.50\%$ ($w \ge 5$) | `analyze_all_neuropils_reciprocity.py` | `proofread_connections_783.feather` | Intra-neuropil directed edges | $w \ge 1, 5$ | **VERIFIED** | Evaluated across all 79 neuropils in single pass. |
| **Bilateral Reciprocity Symmetry** | All 35 bilateral pairs have Cohen's $|h| < 0.10$ | `analyze_all_neuropils_reciprocity.py` | `proofread_connections_783.feather` | Intra-neuropil edges partitioned by hemisphere | $w \ge 1$ | **REPRODUCED WITH CLARIFICATION** | Reflects anatomical morphological symmetry in this specimen, not direct proof of genetic invariance. |
| **Whole-Brain ACh-ACh Reciprocal Depletion** | Observed 9.66% vs Expected 45.10% ($0.214\times, Z=-29.05$) | `analyze_reciprocal_transmitters.py` | `proofread_connections_783.feather` | Whole-brain mutual dyads ($w \ge 5$), global node-label shuffle | $w \ge 5$ | **REPRODUCED WITH CLARIFICATION** | Global label shuffle does not account for cell-type degree heterogeneity or neuropil localization. |
| **Whole-Brain ACh-GABA Reciprocal Enrichment** | Observed 51.23% vs Expected 21.14% ($2.42\times, Z=+38.79$) | `analyze_reciprocal_transmitters.py` | `proofread_connections_783.feather` | Whole-brain mutual dyads ($w \ge 5$), global node-label shuffle | $w \ge 5$ | **REPRODUCED WITH CLARIFICATION** | Same qualification as above. |
| **EB GABA-GABA Mutual Dyad Count ($w \ge 5$)** | 2,615 observed mutual dyads | `analyze_central_complex_rewiring.py` | `proofread_connections_783.feather` | Intra-EB directed edges, consensus NT labels | $w \ge 5$ | **VERIFIED** | $2,615 / 3,518 = 74.33\%$ of all mutual dyads in EB. |
| **EB GABA-GABA Degree-Preserving Null Mean** | 385.8 (Null std 15.66) | `analyze_central_complex_rewiring.py` | `proofread_connections_783.feather` | Directed edge-swap null ($10\times |E|$ swaps, $B=100$) | $w \ge 5$ | **REPRODUCED WITH CLARIFICATION** | Requires mixing diagnostics and separation from overall reciprocity (Phase 3 & 4). |
| **FB ACh-GABA Degree-Preserving Null Mean** | 555 observed vs 59.2 null mean ($Z=+78.41$) | `analyze_central_complex_rewiring.py` | `proofread_connections_783.feather` | Directed edge-swap null ($10\times |E|$ swaps, $B=100$) | $w \ge 5$ | **REPRODUCED WITH CLARIFICATION** | Requires mixing diagnostics and conditional composition null (Phase 3 & 4). |
| **PB ACh-ACh Degree-Preserving Null Mean** | 35 observed vs 7.8 null mean ($Z=+10.60$) | `analyze_central_complex_rewiring.py` | `proofread_connections_783.feather` | Directed edge-swap null ($10\times |E|$ swaps, $B=100$) | $w \ge 5$ | **REPRODUCED WITH CLARIFICATION** | Requires mixing diagnostics and conditional composition null (Phase 3 & 4). |

---

## 4. Key Methodological Caveats Identified for Phase 6

1. **Separation of Reciprocity Quantity vs. Transmitter Quality**:
   The directed edge-swap null rewires the entire directed graph, which causes total mutual dyads ($M$) to drop from $3,518 \to \approx 768$ in EB and $5,442 \to \approx 751$ in FB. Consequently, a portion of the raw motif enrichment could simply reflect excess reciprocal topology. A conditional null that fixes $M$ and tests transmitter pairing directly is required in Phase 4.
2. **Markov Chain Mixing & Autocorrelation**:
   A high rewired edge fraction ($78\%\text{--}94\%$) indicates substantial edge disruption relative to the seed graph, but does not prove statistical independence or Markov chain convergence. Phase 3 must systematically measure acceptance rates, swap multiplier sensitivity ($10\times, 20\times, 50\times$), and chain autocorrelation.
3. **Consensus Phenotypes vs. Edge Predictions**:
   Consensus phenotypes represent the argmax of all presynaptic sites across the entire brain. Connection-level predictions (`gaba_avg`, `ach_avg`, etc.) within specific neuropils must be audited to verify that regional motifs are not distorted by multi-transmitter or atypical projections.

