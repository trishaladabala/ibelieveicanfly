#!/usr/bin/env python3
"""
Feasibility Pilot: Directed Degree-Preserving Edge Swap (Maslov-Sneppen) on the Ellipsoid Body (EB).
Verifies:
1. Exact in-degree and out-degree sequence preservation.
2. Absence of self-loops (u == v) and duplicate edges.
3. Mixing rate (% of original edges rewired).
4. Mutual dyad formation and transmitter pairing stats.
5. Runtime and memory footprint.
"""
from __future__ import annotations
import array
from collections import Counter, defaultdict
from pathlib import Path
import random
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PATH = PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

import pyarrow.ipc as ipc

FILE_PATH = PROJECT_ROOT / "data" / "raw" / "fafb_v783" / "proofread_connections_783.feather"
NT_CLASSES = ["ach", "gaba", "glut", "da", "oct", "ser"]
NT_INDEX = {name: i for i, name in enumerate(NT_CLASSES)}

def directed_edge_swap(
    edge_list: list[tuple[int, int]],
    num_swaps: int,
    rng: random.Random,
) -> tuple[list[tuple[int, int]], int, int]:
    """
    Performs directed edge swaps preserving in-degree and out-degree of every node.
    Returns rewired edge list, successful swap count, attempted swap count.
    """
    # Bit-packed set of directed edges: (u << 32) | v
    edge_set = set((u << 32) | v for u, v in edge_list)
    edges = list(edge_list)
    E = len(edges)
    
    successful_swaps = 0
    attempted_swaps = 0
    
    for _ in range(num_swaps):
        attempted_swaps += 1
        i = rng.randrange(E)
        j = rng.randrange(E)
        if i == j:
            continue
            
        u1, v1 = edges[i]
        u2, v2 = edges[j]
        
        # Avoid self-loops
        if u1 == v2 or u2 == v1 or u1 == u2 or v1 == v2:
            continue
            
        k_new1 = (u1 << 32) | v2
        k_new2 = (u2 << 32) | v1
        
        # Avoid duplicate edges
        if k_new1 in edge_set or k_new2 in edge_set:
            continue
            
        k_old1 = (u1 << 32) | v1
        k_old2 = (u2 << 32) | v2
        
        edge_set.remove(k_old1)
        edge_set.remove(k_old2)
        edge_set.add(k_new1)
        edge_set.add(k_new2)
        
        edges[i] = (u1, v2)
        edges[j] = (u2, v1)
        successful_swaps += 1
        
    return edges, successful_swaps, attempted_swaps

def count_mutual_motifs(
    edge_list: list[tuple[int, int]],
    neuron_nt: dict[int, int],
) -> tuple[int, Counter[str]]:
    """Counts mutual dyads and categorizes them by transmitter pair."""
    edge_set = set((u << 32) | v for u, v in edge_list)
    mutual_dyads = 0
    pair_counts: Counter[str] = Counter()
    
    for u, v in edge_list:
        if u < v:
            rev_k = (v << 32) | u
            if rev_k in edge_set:
                nt_u = neuron_nt.get(u, -1)
                nt_v = neuron_nt.get(v, -1)
                if 0 <= nt_u < 6 and 0 <= nt_v < 6:
                    mutual_dyads += 1
                    c1, c2 = min(nt_u, nt_v), max(nt_u, nt_v)
                    p_name = f"{NT_CLASSES[c1]}_{NT_CLASSES[c2]}"
                    pair_counts[p_name] += 1
                    
    return mutual_dyads, pair_counts

def main():
    print("================================================================================")
    print("FEASIBILITY PILOT: DEGREE-PRESERVING DIRECTED EDGE SWAP ON ELLIPSOID BODY (EB)")
    print("================================================================================")
    t0 = time.perf_counter()
    
    # 1. Ingest EB edges and derive whole-connectome consensus transmitter per neuron
    eb_edges_w: dict[tuple[int, int], int] = defaultdict(int)
    neuron_out_mass: dict[int, list[float]] = defaultdict(lambda: [0.0]*6)
    
    with open(FILE_PATH, "rb") as f:
        reader = ipc.open_file(f)
        for b in range(reader.num_record_batches):
            batch = reader.get_batch(b)
            npils = batch.column("neuropil").to_pylist()
            pres = batch.column("pre_pt_root_id").to_pylist()
            posts = batch.column("post_pt_root_id").to_pylist()
            weights = batch.column("syn_count").to_pylist()
            
            # Extract NT probs if present
            nt_cols = [batch.column(f"{nt}_avg").to_pylist() for nt in NT_CLASSES]
            
            for i, (p, q, w, r) in enumerate(zip(pres, posts, weights, npils)):
                if p is None or q is None or w is None or w <= 0 or p == q:
                    continue
                # Accumulate EB edges
                if r == "EB":
                    eb_edges_w[(p, q)] += w
                # Accumulate whole-brain outgoing NT mass
                p_nt = [col[i] for col in nt_cols]
                if all(v is not None for v in p_nt):
                    m = neuron_out_mass[p]
                    for c in range(6):
                        m[c] += w * p_nt[c]
                        
    # Consensus phenotype
    neuron_nt: dict[int, int] = {}
    for n, mass in neuron_out_mass.items():
        best_c = 0
        best_m = mass[0]
        for c in range(1, 6):
            if mass[c] > best_m:
                best_m = mass[c]
                best_c = c
        if sum(mass) > 0:
            neuron_nt[n] = best_c
            
    ingest_time = time.perf_counter() - t0
    print(f"Data ingestion complete in {ingest_time:.2f}s.")
    
    # Test at threshold w >= 3 (standard robust microcircuit threshold for EB)
    for t in [1, 3, 5]:
        raw_edges = [k for k, w in eb_edges_w.items() if w >= t and k[0] in neuron_nt and k[1] in neuron_nt]
        E = len(raw_edges)
        nodes = set(k[0] for k in raw_edges) | set(k[1] for k in raw_edges)
        V = len(nodes)
        
        orig_in = Counter(v for u, v in raw_edges)
        orig_out = Counter(u for u, v in raw_edges)
        
        obs_m, obs_pairs = count_mutual_motifs(raw_edges, neuron_nt)
        print(f"\n--- EB (w >= {t}): {V} nodes, {E} edges, {obs_m} empirical mutual dyads ---")
        print(f"  Observed Key Motifs:")
        for m_name in ["gaba_gaba", "ach_gaba", "ach_ach", "glut_glut", "gaba_glut"]:
            print(f"    {m_name:10s}: {obs_pairs.get(m_name, 0):4d} ({obs_pairs.get(m_name, 0)/obs_m*100:5.1f}%)" if obs_m > 0 else "")
            
        # Test edge swap mixing across multipliers
        rng = random.Random(42)
        for mult in [1, 5, 10, 20]:
            target_swaps = mult * E
            t_swap_start = time.perf_counter()
            rewired_edges, succ, att = directed_edge_swap(raw_edges, target_swaps, rng)
            swap_time = time.perf_counter() - t_swap_start
            
            # Verify degree sequence
            rew_in = Counter(v for u, v in rewired_edges)
            rew_out = Counter(u for u, v in rewired_edges)
            assert orig_in == rew_in, "In-degree violated!"
            assert orig_out == rew_out, "Out-degree violated!"
            assert len(set(rewired_edges)) == len(rewired_edges), "Duplicates generated!"
            assert all(u != v for u, v in rewired_edges), "Self-loops generated!"
            
            # Measure mixing fraction (% of original edges changed)
            orig_set = set(raw_edges)
            rew_set = set(rewired_edges)
            retained = len(orig_set & rew_set)
            rewired_frac = 1.0 - (retained / E)
            
            rew_m, rew_pairs = count_mutual_motifs(rewired_edges, neuron_nt)
            print(f"  Multiplier {mult:2d}x ({att:,} attempts, {succ:,} succ in {swap_time*1000:6.1f}ms): "
                  f"Rewired {rewired_frac*100:5.1f}% | Null Mutual Dyads: {rew_m:4d} (GABA-GABA: {rew_pairs.get('gaba_gaba', 0)})")

if __name__ == "__main__":
    main()

