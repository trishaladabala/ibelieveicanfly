#!/usr/bin/env python3
from pathlib import Path

report_path = Path("results/real_data_pilot/phase3_validation_report.md")
text = report_path.read_text(encoding="utf-8")

lines = text.splitlines(keepends=True)

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith("#### Table 1:"):
        start_idx = i
    if start_idx != -1 and line.startswith("*Independent Verification*:"):
        end_idx = i
        break

print(f"Table 1 is between lines {start_idx+1} and {end_idx}")

new_table_lines = [
    "#### Table 1: Whole-Brain Multi-Threshold Sensitivity & Reciprocity (Verified Ground Truth)\n",
    "| Threshold ($w$) | Directed Edges ($E$) | Chemical Synapses | Mutual Dyads ($M$) | Reciprocal Directed Edges ($2M$) | Asymmetric Edges ($U$) | Edge Reciprocity ($R_{\\text{edge}} = 2M/E$) | Dyad Reciprocity ($R_{\\text{dyad}} = M/(M+U)$) | Active Neurons | Giant Component (GCC) | GCC Fraction |\n",
    "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n",
    "| **$w \\ge 1$** | 15,091,983 | 54,492,922 | **2,007,259** | 4,014,518 | 11,077,465 | **26.60%** | **15.34%** | 138,639 | 138,113 | 99.62% |\n",
    "| **$w \\ge 2$** | 7,595,967 | 46,996,906 | **729,762** | 1,459,524 | 6,136,443 | **19.21%** | **10.63%** | 137,582 | 136,475 | 99.20% |\n",
    "| **$w \\ge 3$** | 4,916,231 | 41,637,434 | **404,353** | 808,706 | 4,107,525 | **16.45%** | **8.96%** | 136,482 | 134,913 | 98.85% |\n",
    "| **$w \\ge 5$** | 2,700,513 | 34,153,566 | **188,724** | 377,448 | 2,323,065 | **13.98%** | **7.51%** | 134,181 | 132,483 | 98.73% |\n",
    "| **$w \\ge 10$** | 1,066,822 | 23,664,861 | **61,509** | 123,018 | 943,804 | **11.53%** | **6.12%** | 124,445 | 122,654 | 98.56% |\n",
    "| **$w \\ge 20$** | 366,864 | 14,410,844 | **17,725** | 35,450 | 331,414 | **9.66%** | **5.08%** | 89,793 | 87,414 | 97.35% |\n",
    "\n",
    "*Mathematical Definitions & Concordance*:\n",
    "- $M$ is the count of distinct unordered mutual dyads $\{u, v\}$ where both directed edges $(u, v)$ and $(v, u)$ exist at weight $\\ge w$.\n",
    "- $2M$ is the count of directed reciprocal edges.\n",
    "- Edge reciprocity is defined as $R_{\\text{edge}} = 2M / E$.\n",
    "- Dyad reciprocity is defined as $R_{\\text{dyad}} = M / (M + U)$, where $U = E - 2M$ represents asymmetric directed edges (autapses $A = 0$).\n",
    "\n",
]

lines[start_idx:end_idx] = new_table_lines
report_path.write_text("".join(lines), encoding="utf-8")
print("Table 1 replaced cleanly!")

