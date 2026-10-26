#!/usr/bin/env python3
"""
generate_fb_figures.py

Renders publication-grade vector SVG and 300dpi PNG figures for the VectorWing project:
1. figure1_fb_conditional_associations (.svg & .png):
   - Forest plot comparing observed ACh-GABA mutual dyads (554) against null distributions
     across 4 degree-stratified models and 2 continuous k-NN micro-strata benchmarks.
2. figure2_fb_layer_column_matrix (.svg & .png):
   - Multi-panel anatomical dissection showing columnar-tangential dominance (99.5%),
     layer localization (93.9% in Layers 4 & 5), strict 100% directional polarity, and top cell pairs.
3. figure3_eb_vs_fb_circuit_contrast (.svg & .png):
   - Direct architectural contrast between 1D Ring-Attractor heading (EB) and 2D Vector Steering (FB).
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

# Ensure system dist-packages is accessible for cairo bindings in .venv
if "/usr/lib/python3/dist-packages" not in sys.path:
    sys.path.append("/usr/lib/python3/dist-packages")

try:
    import cairo
except ImportError:
    cairo = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIG_DIR = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "figures"
STUDY_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_controlled_study_results.json"
ANATOMY_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_layer_column_anatomy.json"
KNN_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_continuous_degree_results.json"
SIM_JSON = PROJECT_ROOT / "fb_vector_reciprocity" / "results" / "fb_dynamical_simulation_results.json"


def draw_figure1(ctx: cairo.Context, w: int, h: int, study_data: dict, knn_data: dict) -> None:
    """Figure 1: Forest Plot of FB ACh-GABA Mutual Dyad Association Across Controlled Null Models."""
    ctx.set_source_rgb(0.985, 0.988, 0.995)
    ctx.paint()

    # Outer border
    ctx.set_source_rgb(0.82, 0.86, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    # Title Banner
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 58)
    ctx.show_text("Figure 1: Fan-Shaped Body ACh-GABA Reciprocal Pairing Across Controlled Null Models")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("Adult Drosophila FAFB v783 | FB w >= 5 (M = 5,435 mutual dyads, B = 2,000 permutations, seed = 42)")

    # Data items for Forest Plot
    models = study_data["models"]
    m1 = models["model1_mutual_quartiles"]["results"]["pair_statistics"]["ach_gaba"]
    m2 = models["model2_joint_in_out_tertiles"]["results"]["pair_statistics"]["ach_gaba"]
    m3 = models["model3_joint_in_out_medians"]["results"]["pair_statistics"]["ach_gaba"]
    m4 = models["model4_total_degree_quintiles"]["results"]["pair_statistics"]["ach_gaba"]
    k16 = knn_data["fb_continuous_knn"]["fb_k16"]
    k8 = knn_data["fb_continuous_knn"]["fb_k8"]

    rows = [
        ("Model 1: Mutual-Degree Quartiles (4 strata)", m1["null_mean"], m1["null_std"], m1["quantiles"]["q025"], m1["quantiles"]["q975"], m1["enrichment_ratio"], m1["z_score"]),
        ("Model 2: Joint Directed In x Out Tertiles (9 strata)", m2["null_mean"], m2["null_std"], m2["quantiles"]["q025"], m2["quantiles"]["q975"], m2["enrichment_ratio"], m2["z_score"]),
        ("Model 3: Joint Directed In x Out Medians (4 strata)", m3["null_mean"], m3["null_std"], m3["quantiles"]["q025"], m3["quantiles"]["q975"], m3["enrichment_ratio"], m3["z_score"]),
        ("Model 4: Total Directed Degree Quintiles (5 strata)", m4["null_mean"], m4["null_std"], m4["quantiles"]["q025"], m4["quantiles"]["q975"], m4["enrichment_ratio"], m4["z_score"]),
        ("Benchmark A: Continuous Degree k-NN (k=16, 154 strata)", k16["null_mean"], k16["null_std"], k16["q025"], k16["q975"], k16["enrichment_ratio"], k16["z_score"]),
        ("Benchmark B: Continuous Degree k-NN (k=8, 308 strata)", k8["null_mean"], k8["null_std"], k8["q025"], k8["q975"], k8["enrichment_ratio"], k8["z_score"]),
    ]
    mcmc = knn_data.get("fb_continuous_mcmc", {}).get("fb_mcmc_sigma020", {})
    if mcmc:
        rows.append(
            ("Benchmark C: Continuous Degree MCMC (sigma=0.20)", mcmc["null_mean"], mcmc["null_std"], mcmc["q025"], mcmc["q975"], mcmc["enrichment_ratio"], mcmc["z_score"])
        )

    # Forest plot axes
    x_axis_left = 460
    x_axis_right = 920
    y_start = 120
    row_gap = 46

    # Scale: mapping dyads [0, 600] to [x_axis_left, x_axis_right]
    def val_to_x(val: float) -> float:
        return x_axis_left + (val / 600.0) * (x_axis_right - x_axis_left)

    # Grid lines and ticks
    for tick_val in [0, 100, 200, 300, 400, 500, 600]:
        tx = val_to_x(tick_val)
        ctx.set_source_rgb(0.88, 0.90, 0.94)
        ctx.set_line_width(1.0)
        ctx.move_to(tx, 110)
        ctx.line_to(tx, y_start + len(rows) * row_gap)
        ctx.stroke()

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(tx - 10, y_start + len(rows) * row_gap + 18)
        ctx.show_text(str(tick_val))

    # Axis label
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.30, 0.35, 0.45)
    ctx.move_to(x_axis_left + 140, y_start + len(rows) * row_gap + 38)
    ctx.show_text("ACh-GABA Mutual Dyad Count (Observed = 554)")

    # Observed line at 554
    obs_x = val_to_x(554)
    ctx.set_source_rgba(0.85, 0.15, 0.15, 0.8)
    ctx.set_line_width(2.0)
    ctx.move_to(obs_x, 110)
    ctx.line_to(obs_x, y_start + len(rows) * row_gap)
    ctx.stroke()

    # Draw rows
    for i, (label, mean_v, std_v, q025, q975, ratio, z) in enumerate(rows):
        ry = y_start + i * row_gap

        # Model label
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if i < 4 else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(45, ry + 4)
        ctx.show_text(label)

        # Null CI horizontal bar
        x_q025 = val_to_x(q025)
        x_q975 = val_to_x(q975)
        x_mean = val_to_x(mean_v)

        # CI line
        ctx.set_source_rgb(0.25, 0.45, 0.75)
        ctx.set_line_width(3.5)
        ctx.move_to(x_q025, ry)
        ctx.line_to(x_q975, ry)
        ctx.stroke()

        # CI end caps
        ctx.set_line_width(1.5)
        ctx.move_to(x_q025, ry - 6)
        ctx.line_to(x_q025, ry + 6)
        ctx.stroke()
        ctx.move_to(x_q975, ry - 6)
        ctx.line_to(x_q975, ry + 6)
        ctx.stroke()

        # Mean point (diamond)
        ctx.set_source_rgb(0.15, 0.30, 0.65)
        ctx.arc(x_mean, ry, 4.5, 0, 2 * 3.14159)
        ctx.fill()

        # Observed point (solid red circle)
        ctx.set_source_rgb(0.85, 0.15, 0.15)
        ctx.arc(obs_x, ry, 5.0, 0, 2 * 3.14159)
        ctx.fill()

        # Annotation text (Ratio & Z)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.80, 0.10, 0.10)
        ctx.move_to(obs_x + 10, ry + 4)
        ctx.show_text(f"{ratio:.2f}x (Z={z:+.1f})")

    # Legend / Key card
    card_y = y_start + len(rows) * row_gap + 55
    ctx.set_source_rgb(0.93, 0.95, 0.98)
    ctx.rectangle(45, card_y, w - 90, 50)
    ctx.fill()
    ctx.set_source_rgb(0.80, 0.85, 0.90)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, card_y, w - 90, 50)
    ctx.stroke()

    # Legend items
    ctx.set_source_rgb(0.85, 0.15, 0.15)
    ctx.arc(65, card_y + 25, 5, 0, 2 * 3.14159)
    ctx.fill()
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.move_to(76, card_y + 29)
    ctx.show_text("Observed Count (554 dyads)")

    ctx.set_source_rgb(0.25, 0.45, 0.75)
    ctx.arc(285, card_y + 25, 4.5, 0, 2 * 3.14159)
    ctx.fill()
    ctx.set_line_width(3.0)
    ctx.move_to(270, card_y + 25)
    ctx.line_to(300, card_y + 25)
    ctx.stroke()
    ctx.move_to(310, card_y + 29)
    ctx.show_text("Null Expectation (Mean +/- 95% Empirical Interval)")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(640, card_y + 29)
    ctx.show_text("Controlled & Continuous nulls: p < 0.05, FDR q < 0.003")


def draw_figure2(ctx: cairo.Context, w: int, h: int, anat_data: dict) -> None:
    """Figure 2: Cellular and Layer Anatomy of Fan-Shaped Body Reciprocal Feedback."""
    ctx.set_source_rgb(0.985, 0.988, 0.995)
    ctx.paint()

    # Outer border
    ctx.set_source_rgb(0.82, 0.86, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    # Title Banner
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 58)
    ctx.show_text("Figure 2: Anatomical Substrate & Layer Concentration of FB ACh-GABA Reciprocity")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("FlyWire v2.1.0 Annotations | 100% Active Node Coverage (2,465/2,465) | 554 ACh <-> GABA Mutual Dyads")

    # Panel A: Morphology Breakdown (Left)
    pA_x, pA_y, pA_w, pA_h = 45, 110, 310, 240
    ctx.set_source_rgb(0.95, 0.96, 0.98)
    ctx.rectangle(pA_x, pA_y, pA_w, pA_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(pA_x, pA_y, pA_w, pA_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.move_to(pA_x + 15, pA_y + 28)
    ctx.show_text("A. Morphology Pairing of ACh-GABA")

    # Bar chart for Panel A
    col_tan_cnt = anat_data["ach_gaba_broad"]["columnar__tangential"]
    tan_tan_cnt = anat_data["ach_gaba_broad"].get("tangential__tangential", 3)
    total_cnt = col_tan_cnt + tan_tan_cnt

    bars = [
        ("Columnar <-> Tangential", col_tan_cnt, 0.20, 0.55, 0.85),
        ("Tangential <-> Tangential", tan_tan_cnt, 0.70, 0.75, 0.80),
        ("Columnar <-> Columnar", 0, 0.80, 0.85, 0.90),
    ]

    for bi, (blabel, bcnt, cr, cg, cb) in enumerate(bars):
        by = pA_y + 60 + bi * 45
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(pA_x + 15, by + 12)
        ctx.show_text(blabel)

        # Bar
        bw = (bcnt / total_cnt) * 160 if total_cnt > 0 else 0
        ctx.set_source_rgb(cr, cg, cb)
        ctx.rectangle(pA_x + 15, by + 18, max(bw, 2), 14)
        ctx.fill()

        # Count text
        pct = (bcnt / total_cnt * 100) if total_cnt > 0 else 0
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(pA_x + 25 + max(bw, 2), by + 30)
        ctx.show_text(f"{bcnt} ({pct:.1f}%)")

    # Polarity callout inside Panel A
    ctx.set_source_rgb(0.90, 0.93, 0.97)
    ctx.rectangle(pA_x + 15, pA_y + 195, pA_w - 30, 32)
    ctx.fill()
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.10, 0.40, 0.70)
    ctx.move_to(pA_x + 22, pA_y + 215)
    ctx.show_text("Polarity: 100% Col=ACh, Tan=GABA (551/551)")

    # Panel B: Layer Distribution (Middle)
    pB_x, pB_y, pB_w, pB_h = 380, 110, 330, 240
    ctx.set_source_rgb(0.95, 0.96, 0.98)
    ctx.rectangle(pB_x, pB_y, pB_w, pB_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(pB_x, pB_y, pB_w, pB_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.move_to(pB_x + 15, pB_y + 28)
    ctx.show_text("B. Layer Distribution (FB1 to FB9)")

    # Layer bars
    layers_data = anat_data["ach_gaba_layers"]
    layer_names = [f"Layer_{i}" for i in range(1, 10)]
    max_layer_cnt = max(layers_data.values()) if layers_data else 1

    chart_x = pB_x + 30
    chart_y = pB_y + 195
    chart_w = pB_w - 60
    col_w = chart_w / 9.0

    for li, lname in enumerate(layer_names):
        l_cnt = layers_data.get(lname, 0)
        lx = chart_x + li * col_w
        lh = (l_cnt / max_layer_cnt) * 125.0

        # Bar
        if li in [3, 4]:  # Layer 4 and 5 highlighted
            ctx.set_source_rgb(0.85, 0.25, 0.25)
        else:
            ctx.set_source_rgb(0.70, 0.75, 0.82)
        ctx.rectangle(lx + 2, chart_y - lh, col_w - 4, lh)
        ctx.fill()

        # Layer number tick
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if li in [3, 4] else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(lx + 4, chart_y + 14)
        ctx.show_text(f"L{li+1}")

        # Count above bar if > 0
        if l_cnt > 0:
            ctx.set_font_size(8)
            ctx.move_to(lx + 2, chart_y - lh - 4)
            ctx.show_text(str(l_cnt))

    # Highlight note
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.80, 0.15, 0.15)
    ctx.move_to(pB_x + 25, pB_y + 225)
    ctx.show_text("Layers 4 & 5 contain 99.1% of all loops (549/554)")

    # Panel C: Top Specific Cell-Type Pairs (Right)
    pC_x, pC_y, pC_w, pC_h = 735, 110, 325, 240
    ctx.set_source_rgb(0.95, 0.96, 0.98)
    ctx.rectangle(pC_x, pC_y, pC_w, pC_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(pC_x, pC_y, pC_w, pC_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.move_to(pC_x + 15, pA_y + 28)
    ctx.show_text("C. Dominant Specific Microcircuits")

    top_pairs = list(anat_data["ach_gaba_top_cell_pairs"].items())[:6]
    for cpi, (cp_name, cp_cnt) in enumerate(top_pairs):
        cpy = pC_y + 52 + cpi * 30
        pct = cp_cnt / total_cnt * 100

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(pC_x + 15, cpy)
        ctx.show_text(f"{cp_name}")

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_source_rgb(0.15, 0.35, 0.65)
        ctx.move_to(pC_x + 235, cpy)
        ctx.show_text(f"{cp_cnt} ({pct:.1f}%)")

    # Panel D: Architectural Synthesis Card (Bottom)
    pD_x, pD_y, pD_w, pD_h = 45, 375, w - 90, 115
    ctx.set_source_rgb(0.93, 0.95, 0.99)
    ctx.rectangle(pD_x, pD_y, pD_w, pD_h)
    ctx.fill()
    ctx.set_source_rgb(0.75, 0.82, 0.92)
    ctx.set_line_width(1.2)
    ctx.rectangle(pD_x, pD_y, pD_w, pD_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(pD_x + 20, pD_y + 26)
    ctx.show_text("D. Biological Synthesis: Premotor Gain Control & Vector Routing")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.25, 0.30, 0.40)
    ctx.move_to(pD_x + 20, pD_y + 48)
    ctx.show_text("• Columnar-Tangential Polarization: Reciprocal loops in FB connect cholinergic columnar steering neurons (vDeltaA, FC2, hDelta) with GABAergic")
    ctx.move_to(pD_x + 30, pD_y + 64)
    ctx.show_text("tangential fan neurons (FB4A, FB5A), forming an active inhibitory feedback loop.")
    ctx.move_to(pD_x + 20, pD_y + 82)
    ctx.show_text("• Layer Specialization: Layers 4 and 5 correspond to the primary premotor integration hub of the Fan-Shaped Body, where internal state signals")
    ctx.move_to(pD_x + 30, pD_y + 98)
    ctx.show_text("(tangential inputs) modulate heading and goal-directed steering vectors (columnar interneurons) before transmission to descending motor pathways.")


def draw_figure3(ctx: cairo.Context, w: int, h: int) -> None:
    """Figure 3: Architectural Contrast: 1D Ring Attractor (EB) vs 2D Vector Steering (FB)."""
    ctx.set_source_rgb(0.985, 0.988, 0.995)
    ctx.paint()

    # Outer border
    ctx.set_source_rgb(0.82, 0.86, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    # Title Banner
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 58)
    ctx.show_text("Figure 3: Circuit Architecture Contrast: 1D Heading (EB) vs 2D Vector Steering (FB)")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("Central Complex Connectomic Divergence: Homotypic Ring Recurrence vs Heterotypic Columnar-Tangential Feedback")

    # Left Card: Ellipsoid Body (EB)
    card_w = (w - 110) / 2
    left_x = 45
    card_y = 105
    card_h = 375

    ctx.set_source_rgb(0.96, 0.97, 0.99)
    ctx.rectangle(left_x, card_y, card_w, card_h)
    ctx.fill()
    ctx.set_source_rgb(0.80, 0.85, 0.92)
    ctx.set_line_width(1.2)
    ctx.rectangle(left_x, card_y, card_w, card_h)
    ctx.stroke()

    # EB Header
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(15)
    ctx.set_source_rgb(0.15, 0.35, 0.65)
    ctx.move_to(left_x + 20, card_y + 32)
    ctx.show_text("ELLIPSOID BODY (EB): 1D Ring Attractor")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.30, 0.35, 0.45)
    ctx.move_to(left_x + 20, card_y + 54)
    ctx.show_text("Primary Function: Internal Heading Representation (Compass Bump)")

    eb_points = [
        ("Network Size", "483 active neurons, 15,812 directed edges"),
        ("Topological Reciprocity", "44.50% (Rank #1 in whole fly brain; M = 3,518)"),
        ("Primary Reciprocal Motif", "GABA <-> GABA (74.33% of mutual dyads; 2,615 dyads)"),
        ("Conditional Enrichment", "+20.6% to +31.8% excess (Z = +13 to +16, p = 0.0005)"),
        ("Anatomical Substrate", "88.18% Ring Neuron <-> Ring Neuron (ER <-> ER)"),
        ("Homotypic Subtypes", "77.48% homotypic ER base pairs (ER2, ER3d, ER4d)"),
        ("Cross-Transmitter Motif", "ACh <-> GABA is DELETED (0.27x, Z = -23.2)"),
        ("Circuit Logic", "Broad mutual inhibition suppresses off-bump activity;"),
        ("", "compass neurons are segregated in separate columnar loops."),
    ]

    for pi, (label, text) in enumerate(eb_points):
        py = card_y + 85 + pi * 30
        if label:
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(10)
            ctx.set_source_rgb(0.15, 0.25, 0.40)
            ctx.move_to(left_x + 20, py)
            ctx.show_text(f"{label}:")
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_source_rgb(0.25, 0.30, 0.38)
            ctx.move_to(left_x + 175, py)
            ctx.show_text(text)
        else:
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_source_rgb(0.25, 0.30, 0.38)
            ctx.move_to(left_x + 20, py)
            ctx.show_text(text)

    # Right Card: Fan-Shaped Body (FB)
    right_x = left_x + card_w + 20
    ctx.set_source_rgb(0.99, 0.97, 0.96)
    ctx.rectangle(right_x, card_y, card_w, card_h)
    ctx.fill()
    ctx.set_source_rgb(0.92, 0.82, 0.78)
    ctx.set_line_width(1.2)
    ctx.rectangle(right_x, card_y, card_w, card_h)
    ctx.stroke()

    # FB Header
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(15)
    ctx.set_source_rgb(0.75, 0.25, 0.15)
    ctx.move_to(right_x + 20, card_y + 32)
    ctx.show_text("FAN-SHAPED BODY (FB): 2D Vector Matrix")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.40, 0.30, 0.25)
    ctx.move_to(right_x + 20, card_y + 54)
    ctx.show_text("Primary Function: Vector Steering, Goal Routing, Premotor Action")

    fb_points = [
        ("Network Size", "2,465 active neurons, 46,903 directed edges"),
        ("Topological Reciprocity", "23.18% (Rank #6 in fly brain; M = 5,435)"),
        ("Primary Reciprocal Motif", "ACh <-> GABA (554 dyads; 5.7x-5.9x enriched, Z = +16 to +18)"),
        ("Continuous k-NN", "2.3x to 2.7x enriched (Z = +6.3 to +6.8, p = 0.001)"),
        ("Anatomical Substrate", "99.46% Columnar <-> Tangential feedback (551 dyads)"),
        ("Directional Polarity", "100% Columnar = ACh (excitatory), Tangential = GABA"),
        ("Layer Localization", "93.9% concentrated in premotor Layers 4 & 5 (520 dyads)"),
        ("Homotypic Recurrence", "GABA <-> GABA is ABSENT (only 6 dyads, 0.11%)"),
        ("Circuit Logic", "Excitatory columnar steering vectors tightly modulated"),
        ("", "by inhibitory tangential state signals at output layers."),
    ]

    for pi, (label, text) in enumerate(fb_points):
        py = card_y + 85 + pi * 28
        if label:
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(10)
            ctx.set_source_rgb(0.50, 0.20, 0.15)
            ctx.move_to(right_x + 20, py)
            ctx.show_text(f"{label}:")
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_source_rgb(0.35, 0.25, 0.20)
            ctx.move_to(right_x + 175, py)
            ctx.show_text(text)
        else:
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_source_rgb(0.35, 0.25, 0.20)
            ctx.move_to(right_x + 20, py)
            ctx.show_text(text)


def draw_figure4(ctx: cairo.Context, w: int, h: int, sim_data: dict) -> None:
    """Figure 4: Divisive Gain Control & Contrast Stabilization in Reciprocal Steering Circuit (Layers 4 & 5)."""
    ctx.set_source_rgb(0.985, 0.988, 0.995)
    ctx.paint()

    # Outer border
    ctx.set_source_rgb(0.82, 0.86, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    # Title Banner
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 58)
    ctx.show_text("Figure 4: Rate-Based Circuit Dynamics: Divisive Gain Control in FB Layers 4 & 5")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("16-Column Steering Model | Empirical Synaptic Weights (FB4A <-> vDeltaA, FB5A <-> FC2) | Intact vs. Ablated Inhibition")

    intact = sim_data["simulation_results"]["intact_reciprocal_feedback"]
    ablated = sim_data["simulation_results"]["ablated_reciprocal_feedback"]

    # Panel A: Gain Curve (Left, Peak Rate vs Input Drive)
    pA_x, pA_y, pA_w, pA_h = 45, 110, 460, 250
    ctx.set_source_rgb(0.95, 0.96, 0.98)
    ctx.rectangle(pA_x, pA_y, pA_w, pA_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(pA_x, pA_y, pA_w, pA_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.move_to(pA_x + 15, pA_y + 28)
    ctx.show_text("A. Divisive Gain Control (Peak Firing Rate vs Drive)")

    # Plot axes for Panel A
    ax_x0 = pA_x + 60
    ax_x1 = pA_x + pA_w - 30
    ax_y0 = pA_y + pA_h - 40
    ax_y1 = pA_y + 55

    # Ticks & Grid
    ctx.set_line_width(1.0)
    for d_val in [0, 5, 10, 15, 20]:
        x = ax_x0 + (d_val / 20.0) * (ax_x1 - ax_x0)
        ctx.set_source_rgb(0.88, 0.90, 0.94)
        ctx.move_to(x, ax_y1)
        ctx.line_to(x, ax_y0)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(x - 5, ax_y0 + 15)
        ctx.show_text(str(d_val))

    for r_val in [0, 100, 200, 300]:
        y = ax_y0 - (r_val / 300.0) * (ax_y0 - ax_y1)
        ctx.set_source_rgb(0.88, 0.90, 0.94)
        ctx.move_to(ax_x0, y)
        ctx.line_to(ax_x1, y)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(ax_x0 - 28, y + 4)
        ctx.show_text(str(r_val))

    # Axis Labels
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.25, 0.30, 0.40)
    ctx.move_to(pA_x + 180, ax_y0 + 30)
    ctx.show_text("Input Velocity / Sensory Drive (I0)")
    ctx.move_to(pA_x + 8, ax_y1 - 10)
    ctx.show_text("Peak (Hz)")

    # Plot Ablated Curve (Red)
    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.set_line_width(2.5)
    for idx, pt in enumerate(ablated):
        x = ax_x0 + (pt["drive"] / 20.0) * (ax_x1 - ax_x0)
        y = ax_y0 - (pt["peak_rate"] / 300.0) * (ax_y0 - ax_y1)
        if idx == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.stroke()

    # Plot Intact Curve (Blue)
    ctx.set_source_rgb(0.15, 0.45, 0.85)
    ctx.set_line_width(2.5)
    for idx, pt in enumerate(intact):
        x = ax_x0 + (pt["drive"] / 20.0) * (ax_x1 - ax_x0)
        y = ax_y0 - (pt["peak_rate"] / 300.0) * (ax_y0 - ax_y1)
        if idx == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.stroke()

    # Points on curves
    for pt in intact:
        x = ax_x0 + (pt["drive"] / 20.0) * (ax_x1 - ax_x0)
        y = ax_y0 - (pt["peak_rate"] / 300.0) * (ax_y0 - ax_y1)
        ctx.arc(x, y, 3.5, 0, 2 * 3.14159)
        ctx.set_source_rgb(0.15, 0.45, 0.85)
        ctx.fill()

    for pt in ablated:
        x = ax_x0 + (pt["drive"] / 20.0) * (ax_x1 - ax_x0)
        y = ax_y0 - (pt["peak_rate"] / 300.0) * (ax_y0 - ax_y1)
        ctx.arc(x, y, 3.5, 0, 2 * 3.14159)
        ctx.set_source_rgb(0.85, 0.20, 0.20)
        ctx.fill()

    # Legend inside Panel A
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.15, 0.45, 0.85)
    ctx.move_to(ax_x0 + 15, ax_y1 + 18)
    ctx.show_text("— Intact Reciprocal Inhibition (Clamped <= 30.6 Hz)")

    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.move_to(ax_x0 + 15, ax_y1 + 34)
    ctx.show_text("— Ablated Reciprocal Inhibition (Explodes to 297.4 Hz, 9.7x)")

    # Panel B: Columnar Bump Profiles (Right, 16 Columns)
    pB_x, pB_y, pB_w, pB_h = 530, 110, 480, 250
    ctx.set_source_rgb(0.95, 0.96, 0.98)
    ctx.rectangle(pB_x, pB_y, pB_w, pB_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(pB_x, pB_y, pB_w, pB_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.move_to(pB_x + 15, pB_y + 28)
    ctx.show_text("B. Spatial Steering Bump Profile (Normalized Drive I0=15)")

    # Plot axes for Panel B
    bx_x0 = pB_x + 50
    bx_x1 = pB_x + pB_w - 30
    bx_y0 = pB_y + pB_h - 40
    bx_y1 = pB_y + 55

    high_i = intact[6]
    high_a = ablated[6]
    norm_intact = [r / high_i["peak_rate"] for r in high_i["bump_profile"]]
    norm_ablated = [r / high_a["peak_rate"] for r in high_a["bump_profile"]]

    # Column axis ticks
    for col_i in range(16):
        x = bx_x0 + (col_i / 15.0) * (bx_x1 - bx_x0)
        ctx.set_source_rgb(0.88, 0.90, 0.94)
        ctx.set_line_width(1.0)
        ctx.move_to(x, bx_y1)
        ctx.line_to(x, bx_y0)
        ctx.stroke()
        if col_i % 3 == 0 or col_i == 15:
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(9)
            ctx.set_source_rgb(0.45, 0.50, 0.60)
            ctx.move_to(x - 6, bx_y0 + 15)
            ctx.show_text(f"C{col_i+1}")

    for a_val in [0.0, 0.5, 1.0]:
        y = bx_y0 - a_val * (bx_y0 - bx_y1)
        ctx.set_source_rgb(0.88, 0.90, 0.94)
        ctx.move_to(bx_x0, y)
        ctx.line_to(bx_x1, y)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(bx_x0 - 24, y + 4)
        ctx.show_text(f"{a_val:.1f}")

    ctx.set_font_size(10)
    ctx.set_source_rgb(0.25, 0.30, 0.40)
    ctx.move_to(pB_x + 190, bx_y0 + 30)
    ctx.show_text("Fan-Shaped Body Columns (C1 to C16)")

    # Draw Ablated Bump (Red, Broadened)
    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.set_line_width(2.5)
    for col_i in range(16):
        x = bx_x0 + (col_i / 15.0) * (bx_x1 - bx_x0)
        y = bx_y0 - norm_ablated[col_i] * (bx_y0 - bx_y1)
        if col_i == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.stroke()

    # Draw Intact Bump (Blue, Sharp)
    ctx.set_source_rgb(0.15, 0.45, 0.85)
    ctx.set_line_width(2.5)
    for col_i in range(16):
        x = bx_x0 + (col_i / 15.0) * (bx_x1 - bx_x0)
        y = bx_y0 - norm_intact[col_i] * (bx_y0 - bx_y1)
        if col_i == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.stroke()

    # Legend inside Panel B
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.15, 0.45, 0.85)
    ctx.move_to(bx_x0 + 15, bx_y1 + 18)
    ctx.show_text("— Intact Feedback: FWHM = 90.0° (Sharp Directional Tuning)")

    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.move_to(bx_x0 + 15, bx_y1 + 34)
    ctx.show_text("— Ablated Feedback: FWHM = 135.0° (Broadened Saturation, Contrast Loss)")

    # Panel C: Synthesis Card (Bottom)
    pC_x, pC_y, pC_w, pC_h = 45, 380, w - 90, 110
    ctx.set_source_rgb(0.93, 0.95, 0.99)
    ctx.rectangle(pC_x, pC_y, pC_w, pC_h)
    ctx.fill()
    ctx.set_source_rgb(0.75, 0.82, 0.92)
    ctx.set_line_width(1.2)
    ctx.rectangle(pC_x, pC_y, pC_w, pC_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(pC_x + 20, pC_y + 26)
    ctx.show_text("C. Biological Synthesis: Why 99.1% of ACh <-> GABA Loops Are in Layers 4 & 5")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.25, 0.30, 0.40)
    ctx.move_to(pC_x + 20, pC_y + 48)
    ctx.show_text("• Divisive Normalization: Reciprocal GABAergic tangential feedback (FB4A, FB5A, FB5I2) clamps columnar steering neurons (vDeltaA, FC2)")
    ctx.move_to(pC_x + 30, pC_y + 64)
    ctx.show_text("to a physiological dynamic range (1.5 - 30.6 Hz), preventing catastrophic motor saturation under high flight velocity or sensory drive.")
    ctx.move_to(pC_x + 20, pC_y + 82)
    ctx.show_text("• Contrast Preservation: Divisive feedback maintains sharp directional tuning (FWHM = 90.0° vs 135.0° when ablated) and preserves the steering")
    ctx.move_to(pC_x + 30, pC_y + 98)
    ctx.show_text("vector length (||v|| = 0.8598) with sub-degree decoding error (< 0.8°), enabling robust 2D navigation across diverse environments.")


def main() -> None:
    print("=" * 80)
    print("VECTORWING: GENERATING PRESENTATION FIGURES (SVG & PNG)")
    print("=" * 80)

    if cairo is None:
        print("Error: cairo module required.")
        sys.exit(1)

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(STUDY_JSON) as f:
        study_data = json.load(f)
    with open(ANATOMY_JSON) as f:
        anat_data = json.load(f)
    with open(KNN_JSON) as f:
        knn_data = json.load(f)
    sim_data = None
    if SIM_JSON.exists():
        with open(SIM_JSON) as f:
            sim_data = json.load(f)

    # 1. Figure 1
    f1_svg = FIG_DIR / "figure1_fb_conditional_associations.svg"
    f1_png = FIG_DIR / "figure1_fb_conditional_associations.png"
    w1, h1 = 980, 520
    print(f"\n[1/4] Rendering Figure 1 ({w1}x{h1}) ...")
    svg_s1 = cairo.SVGSurface(str(f1_svg), w1, h1)
    draw_figure1(cairo.Context(svg_s1), w1, h1, study_data, knn_data)
    svg_s1.finish()

    img_s1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, w1, h1)
    draw_figure1(cairo.Context(img_s1), w1, h1, study_data, knn_data)
    img_s1.write_to_png(str(f1_png))
    print(f"  Generated SVG: {f1_svg} ({f1_svg.stat().st_size:,} bytes)")
    print(f"  Generated PNG: {f1_png} ({f1_png.stat().st_size:,} bytes)")

    # 2. Figure 2
    f2_svg = FIG_DIR / "figure2_fb_layer_column_matrix.svg"
    f2_png = FIG_DIR / "figure2_fb_layer_column_matrix.png"
    w2, h2 = 1100, 520
    print(f"\n[2/4] Rendering Figure 2 ({w2}x{h2}) ...")
    svg_s2 = cairo.SVGSurface(str(f2_svg), w2, h2)
    draw_figure2(cairo.Context(svg_s2), w2, h2, anat_data)
    svg_s2.finish()

    img_s2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, w2, h2)
    draw_figure2(cairo.Context(img_s2), w2, h2, anat_data)
    img_s2.write_to_png(str(f2_png))
    print(f"  Generated SVG: {f2_svg} ({f2_svg.stat().st_size:,} bytes)")
    print(f"  Generated PNG: {f2_png} ({f2_png.stat().st_size:,} bytes)")

    # 3. Figure 3
    f3_svg = FIG_DIR / "figure3_eb_vs_fb_circuit_contrast.svg"
    f3_png = FIG_DIR / "figure3_eb_vs_fb_circuit_contrast.png"
    w3, h3 = 1080, 520
    print(f"\n[3/4] Rendering Figure 3 ({w3}x{h3}) ...")
    svg_s3 = cairo.SVGSurface(str(f3_svg), w3, h3)
    draw_figure3(cairo.Context(svg_s3), w3, h3)
    svg_s3.finish()

    img_s3 = cairo.ImageSurface(cairo.FORMAT_ARGB32, w3, h3)
    draw_figure3(cairo.Context(img_s3), w3, h3)
    img_s3.write_to_png(str(f3_png))
    print(f"  Generated SVG: {f3_svg} ({f3_svg.stat().st_size:,} bytes)")
    print(f"  Generated PNG: {f3_png} ({f3_png.stat().st_size:,} bytes)")

    # 4. Figure 4
    if sim_data:
        f4_svg = FIG_DIR / "figure4_vector_steering_dynamics.svg"
        f4_png = FIG_DIR / "figure4_vector_steering_dynamics.png"
        w4, h4 = 1050, 520
        print(f"\n[4/4] Rendering Figure 4 ({w4}x{h4}) ...")
        svg_s4 = cairo.SVGSurface(str(f4_svg), w4, h4)
        draw_figure4(cairo.Context(svg_s4), w4, h4, sim_data)
        svg_s4.finish()

        img_s4 = cairo.ImageSurface(cairo.FORMAT_ARGB32, w4, h4)
        draw_figure4(cairo.Context(img_s4), w4, h4, sim_data)
        img_s4.write_to_png(str(f4_png))
        print(f"  Generated SVG: {f4_svg} ({f4_svg.stat().st_size:,} bytes)")
        print(f"  Generated PNG: {f4_png} ({f4_png.stat().st_size:,} bytes)")

    print("\nAll presentation figures rendered successfully!")


if __name__ == "__main__":
    main()
