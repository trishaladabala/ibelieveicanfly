#!/usr/bin/env python3
"""
Generate presentation-quality figures (SVG and PNG) for Phase 8 Portfolio Release Candidate.

Outputs:
1. results/real_data_pilot/phase8/figure1_conditional_gaba_associations.svg
   results/real_data_pilot/phase8/figure1_conditional_gaba_associations.png
   - Forest plot / range comparison of observed EB GABA-GABA mutual dyads against
     the three tested degree-stratified null models (mutual quartiles, directed tertiles, directed medians).

2. results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.svg
   results/real_data_pilot/phase8/figure2_descriptive_cell_type_composition.png
   - Multi-panel descriptive cellular composition of EB mutual dyads from FlyWire v2.1.0 annotations,
     showing broad classes, homotypic ER subtypes, explicit denominators, and field completeness.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

# Use system cairo if available for exact vector SVG and raster PNG rendering
try:
    import cairo
except ImportError:
    cairo = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE8_DIR = PROJECT_ROOT / "results" / "real_data_pilot" / "phase8"
PHASE8_DIR.mkdir(parents=True, exist_ok=True)


def draw_figure1(ctx: cairo.Context, w: int, h: int) -> None:
    """Draws Figure 1: EB GABA-GABA Mutual Dyad Association Across Degree-Stratified Null Models."""
    # Background
    ctx.set_source_rgb(0.98, 0.98, 0.99)
    ctx.paint()

    # Outer border / card
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    # Title Banner
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 60)
    ctx.show_text("Figure 1: EB GABA-GABA Mutual Dyad Association Across Degree-Stratified Null Models")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.48)
    ctx.move_to(45, 82)
    ctx.show_text("Adult Drosophila melanogaster FAFB v783 | Ellipsoid Body (w >= 5, M = 3,518 mutual dyads, B = 2,000 permutations)")

    # Axis Setup for Forest Plot
    plot_x = 380
    plot_w = 420
    axis_y = 440
    val_min = 1800
    val_max = 2800

    def val_to_x(val: float) -> float:
        return plot_x + (val - val_min) / (val_max - val_min) * plot_w

    # Gridlines and ticks
    ctx.set_font_size(11)
    for tick in range(1800, 2801, 200):
        tx = val_to_x(tick)
        ctx.set_source_rgba(0.82, 0.85, 0.90, 0.8)
        ctx.set_line_width(1.0)
        ctx.move_to(tx, 120)
        ctx.line_to(tx, axis_y)
        ctx.stroke()

        ctx.set_source_rgb(0.40, 0.45, 0.52)
        ctx.move_to(tx - 15, axis_y + 20)
        ctx.show_text(f"{tick:,}")

    # Axis label
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.20, 0.25, 0.35)
    ctx.move_to(plot_x + plot_w // 2 - 80, axis_y + 42)
    ctx.show_text("GABA-GABA Mutual Dyads")

    # Data for the 3 models
    models = [
        {
            "id": "Model 1: Mutual Degree Quartiles",
            "desc": "Baseline P6: 4 strata by mutual degree | Shared RNG stream",
            "mean": 2167.11,
            "std": 29.31,
            "q025": 2107,
            "q975": 2225,
            "enrich": "1.206x (+20.7%)",
            "z": "+15.28",
            "p": "0.000500",
            "y": 165,
            "color": (0.22, 0.45, 0.70),  # Steel blue
        },
        {
            "id": "Model 2: Directed In x Out Tertiles",
            "desc": "Primary Sensitivity: 9 strata (3x3 grid) | Fresh seed 42",
            "mean": 2037.96,
            "std": 35.86,
            "q025": 1968,
            "q975": 2108,
            "enrich": "1.283x (+28.3%)",
            "z": "+16.09",
            "p": "0.000500",
            "y": 255,
            "color": (0.15, 0.55, 0.55),  # Teal
        },
        {
            "id": "Model 3: Directed In x Out Medians",
            "desc": "Secondary Sensitivity: 4 strata (2x2 grid) | Fresh seed 42",
            "mean": 1984.76,
            "std": 48.05,
            "q025": 1891,
            "q975": 2079,
            "enrich": "1.318x (+31.8%)",
            "z": "+13.12",
            "p": "0.000500",
            "y": 345,
            "color": (0.45, 0.35, 0.65),  # Purple
        },
    ]

    obs_val = 2615
    obs_x = val_to_x(obs_val)

    # Vertical line for Observed Count across all rows
    ctx.set_source_rgba(0.85, 0.20, 0.20, 0.85)
    ctx.set_line_width(2.0)
    ctx.move_to(obs_x, 115)
    ctx.line_to(obs_x, axis_y)
    ctx.stroke()

    # Observed label at top of line
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.85, 0.15, 0.15)
    ctx.move_to(obs_x - 45, 112)
    ctx.show_text("Observed: 2,615")

    # Render each model row
    for m in models:
        y = m["y"]
        col = m["color"]

        # Background card for model description
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(45, y - 35, 315, 70)
        ctx.fill()
        ctx.set_source_rgb(0.88, 0.90, 0.94)
        ctx.set_line_width(1.0)
        ctx.rectangle(45, y - 35, 315, 70)
        ctx.stroke()

        # Accent bar on card left
        ctx.set_source_rgb(col[0], col[1], col[2])
        ctx.rectangle(45, y - 35, 5, 70)
        ctx.fill()

        # Text labels on left card
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13)
        ctx.set_source_rgb(0.12, 0.16, 0.24)
        ctx.move_to(58, y - 12)
        ctx.show_text(m["id"])

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.40, 0.45, 0.52)
        ctx.move_to(58, y + 6)
        ctx.show_text(m["desc"])

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        ctx.set_source_rgb(col[0], col[1], col[2])
        ctx.move_to(58, y + 24)
        ctx.show_text(f"Enrichment: {m['enrich']} | Z = {m['z']}")

        # 95% CI Interval bar on plot
        x_q025 = val_to_x(m["q025"])
        x_q975 = val_to_x(m["q975"])
        x_mean = val_to_x(m["mean"])

        # Shaded 95% interval
        ctx.set_source_rgba(col[0], col[1], col[2], 0.20)
        ctx.rectangle(x_q025, y - 14, x_q975 - x_q025, 28)
        ctx.fill()

        # Interval boundary whiskers
        ctx.set_source_rgb(col[0], col[1], col[2])
        ctx.set_line_width(2.0)
        ctx.move_to(x_q025, y)
        ctx.line_to(x_q975, y)
        ctx.stroke()

        ctx.move_to(x_q025, y - 8)
        ctx.line_to(x_q025, y + 8)
        ctx.stroke()

        ctx.move_to(x_q975, y - 8)
        ctx.line_to(x_q975, y + 8)
        ctx.stroke()

        # Mean point marker (Diamond)
        d_sz = 6
        ctx.move_to(x_mean, y - d_sz)
        ctx.line_to(x_mean + d_sz, y)
        ctx.line_to(x_mean, y + d_sz)
        ctx.line_to(x_mean - d_sz, y)
        ctx.close_path()
        ctx.fill()

        # Mean label above marker
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(col[0], col[1], col[2])
        ctx.move_to(x_mean - 30, y - 18)
        ctx.show_text(f"Mean: {m['mean']:,.1f}")

        # Summary box on far right
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(820, y - 35, 125, 70)
        ctx.fill()
        ctx.set_source_rgb(0.88, 0.90, 0.94)
        ctx.set_line_width(1.0)
        ctx.rectangle(820, y - 35, 125, 70)
        ctx.stroke()

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(830, y - 14)
        ctx.show_text("Null 95% Range:")
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.35, 0.40, 0.50)
        ctx.move_to(830, y + 2)
        ctx.show_text(f"[{m['q025']} - {m['q975']}]")
        ctx.move_to(830, y + 18)
        ctx.show_text(f"p = {m['p']}")

    # Bottom Calibrated Note
    ctx.set_source_rgb(0.92, 0.94, 0.97)
    ctx.rectangle(45, h - 75, w - 90, 42)
    ctx.fill()
    ctx.set_source_rgb(0.75, 0.80, 0.88)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, h - 75, w - 90, 42)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.20, 0.25, 0.35)
    ctx.move_to(55, h - 55)
    ctx.show_text("Methodological Interpretation:")
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_source_rgb(0.30, 0.35, 0.45)
    ctx.move_to(245, h - 55)
    ctx.show_text("Each null model holds empirical mutual topology (M = 3,518) fixed and permutes whole-neuron labels within degree strata.")
    ctx.move_to(55, h - 40)
    ctx.show_text("Different strata specifications define distinct null hypotheses; none is uniquely correct, and none eliminates exact degree sequence confounding.")


def draw_figure2(ctx: cairo.Context, w: int, h: int) -> None:
    """Draws Figure 2: Descriptive Cellular Composition of EB Mutual Dyads."""
    # Background
    ctx.set_source_rgb(0.98, 0.98, 0.99)
    ctx.paint()

    # Outer border
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    # Title Banner
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 58)
    ctx.show_text("Figure 2: Descriptive Cellular Composition of EB Mutual Dyads (FAFB v783)")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.48)
    ctx.move_to(45, 80)
    ctx.show_text("Descriptive Anatomy from Pinned FlyWire v2.1.0 Annotations (Not Evidence of Independent Partner Preference)")

    # -------------------------------------------------------------
    # PANEL A: Broad Dyad Sub-Class Breakdown (Left side, w=480)
    # -------------------------------------------------------------
    p1_x = 45
    p1_y = 110
    p1_w = 485
    p1_h = 360

    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.rectangle(p1_x, p1_y, p1_w, p1_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(p1_x, p1_y, p1_w, p1_h)
    ctx.stroke()

    # Panel A Header
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(14)
    ctx.set_source_rgb(0.12, 0.18, 0.28)
    ctx.move_to(p1_x + 18, p1_y + 30)
    ctx.show_text("A. Broad Sub-Class Pairings (Denominator M = 3,518)")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.45, 0.50, 0.58)
    ctx.move_to(p1_x + 18, p1_y + 48)
    ctx.show_text("Pairs classified by cell_sub_class column in FlyWire v2.1.0")

    subclass_data = [
        ("Ring neuron <-> Ring neuron", 2306, 65.55, (0.20, 0.50, 0.75), "88.18% of GABA-GABA dyads"),
        ("Missing <-> Missing (EPG-PEN / ExR / Col)", 639, 18.16, (0.80, 0.50, 0.20), "305 EPG-PEN compass loops"),
        ("Ring neuron <-> Missing (ExR / EPG)", 399, 11.34, (0.50, 0.65, 0.35), "195 Ring-ExR, 134 Ring-EPG"),
        ("Columnar <-> Ring neuron", 109, 3.10, (0.60, 0.35, 0.65), "EL & hDeltaK to Ring"),
        ("Columnar <-> Missing", 65, 1.85, (0.75, 0.35, 0.35), "EL to EPG / ExR"),
    ]

    bar_y_start = p1_y + 75
    bar_h = 24
    bar_gap = 52
    max_pct = 75.0
    bar_max_w = 280

    for idx, (label, cnt, pct, col, note) in enumerate(subclass_data):
        by = bar_y_start + idx * bar_gap
        # Label
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(p1_x + 18, by + 12)
        ctx.show_text(label)

        # Bar
        bw = (pct / max_pct) * bar_max_w
        ctx.set_source_rgb(col[0], col[1], col[2])
        ctx.rectangle(p1_x + 18, by + 18, bw, bar_h)
        ctx.fill()

        # Count & Percentage Text
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(p1_x + 28 + bw, by + 34)
        ctx.show_text(f"{cnt:,} ({pct:.2f}%)")

        # Subtitle note
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.58)
        ctx.move_to(p1_x + 300, by + 12)
        ctx.show_text(f"[{note}]")

    # -------------------------------------------------------------
    # PANEL B: Dominant Homotypic Ring Neuron Subtypes (Right, w=510)
    # -------------------------------------------------------------
    p2_x = 550
    p2_y = 110
    p2_w = 510
    p2_h = 360

    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.rectangle(p2_x, p2_y, p2_w, p2_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(p2_x, p2_y, p2_w, p2_h)
    ctx.stroke()

    # Panel B Header
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(14)
    ctx.set_source_rgb(0.12, 0.18, 0.28)
    ctx.move_to(p2_x + 18, p2_y + 30)
    ctx.show_text("B. Top Homotypic Ring Subtypes (N_gaba = 2,615; M = 3,518)")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.45, 0.50, 0.58)
    ctx.move_to(p2_x + 18, p2_y + 48)
    ctx.show_text("Both endpoints share identical hemibrain base type (Not finer morphotypes)")

    er_types = [
        ("ER2 <-> ER2", 458, 17.51, 13.02),
        ("ER3d <-> ER3d", 445, 17.02, 12.65),
        ("ER4d <-> ER4d", 274, 10.48, 7.79),
        ("ER3w <-> ER3w", 243, 9.29, 6.91),
        ("ER5 <-> ER5", 191, 7.30, 5.43),
        ("ER3a <-> ER3a", 174, 6.65, 4.95),
        ("ER3p <-> ER3p", 129, 4.93, 3.67),
        ("ER3m <-> ER3m", 112, 4.28, 3.18),
    ]

    er_y_start = p2_y + 68
    er_h = 16
    er_gap = 26
    er_max_w = 210

    for idx, (label, cnt, p_gaba, p_tot) in enumerate(er_types):
        ey = er_y_start + idx * er_gap

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(p2_x + 18, ey + 12)
        ctx.show_text(f"{label:15s}")

        ew = (cnt / 500.0) * er_max_w
        ctx.set_source_rgb(0.25, 0.55, 0.50)
        ctx.rectangle(p2_x + 130, ey + 1, ew, er_h)
        ctx.fill()

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(p2_x + 140 + ew, ey + 13)
        ctx.show_text(f"{cnt} dyads  ({p_gaba:.1f}% GABA-GABA | {p_tot:.1f}% Total)")

    # Subtotal Summary Line in Panel B
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.move_to(p2_x + 18, p2_y + 285)
    ctx.line_to(p2_x + p2_w - 18, p2_y + 285)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.10, 0.35, 0.35)
    ctx.move_to(p2_x + 18, p2_y + 305)
    ctx.show_text("Top 8 ER Homotypic Subtotal: 2,026 dyads")
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_source_rgb(0.30, 0.35, 0.45)
    ctx.move_to(p2_x + 290, p2_y + 305)
    ctx.show_text("(77.48% of GABA-GABA | 57.59% of M)")

    ctx.move_to(p2_x + 18, p2_y + 325)
    ctx.show_text("All 10 ER Homotypic Subtotal (adding ER4m, ER1): 2,086 dyads (79.77% GABA-GABA)")
    ctx.move_to(p2_x + 18, p2_y + 343)
    ctx.show_text("Total Homotypic Dyads Across All EB Types: 2,171 dyads (61.71% of M = 3,518)")

    # -------------------------------------------------------------
    # PANEL C: Annotation Field Completeness & Guardrail Note
    # -------------------------------------------------------------
    p3_x = 45
    p3_y = 485
    p3_w = w - 90
    p3_h = 100

    ctx.set_source_rgb(0.94, 0.96, 0.98)
    ctx.rectangle(p3_x, p3_y, p3_w, p3_h)
    ctx.fill()
    ctx.set_source_rgb(0.82, 0.86, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(p3_x, p3_y, p3_w, p3_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.12, 0.18, 0.28)
    ctx.move_to(p3_x + 15, p3_y + 22)
    ctx.show_text("C. Field-Specific Annotation Completeness (N = 483 Active EB Neurons):")

    fields = [
        ("root_id Row Match", "483 / 483 (100.0%)", (0.15, 0.45, 0.25)),
        ("hemibrain_type", "479 / 483 (99.2%)", (0.15, 0.45, 0.25)),
        ("cell_sub_class", "332 / 483 (68.7%)", (0.70, 0.40, 0.15)),
        ("cell_type", "15 / 483 (3.1%)", (0.75, 0.20, 0.20)),
    ]

    for f_idx, (f_name, f_val, f_col) in enumerate(fields):
        fx = p3_x + 15 + f_idx * 245
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(fx, p3_y + 44)
        ctx.show_text(f"{f_name}:")

        ctx.set_source_rgb(f_col[0], f_col[1], f_col[2])
        ctx.move_to(fx + 120, p3_y + 44)
        ctx.show_text(f_val)

    # Epistemic note at bottom of Panel C
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.20, 0.25, 0.35)
    ctx.move_to(p3_x + 15, p3_y + 70)
    ctx.show_text("Epistemic Guardrails:")
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(p3_x + 155, p3_y + 70)
    ctx.show_text("Descriptive anatomy only. No cell-type permutation null was run; these counts do NOT demonstrate statistical partner preference.")
    ctx.move_to(p3_x + 15, p3_y + 86)
    ctx.show_text("Labels represent base hemibrain types and are not equated with finer morphotypes. Predicted GABA identity does not confirm functional inhibition.")


def main() -> None:
    print("=" * 80)
    print("PHASE 8: GENERATING PORTFOLIO PRESENTATION FIGURES (SVG & PNG)")
    print("=" * 80)

    if cairo is None:
        print("Error: cairo module is required for figure rendering.")
        sys.exit(1)

    # 1. Figure 1: Conditional Associations Across Models
    f1_svg = PHASE8_DIR / "figure1_conditional_gaba_associations.svg"
    f1_png = PHASE8_DIR / "figure1_conditional_gaba_associations.png"
    w1, h1 = 980, 520

    print(f"\n[1/2] Rendering Figure 1 ({w1}x{h1})...")
    # Render SVG
    svg_surf1 = cairo.SVGSurface(str(f1_svg), w1, h1)
    ctx1_svg = cairo.Context(svg_surf1)
    draw_figure1(ctx1_svg, w1, h1)
    svg_surf1.finish()
    print(f"  Generated SVG: {f1_svg} ({f1_svg.stat().st_size:,} bytes)")

    # Render PNG
    img_surf1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, w1, h1)
    ctx1_png = cairo.Context(img_surf1)
    draw_figure1(ctx1_png, w1, h1)
    img_surf1.write_to_png(str(f1_png))
    print(f"  Generated PNG: {f1_png} ({f1_png.stat().st_size:,} bytes)")

    # 2. Figure 2: Descriptive Cell-Type Composition
    f2_svg = PHASE8_DIR / "figure2_descriptive_cell_type_composition.svg"
    f2_png = PHASE8_DIR / "figure2_descriptive_cell_type_composition.png"
    w2, h2 = 1100, 605

    print(f"\n[2/2] Rendering Figure 2 ({w2}x{h2})...")
    # Render SVG
    svg_surf2 = cairo.SVGSurface(str(f2_svg), w2, h2)
    ctx2_svg = cairo.Context(svg_surf2)
    draw_figure2(ctx2_svg, w2, h2)
    svg_surf2.finish()
    print(f"  Generated SVG: {f2_svg} ({f2_svg.stat().st_size:,} bytes)")

    # Render PNG
    img_surf2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, w2, h2)
    ctx2_png = cairo.Context(img_surf2)
    draw_figure2(ctx2_png, w2, h2)
    img_surf2.write_to_png(str(f2_png))
    print(f"  Generated PNG: {f2_png} ({f2_png.stat().st_size:,} bytes)")

    print("\nFigure generation successfully completed.")


if __name__ == "__main__":
    main()

