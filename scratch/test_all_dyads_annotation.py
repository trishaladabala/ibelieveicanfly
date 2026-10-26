import csv
import json
from pathlib import Path
from collections import Counter

cache_path = Path("results/real_data_pilot/phase7/eb_node_covariates.json")
with open(cache_path) as f:
    eb_data = json.load(f)

mutual_dyads = eb_data["mutual_dyads"]
node_dict = eb_data["nodes"]

annot_file = Path("data/raw/annotations_v2.1.0/Supplemental_file1_neuron_annotations.tsv")
annotations = {}
with open(annot_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        rid = int(row["root_id"])
        if str(rid) in node_dict:
            annotations[rid] = {
                "cell_class": row["cell_class"].strip() if row["cell_class"] else "unannotated",
                "cell_sub_class": row["cell_sub_class"].strip() if row["cell_sub_class"] else "unannotated",
                "hemibrain_type": row["hemibrain_type"].strip() if row["hemibrain_type"] else (row["cell_type"].strip() if row["cell_type"] else "unannotated"),
            }

total_m = len(mutual_dyads)
print(f"Total Mutual Dyads in EB: {total_m}")

# 1. Breakdown by cell_sub_class pairing
subclass_pairs = Counter()
same_subclass_cnt = 0
diff_subclass_cnt = 0
unannotated_subclass_cnt = 0

for u, v in mutual_dyads:
    sc_u = annotations[u]["cell_sub_class"]
    sc_v = annotations[v]["cell_sub_class"]
    if sc_u == "unannotated" or sc_v == "unannotated":
        unannotated_subclass_cnt += 1
    elif sc_u == sc_v:
        same_subclass_cnt += 1
    else:
        diff_subclass_cnt += 1
    
    p = tuple(sorted([sc_u, sc_v]))
    subclass_pairs[p] += 1

print("\n--- All 3,518 Mutual Dyads: Cell Sub-Class Matching ---")
print(f"  Both Endpoints Same Sub-Class     : {same_subclass_cnt:4d} ({same_subclass_cnt/total_m*100:5.2f}%)")
print(f"  Endpoints Different Sub-Classes   : {diff_subclass_cnt:4d} ({diff_subclass_cnt/total_m*100:5.2f}%)")
print(f"  One/Both Endpoints Unannotated    : {unannotated_subclass_cnt:4d} ({unannotated_subclass_cnt/total_m*100:5.2f}%)")

print("\nTop Sub-Class Pairings Across All 3,518 Dyads:")
for p, cnt in subclass_pairs.most_common(10):
    print(f"  {p[0]:15s} <-> {p[1]:15s}: {cnt:4d} ({cnt/total_m*100:5.2f}%)")

# 2. Breakdown by hemibrain_type / cell_type
type_pairs = Counter()
same_type_cnt = 0
diff_type_cnt = 0
unannotated_type_cnt = 0

for u, v in mutual_dyads:
    t_u = annotations[u]["hemibrain_type"]
    t_v = annotations[v]["hemibrain_type"]
    if t_u == "unannotated" or t_v == "unannotated":
        unannotated_type_cnt += 1
    elif t_u == t_v:
        same_type_cnt += 1
    else:
        diff_type_cnt += 1
    p = tuple(sorted([t_u, t_v]))
    type_pairs[p] += 1

print("\n--- All 3,518 Mutual Dyads: Specific Cell Type Matching ---")
print(f"  Both Endpoints Same Type          : {same_type_cnt:4d} ({same_type_cnt/total_m*100:5.2f}%)")
print(f"  Endpoints Different Types         : {diff_type_cnt:4d} ({diff_type_cnt/total_m*100:5.2f}%)")
print(f"  One/Both Endpoints Unannotated    : {unannotated_type_cnt:4d} ({unannotated_type_cnt/total_m*100:5.2f}%)")

print("\nTop 15 Specific Type Pairings Across All 3,518 Dyads:")
for p, cnt in type_pairs.most_common(15):
    print(f"  {p[0]:15s} <-> {p[1]:15s}: {cnt:4d} ({cnt/total_m*100:5.2f}%)")

