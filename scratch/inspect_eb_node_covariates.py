import sys
from pathlib import Path
from collections import defaultdict, Counter
import json

# Load graph data and node covariates for EB w >= 5
# Let us check if we can inspect the exact node properties from proofread_connections_783.feather
import pyarrow.ipc as ipc

FILE_PATH = Path("data/raw/fafb_v783/proofread_connections_783.feather")
NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]

neuron_outputs = defaultdict(lambda: [0.0]*6)
eb_edges = {}

with open(FILE_PATH, "rb") as f:
    reader = ipc.RecordBatchFileReader(f)
    for i in range(reader.num_record_batches):
        batch = reader.get_record_batch(i)
        pre_arr = batch.column("pre_pt_root_id")
        post_arr = batch.column("post_pt_root_id")
        syn_arr = batch.column("syn_count")
        np_arr = batch.column("neuropil")
        ach_arr = batch.column("ach_avg")
        gaba_arr = batch.column("gaba_avg")
        glut_arr = batch.column("glut_avg")
        da_arr = batch.column("da_avg")
        oct_arr = batch.column("oct_avg")
        ser_arr = batch.column("ser_avg")

        for j in range(batch.num_rows):
            pre = pre_arr[j].as_py()
            post = post_arr[j].as_py()
            syn = syn_arr[j].as_py()
            if pre == post:
                continue

            v_ach = ach_arr[j].as_py()
            if v_ach is not None:
                v_g = gaba_arr[j].as_py()
                v_gl = glut_arr[j].as_py()
                v_d = da_arr[j].as_py()
                v_o = oct_arr[j].as_py()
                v_se = ser_arr[j].as_py()

                neuron_outputs[pre][0] += syn * v_ach
                neuron_outputs[pre][1] += syn * v_g
                neuron_outputs[pre][2] += syn * v_gl
                neuron_outputs[pre][3] += syn * v_d
                neuron_outputs[pre][4] += syn * v_o
                neuron_outputs[pre][5] += syn * v_se

                if np_arr[j].as_py() == "EB":
                    pair = (pre, post)
                    if pair not in eb_edges:
                        eb_edges[pair] = syn
                    else:
                        eb_edges[pair] += syn

# Consensus NT and confidence
neuron_nt = {}
neuron_conf = {}
for nid, probs in neuron_outputs.items():
    s = sum(probs)
    if s > 0:
        norm = [p / s for p in probs]
        top_p = max(norm)
        neuron_nt[nid] = int(norm.index(top_p))
        neuron_conf[nid] = float(top_p)

# Filter edges at w >= 5
valid_edges = {k: w for k, w in eb_edges.items() if w >= 5 and k[0] in neuron_nt and k[1] in neuron_nt}
active_nodes = sorted(list(set(u for u, v in valid_edges.keys()) | set(v for u, v in valid_edges.keys())))

# Compute node in-degree, out-degree, mutual degree within EB w >= 5
in_deg = Counter(v for u, v in valid_edges.keys())
out_deg = Counter(u for u, v in valid_edges.keys())
edge_set = set(valid_edges.keys())
mutual_dyads = [(u, v) for u, v in valid_edges.keys() if u < v and (v, u) in edge_set]
m_deg = Counter()
for u, v in mutual_dyads:
    m_deg[u] += 1
    m_deg[v] += 1

print(f"Total EB Active Nodes: {len(active_nodes)}")
print(f"Total EB Valid Edges (w>=5): {len(valid_edges)}")
print(f"Total EB Mutual Dyads (w>=5): {len(mutual_dyads)}")

# Group by NT class
nt_counts = Counter(NT_CLASSES[neuron_nt[n]] for n in active_nodes)
print("\nNT Class Prevalence:")
for nt, cnt in nt_counts.most_common():
    print(f"  {nt.upper():5s}: {cnt:3d} ({cnt/len(active_nodes)*100:.1f}%)")

print("\nCovariates by NT Class (Mean [Min, Median, Max]):")
for nt in ["gaba", "ach", "glut", "da", "ser"]:
    sub = [n for n in active_nodes if NT_CLASSES[neuron_nt[n]] == nt]
    if not sub:
        continue
    m_vals = [m_deg[n] for n in sub]
    in_vals = [in_deg[n] for n in sub]
    out_vals = [out_deg[n] for n in sub]
    conf_vals = [neuron_conf[n] for n in sub]

    m_mean = sum(m_vals)/len(sub)
    in_mean = sum(in_vals)/len(sub)
    out_mean = sum(out_vals)/len(sub)
    c_mean = sum(conf_vals)/len(sub)

    print(f"--- {nt.upper()} (N={len(sub)}) ---")
    print(f"  Mutual Degree : mean={m_mean:5.1f}, min={min(m_vals):2d}, med={sorted(m_vals)[len(sub)//2]:2d}, max={max(m_vals):2d}")
    print(f"  In-Degree     : mean={in_mean:5.1f}, min={min(in_vals):2d}, med={sorted(in_vals)[len(sub)//2]:2d}, max={max(in_vals):2d}")
    print(f"  Out-Degree    : mean={out_mean:5.1f}, min={min(out_vals):2d}, med={sorted(out_vals)[len(sub)//2]:2d}, max={max(out_vals):2d}")
    print(f"  Confidence    : mean={c_mean:5.3f}, min={min(conf_vals):5.3f}, med={sorted(conf_vals)[len(sub)//2]:5.3f}, max={max(conf_vals):5.3f}")

# Save these pre-computed covariates to a JSON so we can quickly experiment without re-reading the 850 MB file!
node_data = {}
for n in active_nodes:
    node_data[str(n)] = {
        "nt": neuron_nt[n],
        "nt_name": NT_CLASSES[neuron_nt[n]],
        "conf": round(neuron_conf[n], 4),
        "m_deg": m_deg[n],
        "in_deg": in_deg[n],
        "out_deg": out_deg[n],
        "tot_deg": in_deg[n] + out_deg[n],
    }

out_cache = Path("results/real_data_pilot/phase7/eb_node_covariates.json")
out_cache.parent.mkdir(parents=True, exist_ok=True)
with open(out_cache, "w") as f:
    json.dump({
        "active_nodes": active_nodes,
        "mutual_dyads": mutual_dyads,
        "nodes": node_data
    }, f, indent=2)

print(f"\nSaved node covariates cache to: {out_cache}")

