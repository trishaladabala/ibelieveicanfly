import json
from pathlib import Path
from collections import Counter

cache_path = Path("results/real_data_pilot/phase7/eb_node_covariates.json")
with open(cache_path) as f:
    data = json.load(f)

nodes = data["active_nodes"]
node_dict = data["nodes"]

print(f"Total nodes: {len(nodes)}")

# Let us test Model 1: 2D Directed Degree Grid (In-degree tertiles x Out-degree tertiles = 9 bins)
in_degs = [node_dict[str(n)]["in_deg"] for n in nodes]
out_degs = [node_dict[str(n)]["out_deg"] for n in nodes]
m_degs = [node_dict[str(n)]["m_deg"] for n in nodes]
confs = [node_dict[str(n)]["conf"] for n in nodes]

def get_tertile_bins(vals):
    s = sorted(vals)
    t1 = s[len(s)//3]
    t2 = s[2*len(s)//3]
    return t1, t2

in_t1, in_t2 = get_tertile_bins(in_degs)
out_t1, out_t2 = get_tertile_bins(out_degs)

print(f"In-degree tertile cutoffs: <= {in_t1}, {in_t1+1}-{in_t2}, > {in_t2}")
print(f"Out-degree tertile cutoffs: <= {out_t1}, {out_t1+1}-{out_t2}, > {out_t2}")

grid_9 = Counter()
grid_9_nt = {}
for n in nodes:
    d = node_dict[str(n)]
    i_bin = 0 if d["in_deg"] <= in_t1 else (1 if d["in_deg"] <= in_t2 else 2)
    o_bin = 0 if d["out_deg"] <= out_t1 else (1 if d["out_deg"] <= out_t2 else 2)
    key = (i_bin, o_bin)
    grid_9[key] += 1
    if key not in grid_9_nt:
        grid_9_nt[key] = Counter()
    grid_9_nt[key][d["nt_name"]] += 1

print("\n--- Model 1: 2D Directed Degree (In x Out, 9 bins) ---")
for k in sorted(grid_9.keys()):
    cnt = grid_9[k]
    nt_dist = dict(grid_9_nt[k])
    gaba_pct = nt_dist.get("gaba", 0) / cnt * 100
    print(f"  Bin In_{k[0]}_Out_{k[1]}: N={cnt:3d} | GABA={gaba_pct:5.1f}% | Dist: {nt_dist}")

# Let us test Model 2: Joint Mutual-Degree and Confidence (2x2 = 4 strata or 3x2 = 6 strata)
m_med = sorted(m_degs)[len(nodes)//2]
c_med = sorted(confs)[len(nodes)//2]
print(f"\nMutual degree median: {m_med}, Confidence median: {c_med:.4f}")

grid_mc = Counter()
grid_mc_nt = {}
for n in nodes:
    d = node_dict[str(n)]
    m_b = 0 if d["m_deg"] <= m_med else 1
    c_b = 0 if d["conf"] <= c_med else 1
    key = (m_b, c_b)
    grid_mc[key] += 1
    if key not in grid_mc_nt:
        grid_mc_nt[key] = Counter()
    grid_mc_nt[key][d["nt_name"]] += 1

print("\n--- Model 2: Joint Mutual-Degree x Confidence (4 bins) ---")
for k in sorted(grid_mc.keys()):
    cnt = grid_mc[k]
    nt_dist = dict(grid_mc_nt[k])
    gaba_pct = nt_dist.get("gaba", 0) / cnt * 100
    print(f"  Bin M_{k[0]}_Conf_{k[1]}: N={cnt:3d} | GABA={gaba_pct:5.1f}% | Dist: {nt_dist}")

# Let us test Model 3: Joint In-Degree, Out-Degree, and Mutual-Degree Composite
# Specifically: 2x2 grid of In-Degree x Out-Degree median splits
in_med = sorted(in_degs)[len(nodes)//2]
out_med = sorted(out_degs)[len(nodes)//2]
print(f"\nIn-degree median: {in_med}, Out-degree median: {out_med}")

grid_4 = Counter()
grid_4_nt = {}
for n in nodes:
    d = node_dict[str(n)]
    i_b = 0 if d["in_deg"] <= in_med else 1
    o_b = 0 if d["out_deg"] <= out_med else 1
    key = (i_b, o_b)
    grid_4[key] += 1
    if key not in grid_4_nt:
        grid_4_nt[key] = Counter()
    grid_4_nt[key][d["nt_name"]] += 1

print("\n--- Model 3: 2D Directed Degree (In-med x Out-med, 4 bins) ---")
for k in sorted(grid_4.keys()):
    cnt = grid_4[k]
    nt_dist = dict(grid_4_nt[k])
    gaba_pct = nt_dist.get("gaba", 0) / cnt * 100
    print(f"  Bin In_{k[0]}_Out_{k[1]}: N={cnt:3d} | GABA={gaba_pct:5.1f}% | Dist: {nt_dist}")

