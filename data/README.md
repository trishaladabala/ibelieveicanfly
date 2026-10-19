# Data Directory: Connectome Datasets

This directory is designated for raw and processed connectivity datasets.

## IMPORTANT REPOSITORY POLICIES
1. **Never commit raw connectomics datasets to Git**: Full-brain connectome tables (e.g., FlyWire or Janelia hemibrain) can range from hundreds of megabytes (aggregated tables) to tens of gigabytes (individual synapse tables).
2. **Never modify original raw files**: All analysis pipelines must treat incoming data as read-only.
3. **Synthetic Test Data Exception**: Small, tracked test fixtures (e.g., `synthetic_connectivity_test.csv`) are permitted exclusively for continuous integration and unit testing.

## Data Subdirectories
- `raw/` *(untracked, gitignored)*: Place original downloaded CSV, TSV, or Parquet files here.
- `processed/` *(untracked, gitignored)*: Intermediate filtered tables or induced subgraphs.
- `fixtures/` *(tracked)*: Small synthetic or unit-test tables (< 50 KB).

## Adding Real Fly-Brain Datasets
When authorized to acquire real Drosophila connectomics data:
1. Review the data schema in `docs/data_dictionary.md`.
2. Review provenance, licensing, and access instructions in `docs/data_provenance.md`.
3. Prefer **aggregated connection tables** (e.g., `pre_root_id, post_root_id, syn_count`) over full raw synapse tables (~50M rows) to stay within the 2.5 GiB RAM and 5400 RPM HDD constraints.
