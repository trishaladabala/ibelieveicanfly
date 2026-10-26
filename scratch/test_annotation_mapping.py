import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

# Load EB active nodes and mutual dyads from cache
cache_path = Path("results/real_data_pilot/phase7/eb_node_covariates.json")
with open(cache_path) as f:
    eb_data = json.load(f)

active_nodes = set(eb_data["active_nodes"])
mutual_dyads = eb_data["mutual_dyads"]
node_dict = eb_data["nodes"]

print(f"Total EB Active Nodes: {len(active_nodes)}")
print(f"Total EB Mutual Dyads: {len(mutual_dyads)}")

# Ingest Supplemental_file1_neuron_annotations.tsv
annot_file = Path("data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv")
annotations = {}

with open(annot_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        rid = int(row["root_id"])
        if rid in active_nodes:
            annotations[rid] = {
                "flow": row["flow"].strip() if row["flow"] else "unannotated",
                "super_class": row["super_class"].strip() if row["super_class"] else "unannotated",
                "cell_class": row["cell_class"].strip() if row["cell_class"] else "unannotated",
                "cell_sub_class": row["cell_sub_class"].strip() if row["cell_sub_class"] else "unannotated",
                "cell_type": row["cell_type"].strip() if row["cell_type"] else "unannotated",
                "hemibrain_type": row["hemibrain_type"].strip() if row["hemibrain_type"] else "unannotated",
                "top_nt": row["top_nt"].strip() if row["top_nt"] else "unannotated",
                "known_nt": row["known_nt"].strip() if row["known_nt"] else "none",
            }

matched_nodes = len(annotations)
print(f"Matched Nodes in Annotation File: {matched_nodes} / {len(active_nodes)} ({matched_nodes/len(active_nodes)*100:.2f}%)")
unmatched_nodes = len(active_nodes) - matched_nodes
print(f"Unmatched Nodes: {unmatched_nodes}")

# Check coverage for endpoints of all mutual dyads and GABA-GABA dyads
gaba_gaba_dyads = [(u, v) for u, v in mutual_dyads if node_dict[str(u)]["nt_name"] == "gaba" and node_dict[str(v)]["nt_name"] == "gaba"]
print(f"\nTotal GABA-GABA Dyads: {len(gaba_gaba_dyads)}")

dyads_both_matched = sum(1 for u, v in mutual_dyads if u in annotations and v in annotations)
dyads_one_matched = sum(1 for u, v in mutual_dyads if (u in annotations) ^ (v in annotations))
dyads_none_matched = sum(1 for u, v in mutual_dyads if u not in annotations and v not in annotations)

gg_both_matched = sum(1 for u, v in gaba_gaba_dyads if u in annotations and v in annotations)
print(f"All Mutual Dyads Coverage: Both={dyads_both_matched} ({dyads_both_matched/len(mutual_dyads)*100:.2f}%), One={dyads_one_matched}, None={dyads_none_matched}")
print(f"GABA-GABA Dyads Coverage: Both={gg_both_matched} ({gg_both_matched/len(gaba_gaba_dyads)*100:.2f}%)")

# Inspect cell_class, cell_sub_class, and cell_type distributions among active nodes
classes = Counter(a["cell_class"] for a in annotations.values())
subclasses = Counter(a["cell_sub_class"] for a in annotations.values())
cell_types = Counter(a["cell_type"] for a in annotations.values())
hb_types = Counter(a["hemibrain_type"] for a in annotations.values())

print("\n--- Cell Class Breakdown (Nodes) ---")
for c, cnt in classes.most_common(10):
    print(f"  {c:25s}: {cnt:3d} ({cnt/len(active_nodes)*100:.1f}%)")

print("\n--- Cell Sub-Class Breakdown (Nodes) ---")
for c, cnt in subclasses.most_common(10):
    print(f"  {c:25s}: {cnt:3d} ({cnt/len(active_nodes)*100:.1f}%)")

print("\n--- Top Cell Types / Hemibrain Types (Nodes) ---")
for c, cnt in cell_types.most_common(15):
    print(f"  {c:25s}: {cnt:3d}")

# Break down GABA-GABA mutual dyads by cell_sub_class and cell_type
gg_pairs_subclass = Counter()
gg_pairs_type = Counter()

for u, v in gaba_gaba_dyads:
    au = annotations.get(u, {})
    av = annotations.get(v, {})
    
    # Subclass pairing
    sc_u = au.get("cell_sub_class", "unannotated")
    sc_v = av.get("cell_sub_class", "unannotated")
    sc_pair = tuple(sorted([sc_u, sc_v]))
    gg_pairs_subclass[sc_pair] += 1
    
    # Cell type pairing (using cell_type or hemibrain_type)
    t_u = au.get("cell_type", "unannotated")
    if t_u == "unannotated":
        t_u = au.get("hemibrain_type", "unannotated")
    t_v = av.get("cell_type", "unannotated")
    if t_v == "unannotated":
        t_v = av.get("hemibrain_type", "unannotated")
    t_pair = tuple(sorted([t_u, t_v]))
    gg_pairs_type[t_pair] += 1

print("\n--- GABA-GABA Dyads by Cell Sub-Class Pairing ---")
for p, cnt in gg_pairs_subclass.most_common(10):
    print(f"  {p[0]:20s} <-> {p[1]:20s}: {cnt:4d} ({cnt/len(gaba_gaba_dyads)*100:.2f}%)")

print("\n--- GABA-GABA Dyads by Cell Type Pairing (Top 15) ---")
for p, cnt in gg_pairs_type.most_common(15):
    print(f"  {p[0]:20s} <-> {p[1]:20s}: {cnt:4d} ({cnt/len(gaba_gaba_dyads)*100:.2f}%)")

