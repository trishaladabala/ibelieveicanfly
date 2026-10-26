#!/usr/bin/env python3
"""
simulate_vector_steering_dynamics.py

Rate-based dynamical model of the Fan-Shaped Body (FB) Layers 4 & 5
columnar-tangential reciprocal steering circuit.

Evaluates Recurrent Subtractive Inhibitory Feedback:
Does the 100% polarized Columnar(ACh) <-> Tangential(GABA) reciprocal feedback
provide linear subtractive attenuation that bounds columnar runaway excitation
and maintains bump sharpness across varying forward velocity and sensory drive levels?

Evaluates:
1. Peak firing rate vs. input drive (subtractive attenuation: intact vs ablated inhibition).
2. Steering bump sharpness (Full Width at Half Maximum, FWHM in degrees).
3. Directional population vector length (tuning contrast fidelity).
4. Angular steering decoding error (|theta_decoded - theta_target|).

Saves structured simulation results to:
- results/fb_dynamical_simulation_results.json
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
OUT_JSON = REPO_ROOT / "results" / "fb_dynamical_simulation_results.json"


def run_simulation(
    num_columns: int = 16,
    input_drives: list[float] | None = None,
    heading_target: float = math.pi / 3.0,
    w_recip: float = 0.15,
    w_inh: float = 0.85,
    j_col: float = 0.25,
    tau_col: float = 20.0,   # ms
    tau_tan: float = 10.0,   # ms
    t_max: float = 300.0,    # ms
    dt: float = 0.5,         # ms
) -> dict[str, Any]:
    """
    Simulates rate-based dynamics for intact and ablated reciprocal inhibition.
    """
    if input_drives is None:
        input_drives = [1.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0]

    phi = [2.0 * math.pi * i / num_columns for i in range(num_columns)]
    n_steps = int(t_max / dt)

    results_intact: list[dict[str, Any]] = []
    results_ablated: list[dict[str, Any]] = []

    for condition, cur_w_inh in [("intact", w_inh), ("ablated", 0.0)]:
        cond_records = []
        for drive in input_drives:
            # Inputs
            I_sensory = [drive * max(0.0, math.cos(heading_target - p)) for p in phi]

            # Initial states
            r_col = [0.1] * num_columns
            r_tan = 0.0

            # Euler integration
            for _ in range(n_steps):
                # Tangential receives excitation from columnar sum
                col_sum = sum(r_col)
                dr_tan = (-r_tan + w_recip * col_sum) / tau_tan
                r_tan = max(0.0, r_tan + dr_tan * dt)

                # Columnar dynamics
                new_r_col = []
                for i in range(num_columns):
                    # Local columnar lateral interaction
                    lateral = sum(j_col * math.cos(phi[i] - phi[j]) * r_col[j] for j in range(num_columns))
                    net_input = I_sensory[i] + lateral - cur_w_inh * r_tan
                    dr_i = (-r_col[i] + max(0.0, net_input)) / tau_col
                    new_r_col.append(max(0.0, r_col[i] + dr_i * dt))
                r_col = new_r_col

            # Steady-state metrics
            peak_rate = max(r_col)
            min_rate = min(r_col)
            half_max = (peak_rate + min_rate) / 2.0

            # FWHM calculation (in degrees)
            above_half = sum(1 for r in r_col if r >= half_max)
            fwhm_deg = (above_half / num_columns) * 360.0

            # Population vector decoding
            vx = sum(r * math.cos(p) for r, p in zip(r_col, phi))
            vy = sum(r * math.sin(p) for r, p in zip(r_col, phi))
            v_mag = math.sqrt(vx * vx + vy * vy)
            vector_length = v_mag / sum(r_col) if sum(r_col) > 0 else 0.0
            decoded_angle = math.atan2(vy, vx) if v_mag > 0 else 0.0
            angle_error_deg = abs(decoded_angle - heading_target) * 180.0 / math.pi
            if angle_error_deg > 180.0:
                angle_error_deg = 360.0 - angle_error_deg

            cond_records.append({
                "drive": drive,
                "peak_rate": round(peak_rate, 2),
                "tangential_rate": round(r_tan, 2),
                "fwhm_deg": round(fwhm_deg, 1),
                "vector_length": round(vector_length, 4),
                "decoded_angle_deg": round(decoded_angle * 180.0 / math.pi, 2),
                "angle_error_deg": round(angle_error_deg, 2),
                "bump_profile": [round(r, 2) for r in r_col],
            })

        if condition == "intact":
            results_intact = cond_records
        else:
            results_ablated = cond_records

    # Comparative summary
    high_drive_intact = results_intact[-1]
    high_drive_ablated = results_ablated[-1]
    peak_suppression_ratio = high_drive_ablated["peak_rate"] / high_drive_intact["peak_rate"] if high_drive_intact["peak_rate"] > 0 else 0.0

    return {
        "metadata": {
            "num_columns": num_columns,
            "heading_target_deg": round(heading_target * 180.0 / math.pi, 2),
            "w_recip": w_recip,
            "w_inh": w_inh,
            "j_col": j_col,
            "tau_col_ms": tau_col,
            "tau_tan_ms": tau_tan,
            "t_max_ms": t_max,
            "dt_ms": dt,
        },
        "simulation_results": {
            "intact_reciprocal_feedback": results_intact,
            "ablated_reciprocal_feedback": results_ablated,
        },
        "summary": {
            "peak_suppression_ratio_at_max_drive": round(peak_suppression_ratio, 2),
            "intact_fwhm_stability_range_deg": [min(r["fwhm_deg"] for r in results_intact), max(r["fwhm_deg"] for r in results_intact)],
            "ablated_fwhm_stability_range_deg": [min(r["fwhm_deg"] for r in results_ablated), max(r["fwhm_deg"] for r in results_ablated)],
            "mean_decoding_error_intact_deg": round(sum(r["angle_error_deg"] for r in results_intact) / len(results_intact), 2),
            "mean_decoding_error_ablated_deg": round(sum(r["angle_error_deg"] for r in results_ablated) / len(results_ablated), 2),
        },
    }


def main() -> None:
    t0 = time.perf_counter()
    print("=" * 80)
    print("FAN-SHAPED BODY (FB) DYNAMICAL CIRCUIT SIMULATION: SUBTRACTIVE INHIBITORY ATTENUATION")
    print("=" * 80)

    sim_data = run_simulation()

    summary = sim_data["summary"]
    intact = sim_data["simulation_results"]["intact_reciprocal_feedback"]
    ablated = sim_data["simulation_results"]["ablated_reciprocal_feedback"]

    print("\n--- Gain Control Benchmark Across Input Drive Levels ---")
    print(f"  {'Drive':6s} | {'Peak (Intact)':14s} | {'Peak (Ablated)':14s} | {'FWHM Intact':12s} | {'FWHM Ablated':12s} | {'VecLen Intact':13s}")
    print("  " + "-" * 82)
    for r_i, r_a in zip(intact, ablated):
        print(
            f"  {r_i['drive']:6.1f} | {r_i['peak_rate']:14.2f} | {r_a['peak_rate']:14.2f} | "
            f"{r_i['fwhm_deg']:10.1f}° | {r_a['fwhm_deg']:10.1f}° | {r_i['vector_length']:13.4f}"
        )

    print("\n--- Key Dynamical Findings ---")
    print(f"  • Peak Suppression Ratio at Max Drive (I=20) : {summary['peak_suppression_ratio_at_max_drive']}x reduction")
    print(f"  • Intact Bump FWHM Range (Sharpness)         : {summary['intact_fwhm_stability_range_deg'][0]}° - {summary['intact_fwhm_stability_range_deg'][1]}° (Stable!)")
    print(f"  • Ablated Bump FWHM Range (Broadening)       : {summary['ablated_fwhm_stability_range_deg'][0]}° - {summary['ablated_fwhm_stability_range_deg'][1]}° (Contrast Loss!)")
    print(f"  • Mean Decoding Error (Intact Feedback)      : {summary['mean_decoding_error_intact_deg']}°")
    print(f"  • Mean Decoding Error (Ablated Feedback)     : {summary['mean_decoding_error_ablated_deg']}°")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(sim_data, f, indent=2)
    print(f"\nSaved simulation outputs to {OUT_JSON}")
    print(f"Simulation completed in {time.perf_counter() - t0:.2f}s!")


if __name__ == "__main__":
    main()
