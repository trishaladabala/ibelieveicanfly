# Phase 6.1 Checkpoint: Statistical Audit, Reproducibility, & Claim Calibration

**Project**: "I Believe I Can Fly" — Adult *Drosophila melanogaster* Connectomics  
**Repository**: `/home/trishal/ibelieveicanfly`  
**Current Phase**: Phase 6.1 Completed (Statistical Audit, Reproducibility & Claim Calibration)  
**Current Task**: Audit Report Delivered (`docs/phase6_1_audit.md`); Standing By for Decision  
**Last Checkpoint Timestamp**: 2026-10-20 09:00:00 IST  

---

## 1. Completed Work in Phase 6.1
1. **Step 1: Preserve and Inspect**:
   - Inspected git status, working tree, and recent commit history.
   - Recorded SHA-256 hashes of all 15 key scripts, result JSONs, docs, and figures.
2. **Step 2: Reproduce the Reported Numbers**:
   - Reconciled all reported quantities across EB, FB, and PB.
   - Reconciled the 24 directed edges / 7 mutual dyads in FB ($46,903$ vs $46,927$ edges; $5,435$ vs $5,442$ dyads; $554$ vs $555$ ACh-GABA) resulting from non-null local NT prediction requirements.
   - Verified that all 21 pair categories sum to exactly the total mutual dyads in EB ($3,518$), FB ($5,435$), and PB ($137$).
3. **Step 3: Audit the Conditional Null**:
   - Fully documented the conditional null mechanism: empirical mutual dyads ($M$) are held 100% constant; discrete whole-cell consensus labels are shuffled within 4 mutual-degree quartiles.
   - Clarified that the method preserves **coarse mutual-degree quartiles**, NOT exact directed in/out-degree sequences.
   - Confirmed that degree stratification elevates the null mean from $1,337.8 \to 2,167.11$, moderating the true conditional enrichment to $+20.7\%$ ($Z = +15.28$).
4. **Step 4: Audit Rewiring and Monte Carlo Statistics**:
   - Validated MCMC edge-swap mixing diagnostics (invariants, acceptance rates, trajectory plateaus by $5\times |E|$, low autocorrelation $\tau_{\text{int}} \le 0.63$, and multi-seed stability).
   - Recomputed Benjamini-Hochberg FDR adjustments locally ($m = 21$) and globally ($m = 63$ and $m = 126$), confirming that all significant findings remain invariant.
   - Interpreted empirical $p = 0.000500$ as the finite-sample resolution limit ($p \le 1/2001$) under $B = 2,000$ permutations.
5. **Step 5: Audit Transmitter Labels**:
   - Distinguished hard consensus labels, connection-level probabilities, probability-weighted dyad mass ($2,336.57$), and physiological effects.
   - Audited the high-confidence EB filter ($\ge 0.80$): $270$ neurons and $2,313$ mutual dyads remain ($65.75\%$), of which $94.29\%$ are GABA–GABA.
6. **Step 6: Calibrate Scientific Claims**:
   - Explicitly classified all primary and secondary claims (Supported by Audited Analysis, Supported under Specific Assumptions / Exploratory, Not Supported).
   - Retracted all "first-ever" or biological novelty claims.
   - Documented PB ACh–ACh depletion as non-significant ($Z = -1.59, p = 0.097, q = 0.976$).
7. **Step 7: Deliver Decision Report**:
   - Authored official audit decision report: `docs/phase6_1_audit.md`.
   - Updated `docs/phase6_final_report.md` with calibrated statements and reconciliations.
   - Executed full automated unit test suite: **22/22 tests passing in 0.099s**.

---

## 2. Key Checksums Verified in Audit

| File Path | SHA-256 Checksum |
|---|---|
| `docs/phase6_1_audit.md` | `a2ba12156d6c82c2533aabb7de12ee1882fd8cd7223eab54dfca2e23b9314ed8` |
| `docs/phase6_final_report.md` | `ec97d377b3b3bf7b1899e0750e50153315a6b07d6d370e060012e841fe73bf20` |
| `scripts/run_phase6_controlled_study.py` | `cdd3718d622049c0b1c2fd7b11fffa29b5901c45e376ae0135ac57096a68af5c` |
| `results/real_data_pilot/phase6/phase6_controlled_study_results.json` | `0ecb390aad40872bcbf2da70c24295fdbce628c71724986a5357d36b1d2a5d1b` |
| `tests/test_preliminary_analysis.py` | `0afb91be2c77b6cd65b03078b303fbd51344b47d672b96af4b0072f0b041f4b9` |

---

## 3. Explicit Stop State
All Phase 6.1 audit mandates are fulfilled. In accordance with instructions, execution stops here. No further biological analyses or expensive pipeline reruns are initiated without explicit user instruction.
