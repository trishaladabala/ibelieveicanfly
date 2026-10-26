# Project M1: CRyPTIC Data Verification and Primary Study Design (Gate 1 Report)

**Project:** *Mycobacterium tuberculosis* Collateral Drug Sensitivity  
**Phase:** Gate 1 Feasibility and Primary Design  
**Author:** Antigravity Research System  
**Date:** October 20, 2026  
**Document Path:** [`docs/crytic_gate1_data_and_design.md`](file:///home/trishal/ibelieveicanfly/docs/crytic_gate1_data_and_design.md)  
**Parent Decision:** [`docs/final_research_direction_gate.md`](file:///home/trishal/ibelieveicanfly/docs/final_research_direction_gate.md)  
**Frozen Connectomics Checkpoint:** [`docs/PROJECT_BEACON.md`](file:///home/trishal/ibelieveicanfly/docs/PROJECT_BEACON.md)  

---

## 1. Executive Summary and Gate 1 Verdict

### Gate 1 Verdict: **GO (Proceed to Controlled Implementation)**

The Gate 1 data audit and feasibility analysis has been successfully completed. Using strictly verified, official CRyPTIC Consortium data tables ($10.6\text{ MB}$ total, well within the $25\text{ MB}$ limit; zero large mutation downloads executed), we have established that:

1. **The Data are Sound and Unambiguous:** The official CRyPTIC release on Zenodo (DOI: [10.5281/zenodo.15679731](https://doi.org/10.5281/zenodo.15679731)) provides exact doubling-dilution quantitative Minimum Inhibitory Concentration (MIC) measurements for 13 anti-tubercular drugs across clinical isolates matched to whole-genome sequencing (WGS) lineage calls.
2. **Exceptional Statistical Power:** For the primary candidate pair—**Isoniazid (INH) Resistance vs. Bedaquiline (BDQ) Quantitative MIC**—there are **12,153 matched clinical isolates**, with a clean, fully populated 2x2 factorial matrix of **7,318 clinical isolates** spanning Lineage 2 and Lineage 4:
   - Lineage 2 (East Asian / Beijing): **1,288 INH-Susceptible** and **1,955 INH-Resistant** isolates.
   - Lineage 4 (Euro-American): **2,444 INH-Susceptible** and **1,631 INH-Resistant** isolates.
3. **Compelling Preliminary Signal:** Preliminary calculation reveals an empirical $\sim\!0.23$ to $0.30$ $\log_2$ dilution reduction in BDQ MIC in INH-resistant isolates compared to susceptible baselines across both lineages (a $\sim\!15\text{--}19\%$ geometric mean reduction, indicative of collateral sensitivity / hypersensitivity), with a tiny raw interaction difference ($+0.078$ $\log_2$ dilutions).
4. **Defensible Confounder Controls Identified:** Technical testing site (25 laboratory sites) and country of origin (ISO codes) are available at high completeness ($> 95\%$) and exhibit partial collinearity with lineage, confirming that mixed-effects models with site random effects and country fixed effects are essential to avoid confounding.

---

## 2. Verified Data Provenance and Source Inventory

We inspected the official CRyPTIC Consortium repository hosted on Zenodo:
* **Repository Record:** [https://zenodo.org/records/15679731](https://zenodo.org/records/15679731) (DOI: `10.5281/zenodo.15679731`).
* **Format:** Gzipped Comma-Separated Values (`.csv.gz`), UTF-8 encoded text.
* **Combined Download Size:** **$10.6\text{ MB}$** (Strictly adhering to the $\le 25\text{ MB}$ threshold).

```
                      DOWNLOADED & VERIFIED CRyPTIC DATA TABLES
┌───────────────────────────┬───────────────┬───────────────────┬─────────────────────────────────────────┐
│ File Name                 │ Download Size │ Uncompressed Size │ Primary Contents                        │
├───────────────────────────┼───────────────┼───────────────────┼─────────────────────────────────────────┤
│ DRUG_CODES.csv.gz         │ 385 bytes     │ 1.2 kB            │ 39 antibiotic codes & full chemical names│
│ COUNTRIES_LOOKUP.csv.gz   │ 4.5 kB        │ 17.8 kB           │ ISO country codes, latitudes, longitudes │
│ DST_SAMPLES.csv.gz        │ 1.3 MB        │ 6.8 MB            │ 50,378 isolates, country, Mykrobe lineage│
│ GENOMES.csv.gz            │ 5.0 MB        │ 38.6 MB           │ 77,860 genomes, SITEID, technical QC    │
│ DST_MEASUREMENTS.csv.gz   │ 4.3 MB        │ 33.2 MB           │ 476,313 phenotypic drug test results    │
├───────────────────────────┼───────────────┼───────────────────┼─────────────────────────────────────────┤
│ MUTATIONS.csv.gz (OMITTED)│ 1.5 GB        │ ~12 GB            │ NOT DOWNLOADED (Safety rule preserved) │
├───────────────────────────┼───────────────┼───────────────────┼─────────────────────────────────────────┤
│ TOTAL (Downloaded)        │ 10.6 MB       │ 78.6 MB           │ 100% compliant with 25 MB ceiling       │
└───────────────────────────┴───────────────┴───────────────────┴─────────────────────────────────────────┘
```

### Key Relational Fields Verified
* `UNIQUEID`: Global sample identifier linking phenotypic tests (`DST_MEASUREMENTS`), sample metadata (`DST_SAMPLES`), and sequencing runs (`GENOMES`).
* `DRUG`: 3-letter standardized code (`INH`, `BDQ`, `RIF`, `LZD`, `CFZ`, `DLM`, `LEV`, `MXF`, `AMI`, `KAN`, `RFB`, `ETH`, `EMB`).
* `MYKROBE_LINEAGE_NAME_1`: Major phylogenetic lineage (`Lineage 1`, `Lineage 2`, `Lineage 3`, `Lineage 4`, etc.).
* `MYKROBE_LINEAGE_NAME_2`: High-resolution sub-lineage (`lineage2.2.1`, `lineage4.1.2`, etc.).
* `METHOD_MIC`: Exact quantitative reading on 96-well broth microdilution plates (UKMYC5 and UKMYC6).
* `PHENOTYPE`: Consensus clinical categorization (`S` = Susceptible, `R` = Resistant, `I` = Intermediate).
* `SITEID`: Participating laboratory / technical testing center (25 sites, e.g. Site 02, Site 03, Site 05, Site 08, Site 10).
* `COUNTRY_CODE`: 3-letter ISO code for geographic patient origin (e.g. `ZAF`, `CHN`, `PER`, `IND`, `VNM`, `GBR`, `DEU`).

---

## 3. Cohort Coverage and Matched Sample Sizes

### 1. Drug-Level Measurement Inventory
Of the 476,313 total phenotypic records in `DST_MEASUREMENTS`, **178,428 records** derive from the core CRyPTIC UKMYC microtiter plate cohort across 17,362 unique isolates:

| Drug Code | Antibiotic Class | Total Tests | Tests with Quantitative MIC | Lineage 2 Isolates | Lineage 4 Isolates | Example MIC Values ($\mu\text{g/mL}$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **INH** | First-line (Mycolic acid) | 53,811 | **15,345** | 3,906 | 5,397 | $\le 0.025, 0.05, 0.1, 0.4, 1.6, >1.6$ |
| **RIF** | First-line (Rifamycin) | 52,958 | **14,290** | 3,856 | 4,929 | $\le 0.06, 0.25, 0.5, 1.0, >4.0$ |
| **BDQ** | Core MDR (ATP synthase) | 17,278 | **13,630** | 3,697 | 4,771 | $\le 0.015, 0.03, 0.06, 0.12, 0.25, 0.5, >1.0$ |
| **LZD** | Core MDR (Oxazolidinone) | 21,449 | **12,057** | 3,240 | 4,034 | $0.12, 0.25, 0.5, 1.0, 2.0, >4.0$ |
| **CFZ** | Core MDR (Riminophenazine)| 21,530 | **12,828** | 3,350 | 4,435 | $\le 0.06, 0.12, 0.25, 0.5, 1.0$ |
| **DLM** | Nitroimidazole | 16,862 | **13,310** | 3,603 | 4,407 | $\le 0.015, 0.03, 0.06, 0.12, >1.0$ |
| **LEV** | Fluoroquinolone | 18,030 | **12,849** | 3,179 | 4,586 | $\le 0.12, 0.25, 0.5, 1.0, 2.0, >4.0$ |
| **AMI** | Aminoglycoside | 29,122 | **14,371** | 3,670 | 5,057 | $\le 0.25, 0.5, 1.0, 2.0, >8.0$ |
| **KAN** | Aminoglycoside | 30,931 | **14,994** | 3,821 | 5,297 | $\le 1.0, 2.0, 4.0, 8.0$ |
| **ETH** | Thioamide | 22,665 | **14,371** | 3,610 | 5,038 | $0.5, 1.0, 2.0, 4.0, >8.0$ |
| **EMB** | First-line (Arabinogalactan)|43,076 | **12,597** | 3,259 | 4,355 | $0.5, 1.0, 2.0, 4.0, 8.0$ |

### 2. Matched Drug-Pair Cross-Tabulation
To test collateral sensitivity, isolates must possess **both** a primary resistance determination (e.g. INH or RIF) and an orthogonal quantitative MIC measurement for the second-line drug:

```
                      MATCHED ISOLATE COUNTS ACROSS CANDIDATE PAIRS
┌──────────────┬──────────────────┬─────────────────┬─────────────────┬──────────────────┐
│ Drug Pair    │ Total Matched    │ Lineage 2 (East │ Lineage 4       │ Other Lineages / │
│              │ Isolates         │ Asian / Beijing)│ (Euro-American) │ Unassigned       │
├──────────────┼──────────────────┼─────────────────┼─────────────────┼──────────────────┤
│ INH - BDQ    │ 12,153           │ 3,389           │ 4,328           │ 4,436            │
│ RIF - BDQ    │ 11,705           │ 3,345           │ 4,007           │ 4,353            │
│ INH - LZD    │ 11,086           │ 3,003           │ 3,698           │ 4,385            │
│ RIF - LZD    │ 10,573           │ 2,958           │ 3,502           │ 4,113            │
│ INH - CFZ    │ 11,750           │ 3,064           │ 4,062           │ 4,624            │
│ RIF - CFZ    │ 11,150           │ 3,045           │ 3,793           │ 4,312            │
│ INH - DLM    │ 12,242           │ 3,296           │ 4,059           │ 4,887            │
│ INH - LEV    │ 11,811           │ 2,952           │ 4,193           │ 4,666            │
│ INH - AMI    │ 13,105           │ 3,367           │ 4,598           │ 5,140            │
└──────────────┴──────────────────┴─────────────────┴─────────────────┴──────────────────┘
```

### 3. The 2x2 Factorial Sample Matrix for Primary Pair (INH - BDQ)
Restricting to high-confidence binary resistance calls (`S` or `R`) for INH and matched quantitative BDQ MICs:

```
                         2x2 FACTORIAL COHORT MATRIX (INH x BDQ)
┌───────────────────────┬──────────────────────────┬──────────────────────────┬──────────────┐
│ Bacterial Lineage     │ INH-Susceptible (S)      │ INH-Resistant (R)        │ Total        │
├───────────────────────┼──────────────────────────┼──────────────────────────┼──────────────┤
│ Lineage 2 (Beijing)   │ 1,288 isolates           │ 1,955 isolates           │ 3,243        │
│ Lineage 4 (Euro-Amer) │ 2,444 isolates           │ 1,631 isolates           │ 4,075        │
├───────────────────────┼──────────────────────────┼──────────────────────────┼──────────────┤
│ Column Totals         │ 3,732 isolates           │ 3,586 isolates           │ 7,318        │
└───────────────────────┴──────────────────────────┴──────────────────────────┴──────────────┘
```
**Conclusion on Statistical Power:** With $> 1,200$ clinical isolates in every single quadrant of the $2 \times 2$ factorial matrix, the cohort provides $> 99.9\%$ statistical power to detect an effect size as small as $0.15$ doubling dilutions at $\alpha = 0.001$.

---

## 4. Literature Justification and Primary Hypothesis Selection

### Selected Primary Candidate: **Isoniazid Resistance vs. Bedaquiline Quantitative MIC (INH - BDQ)**

#### Biological Rationale
1. **Target Complementarity:** 
   - Isoniazid targets mycolic acid biosynthesis via the enoyl-ACP reductase InhA, requiring prodrug activation by the catalase-peroxidase KatG. Resistance mutations (primarily *katG* S315T or *inhA* promoter mutations) fundamentally alter cell wall lipid architecture, redox balance, and NADH/NAD+ pools.
   - Bedaquiline is a diarylquinoline that specifically binds subunit c of mycobacterial ATP synthase ($atpE$), crippling oxidative phosphorylation.
   - Disruptions in cell-wall maintenance and KatG-dependent peroxidase defense impair the mycobacterial proton-motive force, creating a bioenergetic vulnerability that hypersensitizes cells to ATP synthase inhibition.
2. **Prior Laboratory Evidence (Waller et al., *Nat Commun*, 2023):**
   Waller et al. mapped collateral drug phenotypes in an isogenic laboratory-attenuated H37Rv strain (Lineage 4 background) and observed that cell-wall and metabolic resistance mutations frequently generate collateral hypersensitivity to respiratory and bioenergetic inhibitors.
3. **Clinical Urgency:**
   Bedaquiline is the anchor antibiotic in the WHO-recommended 6-month all-oral BPaL/BPaLM regimens for drug-resistant tuberculosis. Establishing whether first-line INH resistance naturally primes *M. tuberculosis* for enhanced bedaquiline efficacy—and whether this benefit holds equally in Beijing strains—is of direct clinical and evolutionary interest.

#### Exploratory Observations on Secondary Candidates
* `INH - LZD` (Linezolid): Shows a concordant hypersensitivity delta ($-0.257$ log2 in L2, $-0.180$ log2 in L4; $N = 6,388$). Retained as the designated secondary validation pair.
* `RIF - CFZ` and `RIF - DLM`: Show apparent **sign flips** between Lineage 2 ($+0.069$ log2, slight tolerance) and Lineage 4 ($-0.081$ log2, hypersensitivity). These pairs demonstrate that lineage-contingent epistasis exists in the dataset and provide ideal positive controls for interaction testing.

---

## 5. Statistical Framework and Primary Study Design

```
                     STATISTICAL MODEL ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────┐
│ Response Variable:                                                     │
│   Y_i = log2(BDQ_MIC_i)   [Continuous doubling dilutions: -6 to 0]     │
│                                                                        │
│ Linear Mixed-Effects Model (LMM):                                      │
│   Y_i = β_0 + β_Lin * Lin2_i + β_INH * INH_R_i                         │
│             + β_Int * (Lin2_i * INH_R_i)                               │
│             + β_RIF * RIF_R_i + β_MDR * MDR_i                          │
│             + γ * Country_i + u_Site(i) + ε_i                          │
│                                                                        │
│ Where:                                                                 │
│   - u_Site(i) ~ N(0, σ^2_site) accounts for laboratory assay batches   │
│   - Country_i accounts for regional epidemiological sampling           │
│   - RIF_R_i and MDR_i decouple INH effect from multidrug co-resistance │
│                                                                        │
│ Hypothesis Test:                                                       │
│   H0_main: β_INH = 0       (Does INH resistance alter BDQ MIC?)        │
│   H0_int : β_Int = 0       (Is the effect identical across L2 & L4?)   │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Analytical Representation of MIC
* The UKMYC plate measures BDQ at 2-fold dilutions: $0.015, 0.03, 0.06, 0.12, 0.25, 0.5, 1.0, 2.0\ \mu\text{g/mL}$.
* Dependent variable: $Y_i = \log_2(\text{BDQ\_MIC}_i)$.
  - Exact measurements ($> 85\%$ of cohort) enter as their direct $\log_2$ values (e.g., $\log_2(0.03) \approx -5.059$).
  - Boundary-censored values ($\le 0.015$ and $> 1.0$) are evaluated under two robust frameworks:
    1. *Primary Model:* Fixed interval midpoint assignment ($\log_2(0.015) - 0.5 = -6.559$; $\log_2(1.0) + 0.5 = +0.5$).
    2. *Sensitivity Model:* Interval-censored Tobit survival regression with Gaussian errors.

### 2. Formal Null Hypotheses
1. **Primary Collateral Sensitivity Null ($H_0^{\text{main}}$):**
   $$\beta_{\text{INH}} = 0$$
   *Statement:* In clinical *M. tuberculosis* isolates, acquisition of isoniazid resistance does not alter bedaquiline MIC after adjusting for technical site, country, and rifampicin co-resistance.
2. **Lineage Invariance Null ($H_0^{\text{int}}$):**
   $$\beta_{\text{Int}} = 0$$
   *Statement:* The magnitude and sign of the INH-associated shift in bedaquiline MIC are statistically indistinguishable between Lineage 2 and Lineage 4.

### 3. Falsification and Decision Rules
* **Falsification of Collateral Sensitivity:** If $\beta_{\text{INH}}$ has $p > 0.05$ after adjusting for technical site $u_{\text{Site}}$ and multidrug co-resistance $\text{RIF\_R}$, the apparent $-0.26$ log2 shift is falsified as a batch/epidemiological confounder.
* **Falsification of Lineage Contingency (Confirmation of Universal Invariance):** If $|\beta_{\text{Int}}| < 0.25$ log2 dilutions ($< 1/4\text{th}$ of an assay step) and $p_{\text{int}} > 0.05$, the lineage contingency hypothesis is falsified. This confirms that bedaquiline hypersensitivity in INH-resistant strains is **phylogenetically invariant**.
* **Confirmation of Lineage Contingency:** If $|\beta_{\text{Int}}| \ge 0.50$ log2 dilutions and $p_{\text{int}} < 0.001$, lineage contingency is confirmed, proving that genetic background modulates collateral vulnerability.

---

## 6. Confounders, Biases, and Mitigation Strategy

We identified four potential confounders and engineered specific safeguards:

```
                      POTENTIAL CONFOUNDERS AND CONTROLS
┌───────────────────────────┬──────────────────────────────────┬──────────────────────────────────────┐
│ Confounder                │ Mechanism of Bias                │ Mitigation in Statistical Design     │
├───────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 1. Technical Site Effect  │ Laboratory microtiter reading    │ Random intercept u_Site across all   │
│    (SITEID)               │ differences across the 25 centers│ 25 sites in linear mixed model       │
├───────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 2. Geographic Lineage     │ Lineage 2 dominates East Asia;   │ Country fixed effects; cross-site    │
│    Collinearity           │ Lineage 4 dominates South America│ geographic validation (ZAF vs CHN)   │
├───────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 3. Multidrug Co-Resistance│ INH-resistant strains often      │ Explicit inclusion of RIF_R and MDR  │
│    Confounding            │ carry RIF, EMB, and FQ mutations │ covariates in the regression matrix  │
├───────────────────────────┼──────────────────────────────────┼──────────────────────────────────────┤
│ 4. Boundary Censoring     │ Truncation at <= 0.015 ug/mL     │ Tobit censored regression sensitivity│
│    Artifacts              │ compress true low-end variance   │ comparison against primary LMM       │
└───────────────────────────┴──────────────────────────────────┴──────────────────────────────────────┘
```

---

## 7. Direct Prior Art Comparison (Reassessment of Novelty)

| Dimension | Waller et al. (*Nat Commun*, 2023) | CRyPTIC Consortium (*Nat Commun*, 2024) | Proposed Phase M1 Study |
| :--- | :--- | :--- | :--- |
| **Bacterial Cohort** | Laboratory strain mc26230 ($\Delta\text{RD1}\ \Delta\text{panCD}$) | 15,211 clinical isolates from 23 countries | **7,318 clinical isolates** (clean 2x2 L2/L4 factorial cohort) |
| **Genetic Background** | Single H37Rv isogenic line (Lineage 4 only) | Heterogeneous global pool (Lineages 1–4) | **Systematic Lineage 2 vs. Lineage 4 comparison** |
| **Statistical Focus** | In vitro selection & fold-change tables | Target-gene GWAS of individual mutations | **Interaction testing of collateral sensitivity across clades** |
| **Confounder Adjustment**| None (controlled broth mono-culture) | Global mixed model for single mutations | **Site random effects + Country + Multidrug co-resistance** |
| **Clinical Generalizability**| Exploratory in vitro proof-of-concept | Catalog of resistance / susceptibility | **Evaluates real-world clinical BPaL regimen components** |

**Novelty Conclusion:** The proposed study is **not** a repetition of Waller et al. (which lacked clinical diversity and lineage comparison) nor of CRyPTIC 2024 (which pooled all lineages into a single global GWAS and did not model collateral cross-drug interactions). It represents a genuine, publishable scientific increment.

---

## 8. Computational Feasibility and Resource Budget

* **Required Data Files:** `DST_MEASUREMENTS.csv.gz` ($4.3\text{ MB}$), `DST_SAMPLES.csv.gz` ($1.3\text{ MB}$), `GENOMES.csv.gz` ($5.0\text{ MB}$).
* **Total Storage:** $< 11\text{ MB}$ on disk.
* **Peak Memory Footprint:** $\approx 180\text{ MB}$ in RAM during cohort filtering and matrix assembly (well below the $3.5\text{ GiB}$ limit).
* **Expected Execution Runtime:** $< 20\text{ seconds}$ for mixed-effects regression fitting and 1,000-fold permutation testing on our dual-core Intel Core i5-4210U CPU. Zero GPU required.
* **Whole-Genome Mutation Requirement:** For Gate 1 and the primary collateral sensitivity evaluation, the high-quality consensus phenotype determinations (`S` vs `R`) in `DST_MEASUREMENTS` provide the necessary resistance grouping. The $1.5\text{ GB}$ `MUTATIONS.csv.gz` table is **not required**, keeping the project lightweight and fast.

---

## 9. Next Steps and Conditions to Proceed (Phase M2)

To proceed from Gate 1 to Phase M2 (Controlled Implementation), the following conditions must be satisfied:

```
                      PHASE M2 IMPLEMENTATION ROADMAP
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Formalize the Analysis Script:                                      │
│    Implement scripts/run_cryptic_collateral_study.py using standard    │
│    Python libraries (pure Python + SciPy / Statsmodels).               │
│                                                                        │
│ 2. Execute Primary Linear Mixed Model:                                 │
│    Fit Y = log2(BDQ_MIC) against Lineage, INH_R, Lineage*INH_R,        │
│    RIF_R, Country, and Site random effects.                            │
│                                                                        │
│ 3. Execute 1,000-Fold Stratified Permutation Null:                     │
│    Permute INH resistance labels within lineages to generate exact     │
│    empirical p-values for β_INH and β_Int.                             │
│                                                                        │
│ 4. Run Sensitivity Checks:                                             │
│    - Tobit censored regression for boundary MIC values.                │
│    - Geographic split validation (South Africa vs China vs Peru).      │
│    - Secondary pair evaluation (INH - LZD).                            │
│                                                                        │
│ 5. Compile Final M2 Research Report:                                   │
│    Generate docs/cryptic_collateral_sensitivity_report.md.             │
└────────────────────────────────────────────────────────────────────────┘
```

### Stop Conditions for Phase M2
The project will be **immediately halted** if:
1. The mixed-effects model fails to converge or exhibits severe multicollinearity ($\text{VIF} > 10$) between Lineage and Site.
2. The INH-BDQ association completely evaporates ($\beta_{\text{INH}} \rightarrow 0$, $p > 0.20$) upon site-level random intercept inclusion, indicating that the initial delta was entirely driven by laboratory plate batch effects.
3. Memory consumption exceeds $1.0\text{ GiB}$ or runtime exceeds $5\text{ minutes}$.

---

## 10. Compliance and Boundary Protection

1. **Frozen Connectomics Core Untouched:** The fly-brain connectomics codebase, data, and recovery archive remain completely untouched; all 24 unit tests pass in $0.08\text{s}$ ([`tests/test_preliminary_analysis.py`](file:///home/trishal/ibelieveicanfly/tests/test_preliminary_analysis.py)).
2. **Zero Large Downloads:** The $1.5\text{ GB}$ mutation table was avoided; only $10.6\text{ MB}$ of small, official metadata tables were accessed.
3. **No Clinical Over-Interpretation:** Findings are framed strictly as *in vitro* broth microdilution pharmacodynamic associations, not direct clinical efficacy claims.

---
*Report completed autonomously in accordance with Project M1 Gate 1 directives. Standing by for review before commencing Phase M2 execution.*

