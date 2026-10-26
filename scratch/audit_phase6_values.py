import json
from pathlib import Path

results_path = Path("results/real_data_pilot/phase6/phase6_controlled_study_results.json")
with open(results_path) as f:
    d = json.load(f)

print("=== AUDIT SUMMARY IN JSON ===")
print(d.get("audit_summary"))

print("\n=== PRIMARY OUTCOME IN JSON ===")
print(d.get("primary_outcome"))

eb_w5 = d["regional_statistical_results"]["EB"]["w5"]
print("\n=== EB w5 Summary ===")
print("Active nodes:", eb_w5["active_nodes"])
print("Directed edges:", eb_w5["directed_edges"])
print("Mutual dyads:", eb_w5["mutual_dyads"])
print("Reciprocity edge pct:", eb_w5["reciprocity_edge_pct"])
print("Connection-level prob masses (sum and gaba_gaba):")
print("  gaba_gaba prob mass:", eb_w5["connection_level_prob_masses"].get("gaba_gaba"))
prob_sum = sum(eb_w5["connection_level_prob_masses"].values())
print("  total prob mass sum across 21 pairs:", prob_sum)

pairs = eb_w5["pair_statistics"]
obs_sum = sum(v["observed"] for v in pairs.values())
null_mean_sum = sum(v["null_mean"] for v in pairs.values())
print(f"Sum of observed dyads across 21 pairs: {obs_sum} (Matches mutual_dyads?: {obs_sum == eb_w5['mutual_dyads']})")
print(f"Sum of null means across 21 pairs: {null_mean_sum:.2f} (Matches mutual_dyads?: {abs(null_mean_sum - eb_w5['mutual_dyads']) < 1e-1})")

print("\nEB w5 Key Pairs:")
for k in ["gaba_gaba", "ach_gaba", "ach_ach", "ach_glut", "gaba_glut", "gaba_ser"]:
    v = pairs[k]
    obs = v['observed']
    nm = v['null_mean']
    std = v['null_std']
    enr = v['enrichment_ratio']
    z = v['z_score']
    p = v['empirical_p_value']
    q = v['fdr_q_value']
    print(f"  {k:12s}: obs={obs:4d}, null_mean={nm:7.2f}, std={std:5.2f}, enr={enr:6.4f}, z={z:+6.2f}, p={p:.6f}, q={q:.6f}")

fb_w5 = d["regional_statistical_results"]["FB"]["w5"]
print("\n=== FB w5 Summary ===")
print("Active nodes:", fb_w5["active_nodes"])
print("Directed edges:", fb_w5["directed_edges"])
print("Mutual dyads:", fb_w5["mutual_dyads"])
fb_pairs = fb_w5["pair_statistics"]
fb_obs_sum = sum(v["observed"] for v in fb_pairs.values())
fb_null_sum = sum(v["null_mean"] for v in fb_pairs.values())
print(f"Sum of observed dyads across 21 pairs: {fb_obs_sum} (Matches mutual_dyads?: {fb_obs_sum == fb_w5['mutual_dyads']})")
print(f"Sum of null means across 21 pairs: {fb_null_sum:.2f} (Matches mutual_dyads?: {abs(fb_null_sum - fb_w5['mutual_dyads']) < 1e-1})")
for k in ["ach_gaba", "ach_ach", "ach_glut", "da_ser", "da_da"]:
    v = fb_pairs[k]
    obs = v['observed']
    nm = v['null_mean']
    std = v['null_std']
    enr = v['enrichment_ratio']
    z = v['z_score']
    p = v['empirical_p_value']
    q = v['fdr_q_value']
    print(f"  {k:12s}: obs={obs:4d}, null_mean={nm:7.2f}, std={std:5.2f}, enr={enr:6.4f}, z={z:+6.2f}, p={p:.6f}, q={q:.6f}")

pb_w5 = d["regional_statistical_results"]["PB"]["w5"]
print("\n=== PB w5 Summary ===")
print("Active nodes:", pb_w5["active_nodes"])
print("Directed edges:", pb_w5["directed_edges"])
print("Mutual dyads:", pb_w5["mutual_dyads"])
pb_pairs = pb_w5["pair_statistics"]
pb_obs_sum = sum(v["observed"] for v in pb_pairs.values())
pb_null_sum = sum(v["null_mean"] for v in pb_pairs.values())
print(f"Sum of observed dyads across 21 pairs: {pb_obs_sum} (Matches mutual_dyads?: {pb_obs_sum == pb_w5['mutual_dyads']})")
print(f"Sum of null means across 21 pairs: {pb_null_sum:.2f} (Matches mutual_dyads?: {abs(pb_null_sum - pb_w5['mutual_dyads']) < 1e-1})")
for k in ["ach_ach", "glut_glut", "ach_glut"]:
    v = pb_pairs[k]
    obs = v['observed']
    nm = v['null_mean']
    std = v['null_std']
    enr = v['enrichment_ratio']
    z = v['z_score']
    p = v['empirical_p_value']
    q = v['fdr_q_value']
    print(f"  {k:12s}: obs={obs:4d}, null_mean={nm:7.2f}, std={std:5.2f}, enr={enr:6.4f}, z={z:+6.2f}, p={p:.6f}, q={q:.6f}")

print("\n=== SENSITIVITY CHECKS IN JSON ===")
print(json.dumps(d.get("sensitivity_checks"), indent=2))

