#!/usr/bin/env python3
from pathlib import Path

p = Path("docs/phase3_results_audit.md")
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

# Replace lines 74 to 80 (0-indexed)
new_lines = [
    "  - $w \\ge 1$: 15,091,983 edges, 2,007,259 mutual dyads, $R_{\\text{edge}} = 26.60\\%$, $R_{\\text{dyad}} = 15.34\\%$, GCC = 99.62% (138,113 nodes).\n",
    "  - $w \\ge 2$: 7,595,967 edges, 729,762 mutual dyads, $R_{\\text{edge}} = 19.21\\%$, $R_{\\text{dyad}} = 10.63\\%$, GCC = 99.20% (136,475 nodes).\n",
    "  - $w \\ge 3$: 4,916,231 edges, 404,353 mutual dyads, $R_{\\text{edge}} = 16.45\\%$, $R_{\\text{dyad}} = 8.96\\%$, GCC = 98.85% (134,913 nodes).\n",
    "  - $w \\ge 5$: 2,700,513 edges, 188,724 mutual dyads, $R_{\\text{edge}} = 13.98\\%$, $R_{\\text{dyad}} = 7.51\\%$, GCC = 98.73% (132,483 nodes).\n",
    "  - $w \\ge 10$: 1,066,822 edges, 61,509 mutual dyads, $R_{\\text{edge}} = 11.53\\%$, $R_{\\text{dyad}} = 6.12\\%$, GCC = 98.56% (122,654 nodes).\n",
    "  - $w \\ge 20$: 366,864 edges, 17,725 mutual dyads, $R_{\\text{edge}} = 9.66\\%$, $R_{\\text{dyad}} = 5.08\\%$, GCC = 97.35% (87,414 nodes).\n",
]
lines[74:80] = new_lines

lines[87] = "  - Proofread neurons with zero chemical connections meeting release criteria in connection table: **616** (0.442%). In the absence of cell-type metadata, characterized strictly as proofread IDs absent from connectivity endpoints.\n"

p.write_text("".join(lines), encoding="utf-8")
print("Cleanly fixed docs/phase3_results_audit.md!")

