#!/usr/bin/env python3
"""
generate_fb_figures.py

Renders publication-grade vector SVG and 300dpi PNG figures for the VectorWing project,
fully adhering to Phase 10 specifications:
1. figure1_network_and_pipeline_overview (.svg & .png):
   - FB connectome graph summary (N=2,465, E=46,903, M=5,435), reciprocal dyad definition,
     and 4-stage data ingestion / analysis pipeline flowchart.
2. figure2_transmitter_associations (.svg & .png):
   - Observed mutual dyad counts across all transmitter pairings, observed vs degree-stratified
     null distributions (554 vs 97.4), and contrast between ACh-GABA enrichment and GABA-GABA depletion.
3. figure3_neuronal_and_layer_organization (.svg & .png):
   - Multi-panel anatomical dissection: Columnar-Tangential dominance (99.5%), strict 100% directional
     chemical polarity, horizontal layer localization (99.1% in L4/5), and top cell-type microcircuits.
4. figure4_statistical_robustness_comparison (.svg & .png):
   - Forest plot comparing discrete and continuous k-NN micro-strata with Monte Carlo simulation precision,
     MCMC slow-mixing drift diagnosis, and transmitter confidence threshold sensitivity.
5. figure5_dynamical_model_stress_testing (.svg & .png):
   - 16-column rate model equations & architecture, linear subtractive attenuation curves,
     intact vs ablated spatial bumps, and sensory noise decoding error.
6. figure6_eb_vs_fb_circuit_contrast (.svg & .png):
   - Architectural dichotomy between 1D heading (EB ring attractor) and 2D vector steering (FB).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

if "/usr/lib/python3/dist-packages" not in sys.path:
    sys.path.append("/usr/lib/python3/dist-packages")

try:
    import cairo
except ImportError:
    cairo = None

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIG_DIR = REPO_ROOT / "results" / "figures"
FB_CACHE = REPO_ROOT / "data" / "fb_node_covariates.json"
if not FB_CACHE.exists():
    FB_CACHE = REPO_ROOT.parent / "fb_vector_reciprocity" / "data" / "fb_node_covariates.json"
STUDY_JSON = REPO_ROOT / "results" / "fb_controlled_study_results.json"
ANATOMY_JSON = REPO_ROOT / "results" / "fb_layer_column_anatomy.json"
KNN_JSON = REPO_ROOT / "results" / "fb_continuous_degree_results.json"
SIM_JSON = REPO_ROOT / "results" / "fb_dynamical_simulation_results.json"
MCMC_JSON = REPO_ROOT / "results" / "mcmc_forensic_diagnosis.json"
DYN_STRESS_JSON = REPO_ROOT / "results" / "dynamics_stress_test_results.json"
SENS_JSON = REPO_ROOT / "results" / "sensitivity_and_controls_results.json"


def draw_figure1(ctx: cairo.Context, w: int, h: int, cache_data: dict) -> None:
    """Figure 1: Connectomic Architecture of FB & Data Ingestion Pipeline Overview."""
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
    ctx.show_text("Figure 1: Connectomic Architecture of the Adult Drosophila Fan-Shaped Body & Pipeline")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("FAFB v783 Connectome (16.8M rows) | Threshold w >= 5 | Canonical Mutual Dyad Extraction")

    # Panel A: Graph Summary Metrics (Left)
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
    ctx.show_text("A. FB Graph Baseline (w >= 5)")

    metrics = [
        ("Active Neurons (N)", "2,465", "100% FlyWire v2.1.0 mapped"),
        ("Directed Edges (E)", "46,903", "598,942 physical synapses"),
        ("Mutual Dyads (M)", "5,435", "10,870 reciprocal edges"),
        ("Synapse Threshold", "w >= 5", "ultrastructural noise filter"),
        ("Autapses Excluded", "0 self-loops", "pre != post enforced"),
    ]
    for mi, (label, val, note) in enumerate(metrics):
        my = pA_y + 55 + mi * 36
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.30, 0.35, 0.45)
        ctx.move_to(pA_x + 15, my + 10)
        ctx.show_text(label)

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.10, 0.20, 0.40)
        ctx.move_to(pA_x + 150, my + 10)
        ctx.show_text(val)

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.50, 0.55, 0.65)
        ctx.move_to(pA_x + 15, my + 24)
        ctx.show_text(note)

    # Panel B: Reciprocal Dyad Definition (Middle)
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
    ctx.show_text("B. Mutual Dyad Mathematics")

    # Diagram of bidirectional dyad
    ctx.set_source_rgb(0.20, 0.45, 0.85)
    ctx.arc(pB_x + 65, pB_y + 85, 18, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(14)
    ctx.move_to(pB_x + 59, pB_y + 90)
    ctx.show_text("u")

    ctx.set_source_rgb(0.85, 0.30, 0.20)
    ctx.arc(pB_x + 245, pB_y + 85, 18, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.move_to(pB_x + 239, pB_y + 90)
    ctx.show_text("v")

    # Forward arrow u -> v
    ctx.set_source_rgb(0.25, 0.30, 0.40)
    ctx.set_line_width(2.0)
    ctx.move_to(pB_x + 88, pB_y + 75)
    ctx.line_to(pB_x + 222, pB_y + 75)
    ctx.stroke()
    ctx.move_to(pB_x + 222, pB_y + 75)
    ctx.line_to(pB_x + 214, pB_y + 70)
    ctx.line_to(pB_x + 214, pB_y + 80)
    ctx.fill()

    # Backward arrow v -> u
    ctx.move_to(pB_x + 222, pB_y + 95)
    ctx.line_to(pB_x + 88, pB_y + 95)
    ctx.stroke()
    ctx.move_to(pB_x + 88, pB_y + 95)
    ctx.line_to(pB_x + 96, pB_y + 90)
    ctx.line_to(pB_x + 96, pB_y + 100)
    ctx.fill()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.move_to(pB_x + 115, pB_y + 68)
    ctx.show_text("w(u,v) >= 5")
    ctx.move_to(pB_x + 115, pB_y + 110)
    ctx.show_text("w(v,u) >= 5")

    # Reciprocity Formulas
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.15, 0.30, 0.60)
    ctx.move_to(pB_x + 15, pB_y + 145)
    ctx.show_text("Edge Reciprocity (R_edge = 2M / E):")
    ctx.set_font_size(14)
    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.move_to(pB_x + 15, pB_y + 168)
    ctx.show_text("23.1755%  (Rank #6 / 79 neuropils)")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.15, 0.30, 0.60)
    ctx.move_to(pB_x + 15, pB_y + 195)
    ctx.show_text("Dyad Reciprocity (R_dyad = M / [E - M]):")
    ctx.set_font_size(13)
    ctx.set_source_rgb(0.10, 0.50, 0.30)
    ctx.move_to(pB_x + 15, pB_y + 216)
    ctx.show_text("13.1065%  (M = 5,435 dyads)")

    # Panel C: Pipeline Flowchart (Right)
    pC_x, pC_y, pC_w, pC_h = 735, 110, 320, 240
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
    ctx.move_to(pC_x + 15, pC_y + 28)
    ctx.show_text("C. Analysis Pipeline Flow")

    stages = [
        ("1. Connectome Ingestion", "FAFB v783 Feather (16.8M synapses, 258 batches)"),
        ("2. Subgraph Extraction", "FB neuropil filter, w >= 5, autapses segregated"),
        ("3. Consensus Cell Typing", "Consensus NT predictions + FlyWire v2.1.0 metadata"),
        ("4. Degree Null Models", "Discrete strata & continuous k-NN micro-stratification"),
    ]
    for si, (stitle, sdesc) in enumerate(stages):
        sy = pC_y + 48 + si * 46
        # Box
        ctx.set_source_rgb(0.90, 0.93, 0.97)
        ctx.rectangle(pC_x + 12, sy, pC_w - 24, 38)
        ctx.fill()
        ctx.set_source_rgb(0.75, 0.80, 0.90)
        ctx.set_line_width(1.0)
        ctx.rectangle(pC_x + 12, sy, pC_w - 24, 38)
        ctx.stroke()

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.15, 0.25, 0.45)
        ctx.move_to(pC_x + 20, sy + 15)
        ctx.show_text(stitle)

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(8.5)
        ctx.set_source_rgb(0.35, 0.40, 0.50)
        ctx.move_to(pC_x + 20, sy + 29)
        ctx.show_text(sdesc)

    # Bottom Summary Card
    card_y = 370
    ctx.set_source_rgb(0.92, 0.95, 0.98)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.fill()
    ctx.set_source_rgb(0.78, 0.84, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(65, card_y + 25)
    ctx.show_text("Mathematical & Architectural Invariants of the Empirical Fan-Shaped Body:")

    points = [
        "• 64-bit precision: Root IDs > 7.2 x 10^17 preserve full precision without IEEE-754 double floating truncation.",
        "• Exact degree accounting: sum(in_deg) == 46,903, sum(out_deg) == 46,903, sum(m_deg) == 10,870 (2*M).",
        "• High reciprocity: FB edge reciprocity (23.18%) is over 2.5x the whole-brain median (8.9%), ranking #6 out of 79 neuropils.",
        "• Canonical extraction: endpoints u < v guarantee every mutual dyad is uniquely counted without duplicate indexing.",
    ]
    for pi, pt in enumerate(points):
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(65, card_y + 45 + pi * 18)
        ctx.show_text(pt)


def draw_figure2(ctx: cairo.Context, w: int, h: int, study_data: dict) -> None:
    """Figure 2: Observed Transmitter-Pair Associations & Degree-Stratified Null Distribution."""
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
    ctx.show_text("Figure 2: Neurotransmitter Pairing Profile of Fan-Shaped Body Mutual Dyads")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("5,435 Mutual Dyads | Whole-Cell Neurotransmitter Consensus (Eckstein et al., 2024) | Degree-Stratified Null Models")

    # Panel A: Mutual Dyads Across Transmitter Pairings (Left)
    pA_x, pA_y, pA_w, pA_h = 45, 110, 480, 240
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
    ctx.show_text("A. Observed Mutual Dyads Across Transmitter Pairs")

    top_pairs = [
        ("ach_glut (Excitatory-Glutamate)", 2267, 41.71, 0.20, 0.50, 0.80),
        ("glut_glut (Homotypic Glutamate)", 968, 17.81, 0.35, 0.65, 0.65),
        ("ach_gaba (Heterotypic Exc-Inh)", 554, 10.19, 0.85, 0.20, 0.20),
        ("ach_ach (Homotypic Cholinergic)", 456, 8.39, 0.30, 0.60, 0.85),
        ("gaba_glut (Inhibitory-Glutamate)", 429, 7.89, 0.60, 0.60, 0.70),
        ("gaba_gaba (Homotypic Inhibitory)", 6, 0.11, 0.75, 0.75, 0.75),
    ]

    for pi, (plabel, pcount, ppct, cr, cg, cb) in enumerate(top_pairs):
        py = pA_y + 50 + pi * 29
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(pA_x + 15, py + 12)
        ctx.show_text(plabel)

        # Bar
        bar_w = (pcount / 2267.0) * 160
        ctx.set_source_rgb(cr, cg, cb)
        ctx.rectangle(pA_x + 220, py + 2, max(bar_w, 2), 14)
        ctx.fill()

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(pA_x + 230 + max(bar_w, 2), py + 14)
        ctx.show_text(f"{pcount} ({ppct:.1f}%)")

    # Panel B: Observed vs Null Distribution for ACh-GABA (Right)
    pB_x, pB_y, pB_w, pB_h = 550, 110, 505, 240
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
    ctx.show_text("B. ACh-GABA Observed (554) vs Degree-Stratified Null")

    # Draw null distribution bell curve
    # Null mean = 97.4, sd = 28.1, observed = 554
    # Map x: [0, 600] -> [pB_x + 40, pB_x + 460]
    def map_x(v: float) -> float:
        return pB_x + 40 + (v / 600.0) * 420

    # Axes
    ctx.set_source_rgb(0.80, 0.85, 0.90)
    ctx.set_line_width(1.0)
    ctx.move_to(map_x(0), pB_y + 180)
    ctx.line_to(map_x(600), pB_y + 180)
    ctx.stroke()

    for tick in [0, 100, 200, 300, 400, 500, 600]:
        tx = map_x(tick)
        ctx.move_to(tx, pB_y + 180)
        ctx.line_to(tx, pB_y + 185)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(tx - 8, pB_y + 198)
        ctx.show_text(str(tick))

    # Draw Gaussian null curve
    ctx.set_source_rgb(0.25, 0.45, 0.75)
    ctx.set_line_width(2.0)
    mean_null = 97.4
    sd_null = 28.1
    pts = []
    for step_v in range(0, 250, 2):
        z = (step_v - mean_null) / sd_null
        gauss_y = math.exp(-0.5 * z * z)
        # map to height
        plot_y = pB_y + 180 - (gauss_y * 100)
        pts.append((map_x(step_v), plot_y))

    ctx.move_to(pts[0][0], pts[0][1])
    for px, py in pts[1:]:
        ctx.line_to(px, py)
    ctx.stroke()

    # Fill under null curve
    ctx.set_source_rgba(0.25, 0.45, 0.75, 0.25)
    ctx.move_to(pts[0][0], pB_y + 180)
    for px, py in pts:
        ctx.line_to(px, py)
    ctx.line_to(pts[-1][0], pB_y + 180)
    ctx.close_path()
    ctx.fill()

    # Null mean text
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.15, 0.35, 0.65)
    ctx.move_to(map_x(mean_null) - 40, pB_y + 65)
    ctx.show_text(f"Null Mean: {mean_null:.1f} ± {sd_null:.1f}")
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(9)
    ctx.move_to(map_x(mean_null) - 40, pB_y + 78)
    ctx.show_text("95% Range: [48, 157]")

    # Observed point at 554
    obs_x = map_x(554)
    ctx.set_source_rgb(0.85, 0.15, 0.15)
    ctx.set_line_width(2.5)
    ctx.move_to(obs_x, pB_y + 50)
    ctx.line_to(obs_x, pB_y + 180)
    ctx.stroke()

    ctx.arc(obs_x, pB_y + 50, 5.5, 0, 2 * math.pi)
    ctx.fill()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    ctx.set_source_rgb(0.85, 0.15, 0.15)
    ctx.move_to(obs_x - 110, pB_y + 60)
    ctx.show_text("Observed = 554 dyads")
    ctx.set_font_size(10)
    ctx.move_to(obs_x - 110, pB_y + 75)
    ctx.show_text("Enrichment: 5.69x (Z = +16.2)")
    ctx.move_to(obs_x - 110, pB_y + 88)
    ctx.show_text("Empirical p = 0.000500")

    # Bottom Callout Card
    card_y = 370
    ctx.set_source_rgb(0.92, 0.95, 0.98)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.fill()
    ctx.set_source_rgb(0.78, 0.84, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(65, card_y + 25)
    ctx.show_text("Key Connectomic Insights: Chemical Pairing Inversion")

    summary_bullets = [
        "• Severe Homotypic GABA Depletion: While GABA-GABA reciprocity dominates the Ellipsoid Body (74.3%), it is nearly absent in the FB (6 dyads, 0.11%, Z = -8.4).",
        "• Massive Heterotypic Reciprocity: Excitatory ACh and inhibitory GABA form 554 reciprocal pairs, exceeding null degree expectation by > 5.4-fold.",
        "• High Chemical Specificity: Out of all 21 possible transmitter pairings, ACh-GABA exhibits the highest statistical enrichment across all degree-conditioned null models.",
        "• Family-Wise FDR Controlled: Benjamini-Hochberg false discovery rate across all transmitter combinations remains q < 0.003.",
    ]
    for bi, bullet in enumerate(summary_bullets):
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(65, card_y + 45 + bi * 18)
        ctx.show_text(bullet)


def draw_figure3(ctx: cairo.Context, w: int, h: int, anat_data: dict) -> None:
    """Figure 3: Cellular Substrate, 100% Directional Polarity, and Layer 4/5 Specialization."""
    # This renders the multi-panel anatomy figure
    ctx.set_source_rgb(0.985, 0.988, 0.995)
    ctx.paint()

    ctx.set_source_rgb(0.82, 0.86, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 58)
    ctx.show_text("Figure 3: Cellular Substrate, 100% Directional Polarity, and Layer Specialization")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("FlyWire v2.1.0 Annotations | 100% Active Node Coverage (2,465/2,465) | 554 ACh <-> GABA Mutual Dyads")

    # Panel A: Morphology Pairing (Left)
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

        bw = (bcnt / total_cnt) * 160 if total_cnt > 0 else 0
        ctx.set_source_rgb(cr, cg, cb)
        ctx.rectangle(pA_x + 15, by + 18, max(bw, 2), 14)
        ctx.fill()

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
    ctx.show_text("B. Horizontal Layer Localization")

    l5_cnt = anat_data["ach_gaba_layers"]["Layer_5"]
    l4_cnt = anat_data["ach_gaba_layers"]["Layer_4"]
    other_cnt = sum(cnt for k, cnt in anat_data["ach_gaba_layers"].items() if k not in ["Layer_4", "Layer_5"])

    layer_bars = [
        ("Layer 5 (Ventral premotor hub)", l5_cnt, 0.85, 0.30, 0.20),
        ("Layer 4 (Intermediate vector)", l4_cnt, 0.25, 0.55, 0.80),
        ("Other Layers (1-3, 6-9, Unassigned)", other_cnt, 0.70, 0.75, 0.80),
    ]
    for li, (llabel, lcnt, cr, cg, cb) in enumerate(layer_bars):
        ly = pB_y + 60 + li * 45
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(pB_x + 15, ly + 12)
        ctx.show_text(llabel)

        lw = (lcnt / 554.0) * 180
        ctx.set_source_rgb(cr, cg, cb)
        ctx.rectangle(pB_x + 15, ly + 18, max(lw, 2), 14)
        ctx.fill()

        lpct = (lcnt / 554.0) * 100
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(pB_x + 25 + max(lw, 2), ly + 30)
        ctx.show_text(f"{lcnt} ({lpct:.1f}%)")

    # Layer 4&5 callout
    ctx.set_source_rgb(0.90, 0.93, 0.97)
    ctx.rectangle(pB_x + 15, pB_y + 195, pB_w - 30, 32)
    ctx.fill()
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.10, 0.40, 0.70)
    ctx.move_to(pB_x + 22, pB_y + 215)
    ctx.show_text("Layers 4 & 5 Combined: 99.10% (549 / 554 dyads)")

    # Panel C: Top Specific Microcircuits (Right)
    pC_x, pC_y, pC_w, pC_h = 735, 110, 320, 240
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
    ctx.move_to(pC_x + 15, pC_y + 28)
    ctx.show_text("C. Dominant Specific Microcircuits")

    top_pairs = [
        ("FB4A <-> vDeltaA (L4)", 150, 27.08),
        ("FB5A <-> FC2C (L5)", 131, 23.65),
        ("FB5A <-> FC2B (L5)", 102, 18.41),
        ("FB5A <-> FC2A (L5)", 39, 7.04),
        ("FB5A <-> hDeltaM (L5)", 32, 5.78),
        ("FB5I2 <-> vDeltaF (L5)", 29, 5.23),
    ]
    for ti, (tlabel, tcnt, tpct) in enumerate(top_pairs):
        ty = pC_y + 50 + ti * 30
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(pC_x + 15, ty + 10)
        ctx.show_text(tlabel)

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.10, 0.30, 0.60)
        ctx.move_to(pC_x + 225, ty + 10)
        ctx.show_text(f"{tcnt} ({tpct:.1f}%)")

    # Bottom Summary Card
    card_y = 370
    ctx.set_source_rgb(0.92, 0.95, 0.98)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.fill()
    ctx.set_source_rgb(0.78, 0.84, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(65, card_y + 25)
    ctx.show_text("Biological Architecture Summary: Premotor Steering Clamps")

    anatomical_bullets = [
        "• Strict Asymmetry: 100.0% of Columnar-Tangential reciprocal loops have Columnar=ACh and Tangential=GABA (0 reverse dyads).",
        "• Dense Layer 4 & 5 Focusing: Over 99% of loops are concentrated in Layers 4 & 5, which host the premotor steering outputs (e.g. PFL3).",
        "• Primary Microcircuits: FB4A <-> vDeltaA (150 dyads) and FB5A <-> FC2 (272 dyads across sub-types) form 76.2% of all reciprocal feedback.",
        "• Circuit Hypothesis: Tangential inhibitory inputs cross-clamp columnar channels to dynamically shape gain during active motor steering.",
    ]
    for bi, bullet in enumerate(anatomical_bullets):
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(65, card_y + 45 + bi * 18)
        ctx.show_text(bullet)


def draw_figure4(ctx: cairo.Context, w: int, h: int, study_data: dict, knn_data: dict, mcmc_data: dict, sens_data: dict) -> None:
    """Figure 4: Statistical Robustness: Degree Conditioning, MCMC Audit & Confidence Sensitivity."""
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
    ctx.show_text("Figure 4: Statistical Robustness: Degree Conditioning, MCMC Audit & Confidence Sensitivity")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("Evaluation Across 6 Valid Null Models, MCMC Mixing Diagnosis, and Transmitter Confidence Filtering")

    # Panel A: Forest Plot of Valid Null Models (Left)
    pA_x, pA_y, pA_w, pA_h = 45, 110, 520, 240
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
    ctx.show_text("A. Enrichment Ratios Across Null Models")

    # Data rows: point estimates with Monte Carlo 95% simulation bounds
    models_list = [
        ("Model 1: Mutual Quartiles", 5.92, 5.85, 5.99, "Coarse 4 strata"),
        ("Model 2: Joint In x Out Tertiles", 5.69, 5.62, 5.76, "Coarse 9 strata"),
        ("Model 3: Joint In x Out Medians", 5.45, 5.39, 5.51, "Coarse 4 strata"),
        ("Model 4: Total Degree Quintiles", 4.96, 4.90, 5.02, "Coarse 5 strata"),
        ("Benchmark A: k-NN (k=16)", 2.75, 2.70, 2.79, "Fine 154 strata"),
        ("Benchmark B: k-NN (k=8)", 2.53, 2.49, 2.57, "Fine 308 strata"),
    ]

    # Map ratio [1.0, 7.0] -> [pA_x + 230, pA_x + 480]
    def map_ratio(r: float) -> float:
        return pA_x + 230 + ((r - 1.0) / 6.0) * 250

    # Grid line at 1.0 (null line)
    ctx.set_source_rgb(0.80, 0.85, 0.90)
    ctx.set_line_width(1.0)
    null_x = map_ratio(1.0)
    ctx.move_to(null_x, pA_y + 45)
    ctx.line_to(null_x, pA_y + 215)
    ctx.stroke()

    for r_tick in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]:
        tx = map_ratio(r_tick)
        ctx.move_to(tx, pA_y + 215)
        ctx.line_to(tx, pA_y + 220)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(tx - 8, pA_y + 228)
        ctx.show_text(f"{r_tick:.0f}x")

    for ri, (mname, rpt, rlo, rhi, mnote) in enumerate(models_list):
        ry = pA_y + 52 + ri * 26
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if ri >= 4 else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.15, 0.20, 0.30)
        ctx.move_to(pA_x + 15, ry + 4)
        ctx.show_text(mname)

        # CI line (Monte Carlo simulation precision)
        x_lo = map_ratio(rlo)
        x_hi = map_ratio(rhi)
        x_pt = map_ratio(rpt)

        if ri < 4:
            ctx.set_source_rgb(0.20, 0.45, 0.80)
        else:
            ctx.set_source_rgb(0.85, 0.25, 0.25)
        ctx.set_line_width(2.5)
        ctx.move_to(x_lo, ry)
        ctx.line_to(x_hi, ry)
        ctx.stroke()

        # Point
        ctx.arc(x_pt, ry, 4.0, 0, 2 * math.pi)
        ctx.fill()

        # Text
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(9)
        ctx.move_to(x_hi + 6, ry + 3)
        ctx.show_text(f"{rpt:.2f}x")

    # Methodological footnote
    ctx.select_font_face("Sans", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(8)
    ctx.set_source_rgb(0.45, 0.50, 0.60)
    ctx.move_to(pA_x + 15, pA_y + 233)
    ctx.show_text("* Error bars: 95% Monte Carlo precision (SE_MC < 0.05x). Biological CI unidentified from N=1.")

    # Panel B: Forensic MCMC Diagnosis (Right)
    pB_x, pB_y, pB_w, pB_h = 585, 110, 520, 240
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
    ctx.show_text("B. Forensic Audit: MCMC Uniform Stationary Drift")

    # MCMC history plot
    # Steps: 0 to 150,000 -> [pB_x + 60, pB_x + 480]
    # Counts: [0, 600] -> [pB_y + 190, pB_y + 55]
    def map_step(s: float) -> float:
        return pB_x + 60 + (s / 150000.0) * 410

    def map_cnt(c: float) -> float:
        return pB_y + 190 - (c / 600.0) * 135

    # Axes
    ctx.set_source_rgb(0.80, 0.85, 0.90)
    ctx.set_line_width(1.0)
    ctx.move_to(map_step(0), map_cnt(0))
    ctx.line_to(map_step(150000), map_cnt(0))
    ctx.stroke()

    for stick in [0, 50000, 100000, 150000]:
        sx = map_step(stick)
        ctx.move_to(sx, map_cnt(0))
        ctx.line_to(sx, map_cnt(0) + 5)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(sx - 15, map_cnt(0) + 16)
        ctx.show_text(f"{stick//1000}k")

    # True uniform stationary expectation (393.8 dyads)
    null_y = map_cnt(393.8)
    ctx.set_source_rgba(0.20, 0.50, 0.80, 0.8)
    ctx.set_line_width(1.5)
    ctx.move_to(map_step(0), null_y)
    ctx.line_to(map_step(150000), null_y)
    ctx.stroke()
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(9)
    ctx.move_to(map_step(10000), null_y - 5)
    ctx.show_text("Theoretical Uniform Stationary Mean (393.8 dyads)")

    # Model 1 Mutual Quartiles expectation (93.6 dyads) shown for contrast
    m1_y = map_cnt(93.6)
    ctx.set_source_rgba(0.50, 0.50, 0.50, 0.5)
    ctx.set_line_width(1.0)
    ctx.set_dash([4.0, 4.0])
    ctx.move_to(map_step(0), m1_y)
    ctx.line_to(map_step(150000), m1_y)
    ctx.stroke()
    ctx.set_dash([])
    ctx.move_to(map_step(10000), m1_y - 4)
    ctx.show_text("Model 1 Degree-Stratified Mean (93.6 dyads)")

    # Empirical trajectory: (0, 554), (25k, 489), (50k, 454), (75k, 489), (100k, 460), (125k, 444), (150k, 420)
    emp_pts = [(0, 554), (25000, 489), (50000, 454), (75000, 489), (100000, 460), (125000, 444), (150000, 420)]
    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.set_line_width(2.0)
    ctx.move_to(map_step(emp_pts[0][0]), map_cnt(emp_pts[0][1]))
    for s, c in emp_pts[1:]:
        ctx.line_to(map_step(s), map_cnt(c))
    ctx.stroke()

    # Random trajectory: (0, 368), (25k, 379), (50k, 376), (75k, 358), (100k, 375), (125k, 405), (150k, 406)
    rnd_pts = [(0, 368), (25000, 379), (50000, 376), (75000, 358), (100000, 375), (125000, 405), (150000, 406)]
    ctx.set_source_rgb(0.25, 0.65, 0.35)
    ctx.move_to(map_step(rnd_pts[0][0]), map_cnt(rnd_pts[0][1]))
    for s, c in rnd_pts[1:]:
        ctx.line_to(map_step(s), map_cnt(c))
    ctx.stroke()

    # Labels on plot
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.move_to(map_step(2000), map_cnt(554) - 8)
    ctx.show_text("Empirical Init (554 -> 420)")

    ctx.set_source_rgb(0.25, 0.65, 0.35)
    ctx.move_to(map_step(2000), map_cnt(368) + 16)
    ctx.show_text("Random Init (368 -> 406)")

    # Bottom Callout Card
    card_y = 370
    ctx.set_source_rgb(0.92, 0.95, 0.98)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.fill()
    ctx.set_source_rgb(0.78, 0.84, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(65, card_y + 25)
    ctx.show_text("Rigorous Methodological Verdict:")

    stat_bullets = [
        "• Attenuation Under Fine Micro-Stratification: Coarse degree models yield ~5.7x; fine-grained k-NN micro-strata (k=8, 308 strata) attenuate to 2.53x conditional association (p = 0.000999).",
        "• MCMC Mathematical Proof: Transition matrix T is doubly stochastic (T[X->X'] = T[X'->X]), proving stationary distribution is UNIFORM permutation (mean 393.8 dyads).",
        "• Reported 1.20x MCMC Excess Withdrawn: The reported 1.20x (~460 dyads) was an artifact of slow mixing drifting from 554 toward 393.8 (93.3% reject rate).",
        "• Tangential Confidence Floor: GABAergic tangential neurons have a maximum predicted confidence of 0.7873 (median 0.7812); threshold >= 0.80 excises all dyads.",
    ]
    for bi, bullet in enumerate(stat_bullets):
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(65, card_y + 45 + bi * 18)
        ctx.show_text(bullet)


def draw_figure5(ctx: cairo.Context, w: int, h: int, sim_data: dict, stress_data: dict) -> None:
    """Figure 5: 16-Column Recurrent Attractor Dynamics, Linear Subtractive Attenuation & Noise Sensitivity."""
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
    ctx.show_text("Figure 5: Rate-Based Circuit Dynamics: Linear Subtractive Feedback & Stress-Testing")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("16-Column Recurrent Attractor ODE | Subtractive Feedback vs Divisive Normalization | Noise Perturbation")

    # Panel A: Linear Gain Curves (Left)
    pA_x, pA_y, pA_w, pA_h = 45, 110, 480, 240
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
    ctx.show_text("A. Linear Subtractive Feedback (Peak Rate vs Drive)")

    # Drive [0, 30] -> [pA_x + 45, pA_x + 440]
    # Peak Rate [0, 450] -> [pA_y + 200, pA_y + 50]
    def map_drive(d: float) -> float:
        return pA_x + 45 + (d / 30.0) * 395

    def map_rate(r: float) -> float:
        return pA_y + 200 - (r / 450.0) * 150

    # Axes
    ctx.set_source_rgb(0.80, 0.85, 0.90)
    ctx.set_line_width(1.0)
    ctx.move_to(map_drive(0), map_rate(0))
    ctx.line_to(map_drive(30), map_rate(0))
    ctx.stroke()

    for dtick in [0, 10, 20, 30]:
        dx = map_drive(dtick)
        ctx.move_to(dx, map_rate(0))
        ctx.line_to(dx, map_rate(0) + 5)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.45, 0.50, 0.60)
        ctx.move_to(dx - 6, map_rate(0) + 16)
        ctx.show_text(str(dtick))

    # Plot gain curves for W_inh = 0.0 (ablated), 0.50, 0.85 (intact), 2.0
    curves = [
        ("W_inh = 0.00 (Ablated)", [(1, 14.9), (10, 148.7), (20, 297.4), (30, 446.1)], 0.85, 0.20, 0.20),
        ("W_inh = 0.50", [(1, 2.4), (10, 24.0), (20, 48.0), (30, 72.1)], 0.80, 0.55, 0.20),
        ("W_inh = 0.85 (Intact Baseline)", [(1, 1.5), (10, 15.3), (20, 30.6), (30, 45.9)], 0.20, 0.50, 0.85),
        ("W_inh = 2.00 (Strong Feedback)", [(1, 0.8), (10, 7.8), (20, 15.6), (30, 23.5)], 0.30, 0.65, 0.40),
    ]

    for clabel, cpts, cr, cg, cb in curves:
        ctx.set_source_rgb(cr, cg, cb)
        ctx.set_line_width(2.0)
        ctx.move_to(map_drive(cpts[0][0]), map_rate(cpts[0][1]))
        for d, r in cpts[1:]:
            ctx.line_to(map_drive(d), map_rate(r))
        ctx.stroke()

        for d, r in cpts:
            ctx.arc(map_drive(d), map_rate(r), 3.5, 0, 2 * math.pi)
            ctx.fill()

    # Labels for curves
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(9)
    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.move_to(map_drive(18), map_rate(320))
    ctx.show_text("Ablated (W_inh = 0.0, Slope = 14.9)")

    ctx.set_source_rgb(0.20, 0.50, 0.85)
    ctx.move_to(map_drive(18), map_rate(70))
    ctx.show_text("Intact (W_inh = 0.85, Slope = 1.53)")

    # Panel B: Spatial Tuning Bump & Sensory Noise (Right)
    pB_x, pB_y, pB_w, pB_h = 550, 110, 505, 240
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
    ctx.show_text("B. Spatial Tuning Bumps & Noise Sensitivity")

    # Column bump: 16 columns -> [pB_x + 35, pB_x + 240]
    # Height [0, 320 Hz]
    def map_col(c: int) -> float:
        return pB_x + 35 + (c / 15.0) * 190

    # Draw intact bump (sharp, 30.6 Hz)
    # Peak at column 8
    intact_rates = [0.0, 0.0, 0.0, 0.0, 0.0, 1.2, 8.5, 25.1, 30.6, 25.1, 8.5, 1.2, 0.0, 0.0, 0.0, 0.0]
    # Ablated rates (scaled by 0.1 for visibility on same axis or dual)
    ablated_rates_div10 = [0.0, 2.0, 6.0, 12.0, 19.0, 25.0, 28.5, 29.7, 29.7, 28.5, 25.0, 19.0, 12.0, 6.0, 2.0, 0.0]

    ctx.set_source_rgb(0.20, 0.50, 0.85)
    ctx.set_line_width(2.0)
    ctx.move_to(map_col(0), pB_y + 190 - intact_rates[0] * 3.5)
    for ci in range(1, 16):
        ctx.line_to(map_col(ci), pB_y + 190 - intact_rates[ci] * 3.5)
    ctx.stroke()

    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.set_line_width(1.5)
    ctx.move_to(map_col(0), pB_y + 190 - ablated_rates_div10[0] * 3.5)
    for ci in range(1, 16):
        ctx.line_to(map_col(ci), pB_y + 190 - ablated_rates_div10[ci] * 3.5)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(9)
    ctx.set_source_rgb(0.20, 0.50, 0.85)
    ctx.move_to(pB_x + 35, pB_y + 70)
    ctx.show_text("Intact Bump (Peak 30.6 Hz, FWHM 90°)")

    ctx.set_source_rgb(0.85, 0.20, 0.20)
    ctx.move_to(pB_x + 35, pB_y + 85)
    ctx.show_text("Ablated Bump (Peak 297 Hz, FWHM 135°)")

    # Noise error table on right of Panel B
    ctx.set_source_rgb(0.90, 0.93, 0.97)
    ctx.rectangle(pB_x + 255, pB_y + 50, 235, 140)
    ctx.fill()
    ctx.set_source_rgb(0.80, 0.85, 0.90)
    ctx.set_line_width(1.0)
    ctx.rectangle(pB_x + 255, pB_y + 50, 235, 140)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    ctx.set_source_rgb(0.15, 0.25, 0.45)
    ctx.move_to(pB_x + 265, pB_y + 68)
    ctx.show_text("Steering Decoding Error vs Noise:")

    noise_rows = [
        ("Noise 0% (Noiseless)", "< 0.8°", "Artifact of symmetry"),
        ("Noise 5%", "1.52°", "Robust centroid"),
        ("Noise 10%", "2.38°", "Linear degradation"),
        ("Noise 20%", "5.65°", "Realistic sensory noise"),
        ("Noise 30%", "8.69°", "Significant jitter"),
    ]
    for ni, (nlevel, nerr, nnote) in enumerate(noise_rows):
        ny = pB_y + 86 + ni * 19
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(pB_x + 265, ny)
        ctx.show_text(nlevel)

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.move_to(pB_x + 375, ny)
        ctx.show_text(nerr)

    # Bottom Summary Card
    card_y = 370
    ctx.set_source_rgb(0.92, 0.95, 0.98)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.fill()
    ctx.set_source_rgb(0.78, 0.84, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(65, card_y + 25)
    ctx.show_text("Dynamical Simulation Insights & Epistemic Guardrails:")

    dyn_bullets = [
        "• Linear Subtractive Attenuation: Recurrent inhibition bounds peak columnar activity (slope reduces from 14.9 to 1.53), preventing runaway excitation without divisive saturation.",
        "• Tuning Contrast Preservation: Intact feedback maintains sharp columnar tuning (FWHM 90°) whereas ablated feedback spreads across columns (FWHM 135°).",
        "• Decoding Precision Nuance: Sub-degree error (<0.8°) in noiseless simulation is a mathematical consequence of circular symmetry; biological noise yields ~5.65° error.",
        "• Supercritical Stability Limit: Lateral coupling J_col >= 0.60 causes explosive instability (> 3.8 x 10^6 Hz), establishing a strict biophysical boundary.",
    ]
    for bi, bullet in enumerate(dyn_bullets):
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(65, card_y + 45 + bi * 18)
        ctx.show_text(bullet)


def draw_figure6(ctx: cairo.Context, w: int, h: int) -> None:
    """Figure 6: Architectural Dichotomy: 1D Heading (EB) vs 2D Steering (FB)."""
    ctx.set_source_rgb(0.985, 0.988, 0.995)
    ctx.paint()

    ctx.set_source_rgb(0.82, 0.86, 0.92)
    ctx.set_line_width(1.5)
    ctx.rectangle(20, 20, w - 40, h - 40)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ctx.set_source_rgb(0.10, 0.15, 0.25)
    ctx.move_to(45, 58)
    ctx.show_text("Figure 6: Architectural Dichotomy: 1D Heading (EB) vs 2D Steering (FB)")

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.35, 0.40, 0.50)
    ctx.move_to(45, 80)
    ctx.show_text("Structural & Functional Contrast Across the Drosophila Central Complex Connectome (FAFB v783)")

    # Left Column: Ellipsoid Body (EB)
    eb_x, eb_y, eb_w, eb_h = 45, 110, 480, 240
    ctx.set_source_rgb(0.95, 0.96, 0.98)
    ctx.rectangle(eb_x, eb_y, eb_w, eb_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(eb_x, eb_y, eb_w, eb_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(14)
    ctx.set_source_rgb(0.15, 0.35, 0.65)
    ctx.move_to(eb_x + 15, eb_y + 28)
    ctx.show_text("1D Heading Compass: Ellipsoid Body (EB)")

    eb_features = [
        ("Circuit Topology", "Toroidal Ring Attractor (1D circular azimuth)"),
        ("Edge Reciprocity", "44.50% (Whole fly brain rank: #1)"),
        ("Dominant Motif", "Homotypic GABA <-> GABA (74.33% of dyads)"),
        ("Cellular Substrate", "Ring <-> Ring recurrent inhibition (88.2%)"),
        ("Chemical Pairing", "ACh <-> GABA DEPLETED (0.27x under null)"),
        ("Biological Role", "Compass bump maintenance via global inhibitory pool"),
    ]
    for fi, (ftitle, fval) in enumerate(eb_features):
        fy = eb_y + 55 + fi * 30
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(eb_x + 15, fy + 8)
        ctx.show_text(ftitle + ":")

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_source_rgb(0.35, 0.40, 0.50)
        ctx.move_to(eb_x + 150, fy + 8)
        ctx.show_text(fval)

    # Right Column: Fan-Shaped Body (FB)
    fb_x, fb_y, fb_w, fb_h = 555, 110, 480, 240
    ctx.set_source_rgb(0.95, 0.96, 0.98)
    ctx.rectangle(fb_x, fb_y, fb_w, fb_h)
    ctx.fill()
    ctx.set_source_rgb(0.85, 0.88, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(fb_x, fb_y, fb_w, fb_h)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(14)
    ctx.set_source_rgb(0.85, 0.25, 0.20)
    ctx.move_to(fb_x + 15, fb_y + 28)
    ctx.show_text("2D Vector Steering Matrix: Fan-Shaped Body (FB)")

    fb_features = [
        ("Circuit Topology", "Multi-Layered Columnar Matrix (2D vector steering)"),
        ("Edge Reciprocity", "23.18% (Whole fly brain rank: #6)"),
        ("Dominant Motif", "Heterotypic ACh <-> GABA (554 dyads, 10.19%)"),
        ("Cellular Substrate", "Columnar <-> Tangential (99.46% of loops)"),
        ("Chemical Pairing", "ACh <-> GABA ENRICHED (5.7x coarse, 2.5x k-NN)"),
        ("Biological Role", "Layer 4/5 premotor steering gain modulation"),
    ]
    for fi, (ftitle, fval) in enumerate(fb_features):
        fy = fb_y + 55 + fi * 30
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.20, 0.25, 0.35)
        ctx.move_to(fb_x + 15, fy + 8)
        ctx.show_text(ftitle + ":")

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_source_rgb(0.35, 0.40, 0.50)
        ctx.move_to(fb_x + 150, fy + 8)
        ctx.show_text(fval)

    # Bottom Synthesis Card
    card_y = 370
    ctx.set_source_rgb(0.92, 0.95, 0.98)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.fill()
    ctx.set_source_rgb(0.78, 0.84, 0.92)
    ctx.set_line_width(1.0)
    ctx.rectangle(45, card_y, w - 90, 110)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(12)
    ctx.set_source_rgb(0.10, 0.20, 0.40)
    ctx.move_to(65, card_y + 25)
    ctx.show_text("Neurocomputational Synthesis: Functional Specialization Across Navigational Neuropils")

    synthesis_bullets = [
        "• Ring Attractor vs Steering Matrix: The EB uses uniform homotypic inhibition to ensure a single, localized azimuth bump without directional drift.",
        "• Inverted Chemical Logic: While the EB suppresses heterotypic cross-talk, the FB enhances heterotypic feedback by > 2.5-fold to regulate motor steering commands.",
        "• Layer 4 & 5 Output Gating: Reciprocal loops in FB are tightly focused at the premotor output stage (PFL3 steering neurons), not across all 9 horizontal layers.",
        "• Connectomic Principle: Drosophila central complex neuropils employ chemospecific reciprocal motifs tailored to their exact computational geometry.",
    ]
    for bi, bullet in enumerate(synthesis_bullets):
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        ctx.set_source_rgb(0.25, 0.30, 0.40)
        ctx.move_to(65, card_y + 45 + bi * 18)
        ctx.show_text(bullet)


def save_figure(draw_fn, base_path: Path, w: int, h: int, *args) -> None:
    svg_path = base_path.with_suffix(".svg")
    png_path = base_path.with_suffix(".png")

    svg_surf = cairo.SVGSurface(str(svg_path), w, h)
    draw_fn(cairo.Context(svg_surf), w, h, *args)
    svg_surf.finish()

    img_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    draw_fn(cairo.Context(img_surf), w, h, *args)
    img_surf.write_to_png(str(png_path))

    print(f"  Generated SVG: {svg_path.name} ({svg_path.stat().st_size:,} bytes)")
    print(f"  Generated PNG: {png_path.name} ({png_path.stat().st_size:,} bytes)")


def main() -> None:
    print("=" * 80)
    print("VECTORWING: GENERATING PUBLICATION-GRADE PRESENTATION FIGURES (SVG & PNG)")
    print("=" * 80)

    if cairo is None:
        print("Error: cairo module required.")
        sys.exit(1)

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(FB_CACHE) as f:
        cache_data = json.load(f)
    with open(STUDY_JSON) as f:
        study_data = json.load(f)
    with open(ANATOMY_JSON) as f:
        anat_data = json.load(f)
    with open(KNN_JSON) as f:
        knn_data = json.load(f)
    with open(SIM_JSON) as f:
        sim_data = json.load(f)

    mcmc_data = {}
    if MCMC_JSON.exists():
        with open(MCMC_JSON) as f:
            mcmc_data = json.load(f)

    stress_data = {}
    if DYN_STRESS_JSON.exists():
        with open(DYN_STRESS_JSON) as f:
            stress_data = json.load(f)

    sens_data = {}
    if SENS_JSON.exists():
        with open(SENS_JSON) as f:
            sens_data = json.load(f)

    # 1. Figure 1: Network and Pipeline Overview
    print("\n[1/6] Rendering Figure 1: Network & Pipeline Overview (1100x520) ...")
    save_figure(draw_figure1, FIG_DIR / "figure1_network_and_pipeline_overview", 1100, 520, cache_data)

    # 2. Figure 2: Observed Transmitter-Pair Associations
    print("\n[2/6] Rendering Figure 2: Transmitter-Pair Associations (1100x520) ...")
    save_figure(draw_figure2, FIG_DIR / "figure2_transmitter_associations", 1100, 520, study_data)

    # 3. Figure 3: Neuronal and Anatomical Organization
    print("\n[3/6] Rendering Figure 3: Neuronal & Layer Organization (1100x520) ...")
    save_figure(draw_figure3, FIG_DIR / "figure3_neuronal_and_layer_organization", 1100, 520, anat_data)

    # 4. Figure 4: Statistical Robustness & Model Comparison
    print("\n[4/6] Rendering Figure 4: Statistical Robustness Comparison (1150x520) ...")
    save_figure(draw_figure4, FIG_DIR / "figure4_statistical_robustness_comparison", 1150, 520, study_data, knn_data, mcmc_data, sens_data)

    # 5. Figure 5: Dynamical Model & Stress Testing
    print("\n[5/6] Rendering Figure 5: Dynamical Model & Stress Testing (1100x520) ...")
    save_figure(draw_figure5, FIG_DIR / "figure5_dynamical_model_stress_testing", 1100, 520, sim_data, stress_data)

    # 6. Figure 6: Architectural Dichotomy (EB vs FB)
    print("\n[6/6] Rendering Figure 6: EB vs FB Architectural Dichotomy (1080x520) ...")
    save_figure(draw_figure6, FIG_DIR / "figure6_eb_vs_fb_circuit_contrast", 1080, 520)

    # Also maintain legacy names for backward compatibility
    print("\n[Backward Compatibility] Updating legacy aliases ...")
    save_figure(draw_figure4, FIG_DIR / "figure1_fb_conditional_associations", 1150, 520, study_data, knn_data, mcmc_data, sens_data)
    save_figure(draw_figure3, FIG_DIR / "figure2_fb_layer_column_matrix", 1100, 520, anat_data)
    save_figure(draw_figure6, FIG_DIR / "figure3_eb_vs_fb_circuit_contrast", 1080, 520)
    save_figure(draw_figure5, FIG_DIR / "figure4_vector_steering_dynamics", 1100, 520, sim_data, stress_data)

    print("\nAll 6 presentation figures (and backward-compatible aliases) rendered successfully!")


if __name__ == "__main__":
    main()
