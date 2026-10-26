import sys
from pathlib import Path
sys.path.insert(0, str(Path("scripts").resolve()))
from run_phase6_controlled_study import benjamini_hochberg
import json

with open("results/real_data_pilot/phase6/phase6_controlled_study_results.json") as f:
    d = json.load(f)

# Collect all p-values across all 3 regions at w >= 5 (63 tests)
p_all_w5 = []
labels_w5 = []
for r in ["EB", "FB", "PB"]:
    pairs = d["regional_statistical_results"][r]["w5"]["pair_statistics"]
    for p, stats in pairs.items():
        p_all_w5.append(stats["empirical_p_value"])
        labels_w5.append((r, "w5", p, stats["observed"], stats["null_mean"], stats["enrichment_ratio"], stats["z_score"]))

q_all_w5 = benjamini_hochberg(p_all_w5)

print("=== GLOBAL FDR ACROSS ALL 63 PAIRS AT w >= 5 ===")
for (r, w, p, obs, nm, enr, z), p_val, q_glob in zip(labels_w5, p_all_w5, q_all_w5):
    local_q = d["regional_statistical_results"][r]["w5"]["pair_statistics"][p]["fdr_q_value"]
    if q_glob < 0.05 or local_q < 0.05:
        print(f"  {r:2s} {p:12s}: Obs={obs:4d}, Null={nm:7.2f}, Enr={enr:5.2f}x, Z={z:+5.1f}, p={p_val:.6f} | Local q={local_q:.6f} | Global q={q_glob:.6f}")

# Collect all 126 tests across w >= 3 and w >= 5
p_all_126 = []
labels_126 = []
for r in ["EB", "FB", "PB"]:
    for w in ["w3", "w5"]:
        pairs = d["regional_statistical_results"][r][w]["pair_statistics"]
        for p, stats in pairs.items():
            p_all_126.append(stats["empirical_p_value"])
            labels_126.append((r, w, p, stats["observed"], stats["null_mean"], stats["enrichment_ratio"], stats["z_score"]))

q_all_126 = benjamini_hochberg(p_all_126)
print("\n=== GLOBAL FDR ACROSS ALL 126 PAIRS (w3 + w5) ===")
for (r, w, p, obs, nm, enr, z), p_val, q_126 in zip(labels_126, p_all_126, q_all_126):
    local_q = d["regional_statistical_results"][r][w]["pair_statistics"][p]["fdr_q_value"]
    if q_126 < 0.05 or local_q < 0.05:
        print(f"  {r:2s} {w:2s} {p:12s}: Obs={obs:4d}, Null={nm:7.2f}, Enr={enr:5.2f}x, Z={z:+5.1f}, p={p_val:.6f} | Local q={local_q:.6f} | Global q(126)={q_126:.6f}")

