#!/usr/bin/env python3
"""
Generate publication-grade vector graphics (SVG) for Phase 6 Central Complex Connectomics Study.

Produces:
1. results/real_data_pilot/phase6/figure1_conditional_composition.svg
   - Primary comparison of observed mutual dyad counts against degree-stratified conditional null (with 95% CI).
2. results/real_data_pilot/phase6/figure2_topological_vs_chemical_null.svg
   - Methodological decoupling: Tier 1 Edge-Swap Topological Null vs Tier 2 Conditional Degree-Stratified Null.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE6_DIR = PROJECT_ROOT / "results" / "real_data_pilot" / "phase6"
RESULTS_JSON = PHASE6_DIR / "phase6_controlled_study_results.json"
MCMC_JSON = PROJECT_ROOT / "results" / "real_data_pilot" / "central_complex_degree_preserving_null.json"


def generate_figure1_svg(data: dict, out_path: Path) -> None:
    """Figure 1: Observed vs Conditional Null (95% CI) for Major Motifs in EB, FB, PB."""
    # Selected key motifs
    panels = [
        {
            "region": "Ellipsoid Body (EB, w >= 5)",
            "total_m": data["regional_statistical_results"]["EB"]["w5"]["mutual_dyads"],
            "motifs": [
                ("gaba_gaba", "GABA ↔ GABA (Primary)", "#43a047"),
                ("ach_ach", "ACh ↔ ACh", "#1e88e5"),
                ("ach_gaba", "ACh ↔ GABA", "#e53935"),
                ("ach_glut", "ACh ↔ Glut", "#8e24aa"),
            ],
            "stats": data["regional_statistical_results"]["EB"]["w5"]["pair_statistics"],
        },
        {
            "region": "Fan-Shaped Body (FB, w >= 5)",
            "total_m": data["regional_statistical_results"]["FB"]["w5"]["mutual_dyads"],
            "motifs": [
                ("ach_gaba", "ACh ↔ GABA (Sec 1)", "#e53935"),
                ("ach_glut", "ACh ↔ Glut", "#8e24aa"),
                ("ach_ach", "ACh ↔ ACh", "#1e88e5"),
                ("da_ser", "DA ↔ Ser", "#fb8c00"),
            ],
            "stats": data["regional_statistical_results"]["FB"]["w5"]["pair_statistics"],
        },
        {
            "region": "Protocerebral Bridge (PB, w >= 5)",
            "total_m": data["regional_statistical_results"]["PB"]["w5"]["mutual_dyads"],
            "motifs": [
                ("glut_glut", "Glut ↔ Glut", "#00897b"),
                ("ach_ach", "ACh ↔ ACh (Sec 2)", "#1e88e5"),
                ("ach_glut", "ACh ↔ Glut", "#8e24aa"),
            ],
            "stats": data["regional_statistical_results"]["PB"]["w5"]["pair_statistics"],
        },
    ]

    width, height = 980, 680
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<style>',
        '  .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 18px; font-weight: bold; fill: #111; }',
        '  .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #555; }',
        '  .panel-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #222; }',
        '  .axis-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; fill: #666; }',
        '  .bar-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; font-weight: 500; fill: #333; }',
        '  .stat-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; font-weight: bold; fill: #222; }',
        '  .legend { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; fill: #444; }',
        '</style>',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        '<!-- Header -->',
        '<text x="40" y="38" class="title">Figure 1: Reciprocal Transmitter-Pair Composition under Conditional Null Model</text>',
        '<text x="40" y="58" class="subtitle">Empirical mutual dyad counts vs Degree-Stratified Conditional Null (B = 2,000 permutations, 95% CI) across EB, FB, and PB (w ≥ 5)</text>',
    ]

    # Legend
    svg.append('<!-- Legend -->')
    svg.append('<rect x="580" y="25" width="16" height="12" fill="#2b5c8f" rx="2" />')
    svg.append('<text x="602" y="35" class="legend">Observed Dyad Count</text>')
    svg.append('<rect x="740" y="25" width="16" height="12" fill="#e0e0e0" stroke="#777" stroke-width="1" rx="2" />')
    svg.append('<text x="762" y="35" class="legend">Conditional Null Mean (± 95% CI)</text>')

    y_offset = 95
    panel_height = 175

    for p_idx, p in enumerate(panels):
        svg.append(f'<!-- Panel {p_idx+1}: {p["region"]} -->')
        svg.append(f'<line x1="40" y1="{y_offset}" x2="940" y2="{y_offset}" stroke="#eee" stroke-width="1" />')
        svg.append(f'<text x="40" y="{y_offset + 22}" class="panel-title">{p["region"]} — Total Reciprocal Dyads: {p["total_m"]:,}</text>')

        # Determine scaling for this panel
        max_val = max(max(p["stats"][k]["observed"], p["stats"][k]["null_mean"]) for k, _, _ in p["motifs"]) * 1.25
        chart_x = 220
        chart_w = 480
        row_y = y_offset + 42

        for k, label, color in p["motifs"]:
            st = p["stats"][k]
            obs = st["observed"]
            null_m = st["null_mean"]
            q025 = st["quantiles"]["q025"]
            q975 = st["quantiles"]["q975"]
            enr = st["enrichment_ratio"]
            z = st["z_score"]
            p_val = st["empirical_p_value"]

            # Bar coordinates
            obs_w = (obs / max_val) * chart_w
            null_w = (null_m / max_val) * chart_w
            ci_x1 = chart_x + (q025 / max_val) * chart_w
            ci_x2 = chart_x + (q975 / max_val) * chart_w

            # Label
            svg.append(f'<text x="210" y="{row_y + 16}" text-anchor="end" class="bar-label">{label}</text>')

            # Null bar (gray)
            svg.append(f'<rect x="{chart_x}" y="{row_y}" width="{null_w:.1f}" height="10" fill="#e2e8f0" stroke="#cbd5e1" rx="2" />')
            # 95% CI error bar on null
            svg.append(f'<line x1="{ci_x1:.1f}" y1="{row_y + 5}" x2="{ci_x2:.1f}" y2="{row_y + 5}" stroke="#475569" stroke-width="1.5" />')
            svg.append(f'<line x1="{ci_x1:.1f}" y1="{row_y + 2}" x2="{ci_x1:.1f}" y2="{row_y + 8}" stroke="#475569" stroke-width="1.5" />')
            svg.append(f'<line x1="{ci_x2:.1f}" y1="{row_y + 2}" x2="{ci_x2:.1f}" y2="{row_y + 8}" stroke="#475569" stroke-width="1.5" />')

            # Observed bar (colored)
            svg.append(f'<rect x="{chart_x}" y="{row_y + 12}" width="{obs_w:.1f}" height="12" fill="{color}" rx="2" />')

            # Statistics label
            enr_str = f"{enr:.2f}x"
            sig_marker = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "n.s."))
            stat_str = f"Obs: {obs:,} | Null: {null_m:,.1f} | {enr_str} (Z = {z:+.1f}, {sig_marker})"
            svg.append(f'<text x="{chart_x + max(obs_w, null_w) + 12}" y="{row_y + 19}" class="stat-text">{stat_str}</text>')

            row_y += 28

        y_offset += panel_height

    # Footer note
    svg.append(f'<text x="40" y="{height - 20}" class="subtitle">* p &lt; 0.05, ** p &lt; 0.01, *** p &lt; 0.001 (Empirical 2-tailed finite-sample p-value, B = 2,000 permutations). Reciprocal topology M held strictly constant.</text>')
    svg.append('</svg>')

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(svg))
    print(f"Generated Figure 1: {out_path}")


def generate_figure2_svg(data: dict, out_path: Path) -> None:
    """Figure 2: Methodological Decoupling — Topological Edge Swaps vs Conditional Null."""
    width, height = 980, 560
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<style>',
        '  .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 18px; font-weight: bold; fill: #111; }',
        '  .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #555; }',
        '  .col-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #1e3a8a; }',
        '  .box-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #222; }',
        '  .metric { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #333; }',
        '  .highlight { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #b91c1c; }',
        '  .caption { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 11px; fill: #475569; }',
        '</style>',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        '<!-- Header -->',
        '<text x="40" y="38" class="title">Figure 2: Decoupling Overall Reciprocity from Chemical Transmitter Selectivity</text>',
        '<text x="40" y="58" class="subtitle">Why Degree-Preserving Edge Swaps artificially inflate GABA-GABA Z-scores from +15 to +125 in the Ellipsoid Body (w ≥ 5)</text>',
    ]

    # Two Main Panels Side by Side
    col_w = 425
    y0 = 85

    # LEFT PANEL: Tier 1 Edge-Swap Topological Null
    svg.append(f'<!-- Left Panel -->')
    svg.append(f'<rect x="40" y="{y0}" width="{col_w}" height="410" fill="#f8fafc" stroke="#cbd5e1" rx="8" />')
    svg.append(f'<text x="60" y="{y0 + 30}" class="col-title">Tier 1: Topological MCMC Edge-Swap Null</text>')
    svg.append(f'<text x="60" y="{y0 + 50}" class="caption">Preserves in/out-degrees; randomizes directed connections.</text>')

    # Box 1: Topology Suppression
    svg.append(f'<rect x="60" y="{y0 + 70}" width="{col_w - 40}" height="100" fill="#ffffff" stroke="#e2e8f0" rx="6" />')
    svg.append(f'<text x="75" y="{y0 + 95}" class="box-title">Effect on Reciprocal Dyad Count (M)</text>')
    svg.append(f'<text x="75" y="{y0 + 120}" class="metric">• Empirical Mutual Dyads: <tspan font-weight="bold">3,518</tspan> (R_edge = 44.5%)</text>')
    svg.append(f'<text x="75" y="{y0 + 140}" class="metric">• Edge-Swap Null M: <tspan font-weight="bold">763.4 ± 22.0</tspan> (R_edge ≈ 9.7%)</text>')
    svg.append(f'<text x="75" y="{y0 + 160}" class="highlight">Result: 4.61× collapse of reciprocal topology</text>')

    # Box 2: Confounded Motif Result
    svg.append(f'<rect x="60" y="{y0 + 185}" width="{col_w - 40}" height="185" fill="#ffffff" stroke="#e2e8f0" rx="6" />')
    svg.append(f'<text x="75" y="{y0 + 210}" class="box-title">Confounded EB GABA ↔ GABA Metric</text>')
    svg.append(f'<text x="75" y="{y0 + 235}" class="metric">• Observed GABA ↔ GABA: <tspan font-weight="bold">2,615</tspan></text>')
    svg.append(f'<text x="75" y="{y0 + 255}" class="metric">• Edge-Swap Null Mean: <tspan font-weight="bold">385.9 ± 17.7</tspan></text>')
    svg.append(f'<text x="75" y="{y0 + 280}" class="metric">• Apparent Raw Enrichment: <tspan font-weight="bold" fill="#b91c1c">6.78×</tspan></text>')
    svg.append(f'<text x="75" y="{y0 + 305}" class="metric">• Apparent Z-Score: <tspan font-weight="bold" fill="#b91c1c">Z = +125.7</tspan></text>')
    svg.append(f'<text x="75" y="{y0 + 340}" class="caption">⚠️ Conflates 4.6× excess loops with chemical preference.</text>')
    svg.append(f'<text x="75" y="{y0 + 355}" class="caption">    In rewired graph, GABA-GABA is already 50.5% of M.</text>')

    # RIGHT PANEL: Tier 2 Conditional Degree-Stratified Null
    svg.append(f'<!-- Right Panel -->')
    x_r = 515
    svg.append(f'<rect x="{x_r}" y="{y0}" width="{col_w}" height="410" fill="#f0fdf4" stroke="#bbf7d0" rx="8" />')
    svg.append(f'<text x="{x_r + 20}" y="{y0 + 30}" class="col-title" fill="#15803d">Tier 2: Conditional Degree-Stratified Null</text>')
    svg.append(f'<text x="{x_r + 20}" y="{y0 + 50}" class="caption">Holds empirical mutual dyads constant; permutes labels by degree.</text>')

    # Box 1: Topology Preservation
    svg.append(f'<rect x="{x_r + 20}" y="{y0 + 70}" width="{col_w - 40}" height="100" fill="#ffffff" stroke="#dcfce7" rx="6" />')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 95}" class="box-title">Preservation of Empirical Topology</text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 120}" class="metric">• Empirical Mutual Dyads: <tspan font-weight="bold">3,518</tspan> (Fixed)</text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 140}" class="metric">• Conditional Null M: <tspan font-weight="bold">3,518</tspan> (Exact Match, 100%)</text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 160}" class="stat-text" fill="#15803d">✓ Zero topology confounding: tests chemical pairing alone</text>')

    # Box 2: Isolated Chemical Selectivity
    svg.append(f'<rect x="{x_r + 20}" y="{y0 + 185}" width="{col_w - 40}" height="185" fill="#ffffff" stroke="#dcfce7" rx="6" />')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 210}" class="box-title">Isolated EB GABA ↔ GABA Pairing</text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 235}" class="metric">• Observed GABA ↔ GABA: <tspan font-weight="bold">2,615</tspan> (74.33% of M)</text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 255}" class="metric">• Stratified Null Mean: <tspan font-weight="bold">2,167.1 ± 29.3</tspan> (61.60% of M)</text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 280}" class="metric">• True Conditional Enrichment: <tspan font-weight="bold" fill="#15803d">1.21× (+20.7%)</tspan></text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 305}" class="metric">• Calibrated Z-Score: <tspan font-weight="bold" fill="#15803d">Z = +15.3 (p = 0.0005)</tspan></text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 340}" class="caption">✓ Connection-level probabilistic mass: 2,336.6 (66.4% of M)</text>')
    svg.append(f'<text x="{x_r + 35}" y="{y0 + 355}" class="caption">✓ Substantial, robust, but biologically moderated effect.</text>')

    # Footer note
    svg.append(f'<text x="40" y="{height - 20}" class="subtitle">Equation: Raw Ratio (6.78×) ≈ Topological Reciprocity Excess (4.61×) × Conditional Pairing Preference (1.47× naive / 1.21× stratified).</text>')
    svg.append('</svg>')

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(svg))
    print(f"Generated Figure 2: {out_path}")


def main() -> None:
    if not RESULTS_JSON.exists():
        print(f"Error: results file {RESULTS_JSON} not found!")
        sys.exit(1)

    with open(RESULTS_JSON) as f:
        data = json.load(f)

    fig1_path = PHASE6_DIR / "figure1_conditional_composition.svg"
    fig2_path = PHASE6_DIR / "figure2_topological_vs_chemical_null.svg"

    generate_figure1_svg(data, fig1_path)
    generate_figure2_svg(data, fig2_path)
    print("All Phase 6 vector figures generated successfully.")


if __name__ == "__main__":
    main()

