import json
from pathlib import Path
from collections import Counter, defaultdict
import random
import math

cache_path = Path("results/real_data_pilot/phase7/eb_node_covariates.json")
with open(cache_path) as f:
    data = json.load(f)

nodes = data["active_nodes"]
node_dict = data["nodes"]
mutual_dyads = data["mutual_dyads"]

# Observed count
obs_gaba = sum(1 for u, v in mutual_dyads if node_dict[str(u)]["nt_name"] == "gaba" and node_dict[str(v)]["nt_name"] == "gaba")
print(f"Observed GABA-GABA mutual dyads: {obs_gaba} / {len(mutual_dyads)} ({obs_gaba/len(mutual_dyads)*100:.2f}%)")

def run_perms(strata_dict, num_perms=2000, seed=42):
    rng = random.Random(seed)
    dist = [0] * num_perms
    strata_list = list(strata_dict.values())
    for b in range(num_perms):
        mapping = {}
        for st in strata_list:
            lbls = [node_dict[str(n)]["nt"] for n in st]
            rng.shuffle(lbls)
            mapping.update(zip(st, lbls))
        c = sum(1 for u, v in mutual_dyads if mapping[u] == 1 and mapping[v] == 1)
        dist[b] = c
    mean_val = sum(dist) / num_perms
    var_val = sum((x - mean_val)**2 for x in dist) / (num_perms - 1)
    std_val = math.sqrt(var_val)
    z = (obs_gaba - mean_val) / std_val
    extreme = sum(1 for x in dist if abs(x - mean_val) >= abs(obs_gaba - mean_val))
    p_val = (extreme + 1) / (num_perms + 1)
    return {
        "null_mean": round(mean_val, 2),
        "null_std": round(std_val, 2),
        "z_score": round(z, 2),
        "empirical_p": p_val,
        "enrichment": round(obs_gaba / mean_val, 4),
        "min": min(dist),
        "max": max(dist),
    }

# Baseline Phase 6: Mutual Degree Quartiles
m_degs = {n: node_dict[str(n)]["m_deg"] for n in nodes}
sorted_m = sorted(nodes, key=lambda n: m_degs[n])
b_size = len(nodes) // 4
strata_p6 = {
    0: sorted_m[:b_size],
    1: sorted_m[b_size:2*b_size],
    2: sorted_m[2*b_size:3*b_size],
    3: sorted_m[3*b_size:],
}
res_p6 = run_perms(strata_p6)
print(f"Phase 6 Baseline (Mutual Degree Quartiles): Null={res_p6['null_mean']} +/- {res_p6['null_std']}, Enr={res_p6['enrichment']:.4f}x, Z={res_p6['z_score']}, p={res_p6['empirical_p']}")

# Model A: 2D Directed Degree (In-med x Out-med, 4 bins)
in_degs = [node_dict[str(n)]["in_deg"] for n in nodes]
out_degs = [node_dict[str(n)]["out_deg"] for n in nodes]
in_med = sorted(in_degs)[len(nodes)//2]
out_med = sorted(out_degs)[len(nodes)//2]
strata_dir4 = defaultdict(list)
for n in nodes:
    d = node_dict[str(n)]
    i_b = 0 if d["in_deg"] <= in_med else 1
    o_b = 0 if d["out_deg"] <= out_med else 1
    strata_dir4[(i_b, o_b)].append(n)
res_dir4 = run_perms(strata_dir4)
print(f"Model A (Joint Directed In-med x Out-med, 4 bins): Null={res_dir4['null_mean']} +/- {res_dir4['null_std']}, Enr={res_dir4['enrichment']:.4f}x, Z={res_dir4['z_score']}, p={res_dir4['empirical_p']}")

# Model B: 2D Directed Degree (In-tertile x Out-tertile, 9 bins)
s_in = sorted(in_degs)
s_out = sorted(out_degs)
in_t1, in_t2 = s_in[len(nodes)//3], s_in[2*len(nodes)//3]
out_t1, out_t2 = s_out[len(nodes)//3], s_out[2*len(nodes)//3]
strata_dir9 = defaultdict(list)
for n in nodes:
    d = node_dict[str(n)]
    i_b = 0 if d["in_deg"] <= in_t1 else (1 if d["in_deg"] <= in_t2 else 2)
    o_b = 0 if d["out_deg"] <= out_t1 else (1 if d["out_deg"] <= out_t2 else 2)
    strata_dir9[(i_b, o_b)].append(n)
res_dir9 = run_perms(strata_dir9)
print(f"Model B (Joint Directed In-tert x Out-tert, 9 bins): Null={res_dir9['null_mean']} +/- {res_dir9['null_std']}, Enr={res_dir9['enrichment']:.4f}x, Z={res_dir9['z_score']}, p={res_dir9['empirical_p']}")

# Model C: Directed Total Degree Quartiles x Confidence Median (8 bins)
tot_degs = {n: node_dict[str(n)]["tot_deg"] for n in nodes}
s_tot = sorted(nodes, key=lambda n: tot_degs[n])
c_med = sorted([node_dict[str(n)]["conf"] for n in nodes])[len(nodes)//2]
tot_q_size = len(nodes) // 4
tot_q_cutoffs = [tot_degs[s_tot[tot_q_size]], tot_degs[s_tot[2*tot_q_size]], tot_degs[s_tot[3*tot_q_size]]]

strata_c8 = defaultdict(list)
for n in nodes:
    d = node_dict[str(n)]
    td = d["tot_deg"]
    q_b = 0 if td <= tot_q_cutoffs[0] else (1 if td <= tot_q_cutoffs[1] else (2 if td <= tot_q_cutoffs[2] else 3))
    c_b = 0 if d["conf"] <= c_med else 1
    strata_c8[(q_b, c_b)].append(n)

# Check strata sizes for Model C
print("\nModel C Strata Sizes (Tot-Degree Quartile x Conf Median):")
for k in sorted(strata_c8.keys()):
    cnt = len(strata_c8[k])
    gaba_cnt = sum(1 for n in strata_c8[k] if node_dict[str(n)]["nt_name"] == "gaba")
    print(f"  Stratum {k}: N={cnt:2d}, GABA={gaba_cnt:2d} ({gaba_cnt/cnt*100:5.1f}%)")

res_c8 = run_perms(strata_c8)
print(f"Model C (Tot-Degree Quartiles x Conf Median, 8 bins): Null={res_c8['null_mean']} +/- {res_c8['null_std']}, Enr={res_c8['enrichment']:.4f}x, Z={res_c8['z_score']}, p={res_c8['empirical_p']}")
