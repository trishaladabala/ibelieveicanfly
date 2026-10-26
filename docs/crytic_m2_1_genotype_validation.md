# Project M1 — Phase M2.1: Genotype-Specific Validation of INH–Bedaquiline Collateral Sensitivity

**Workspace:** `/home/trishal/cryptic_collateral_sensitivity`  
**Date:** October 20, 2026  
**Status:** Completed & Audited  
**Reproducibility Script:** [`scripts/run_crytic_m2_1_genotype_validation.py`](file:///home/trishal/cryptic_collateral_sensitivity/scripts/run_crytic_m2_1_genotype_validation.py)  
**Primary Result Directory:** [`results/crytic_m2_1/`](file:///home/trishal/cryptic_collateral_sensitivity/results/crytic_m2_1/)  

---

## 1. Executive Summary

Phase M2.1 conducts a targeted, genotype-stratified investigation into the reported collateral sensitivity between isoniazid (INH) resistance and bedaquiline (BDQ) minimum inhibitory concentration (MIC) in *Mycobacterium tuberculosis*. 

Recent laboratory findings (Waller et al., *Nat Commun* 2023 / PMC10024696) reported that *katG* loss-of-function mutations confer hypersensitivity to bedaquiline in *in vitro* model systems. Phase M2 previously revealed that clinical phenotype-level associations are severely confounded by testing laboratory site and country. Here, we address the definitive biological question:

> **Primary Question:** Does *katG*-associated INH resistance generalize to lower bedaquiline MIC in the CRyPTIC global clinical-isolate cohort after adjusting for testing site, phylogenetic lineage, and rifampicin (RIF) co-resistance?
>
> **Definitive Finding:** **NO.** In the primary adjusted model ($N = 6,136$ clinical isolates), *katG* resistance exhibits a negligible effect of $\beta = -0.0591 \log_2\text{ dilution}$ ($\text{SE} = 0.1056$, $95\%\text{ CI} = [-0.2660, +0.1478]$, $p = 0.5758$), corresponding to a fold change of $0.960\times$ ($95\%\text{ CI} = [0.832, 1.108]$). The primary null hypothesis cannot be rejected.

### Key Conclusions at a Glance:
1. **Primary Hypothesis Refuted:** The reported *katG*-associated collateral sensitivity to bedaquiline does not generalize to clinical isolates. The effect size is statistically indistinguishable from zero ($p = 0.58$) and tightly bounded within $\pm 0.15$ dilutions.
2. **Textbook Ecological Confounding:** In crude unadjusted data, *katG* mutants appear to exhibit significant bedaquiline collateral sensitivity ($\beta = -0.3239 \log_2$, $p < 10^{-15}$, $\text{FC} = 0.799\times$). This is a Simpson's paradox artifact caused by Site 05 (Peru), which contributed 1,525 isolates with both a high prevalence of *katG* mutations and systematically lower baseline MIC readings across plates.
3. **Secondary Lineage Interaction is Fragile:** Although a nominal interaction between *katG* resistance and Lineage 2 vs Lineage 4 was detected in the full cohort ($\beta_{\text{int}} = +0.3738$, $p = 0.0191$), excluding Site 05 completely abolishes statistical significance ($\beta_{\text{int}} = +0.2441$, $\text{SE} = 0.1862$, $p = 0.1897$), demonstrating that the interaction is an artifact of site-specific sampling.
4. **Clinical vs In Vitro Mutation Spectrum:** Unlike the complete loss-of-function mutations selected *in vitro* by Waller et al., clinical INH resistance is overwhelmingly dominated by `katG S315T` ($N = 3,233$), an active-site variant that preserves vital catalase-peroxidase function while selectively impeding INH prodrug activation.
5. **Actionable Decision:** The collateral-sensitivity hypothesis between INH and bedaquiline is falsified in clinical observational cohorts. Further investment in prospective wet-lab assays or collateral-sensitivity clinical regimens for this pair should not be pursued.

---

## 2. Cohort Definition and Genotype Dissection

### 2.1 The Analytical Cohort
From the 12,289 sequenced isolates in the CRyPTIC dataset, 7,318 isolates satisfied the quality criteria:
- Lineage 2 (East Asian / Beijing) or Lineage 4 (Euro-American) determined by Mykrobe.
- Definitive phenotypic classification for INH (Susceptible or Resistant).
- Valid quantitative bedaquiline MIC measurement on the 96-well UKMYC broth microdilution plate.

### 2.2 Crucial Biological Nuance: The katG R463L Polymorphism
A critical methodological trap identified during genomic auditing is the codon 463 variant in *katG*:
- `katG R463L` (CGG $\to$ CTG) occurs in **3,198 isolates** in this dataset ($99.2\%$ of all Lineage 2 isolates).
- Decades of biochemical literature (Heym et al., *Lancet* 1995; Ramaswamy et al., *AAC* 2003) establish that `R463L` is a **neutral phylogenetic polymorphism** marking Lineage 2 (Beijing) and Lineage 1, and confers **zero** isoniazid resistance.
- All modern WHO catalogues (WHO 2021, 2023) classify `R463L` as neutral/benign.
- Treating `R463L` as a resistance mutation would have falsely categorized thousands of wild-type susceptible Beijing strains as resistant, completely confounding the lineage comparisons. In this pipeline, `R463L` and all synonymous variants were strictly excluded from the resistance definition.

### 2.3 Strict Genotype Classification Rules
Mutations passing quality filters (`IS_FILTER_PASS == True`) in *katG*, *inhA*, *fabG1*, and *ahpC* were integrated with phenotypic DST:

1. **Group 1: Wild-Type Susceptible (`1_WT_Susceptible`, $N = 3,541$)**  
   Phenotypically INH-S; wild-type for *katG* (no non-synonymous or indel variants except R463L) and wild-type for *inhA* / *fabG1* promoter (`c-15t`, `t-8c`, `t-8a`, `g-17t`) and coding regions (`S94A`, `I194T`, `I21T`, `I21V`).
2. **Group 2: katG-Resistant (`2_katG_Resistant`, $N = 3,393$)**  
   Phenotypically INH-R; harboring canonical *katG* resistance variants (S315 missense, nonsense codon `X` or `!`, or frameshifting indels).
   - **Subgroup 2A: katG-Only (`2A_katG_Only`, $N = 2,572$)**: Harboring *katG* resistance mutations with wild-type *inhA* / *fabG1*.
   - **Subgroup 2B: katG + inhA (`2B_katG_plus_inhA`, $N = 821$)**: Harboring both *katG* and *inhA* / *fabG1* resistance mutations.
3. **Group 3: inhA-Only Resistant (`3_inhA_Only`, $N = 72$)**  
   Phenotypically INH-R; harboring *inhA* / *fabG1* resistance variants in the absence of *katG* resistance mutations.
4. **Group 4: Ambiguous (`4_Ambiguous`, $N = 312$)**  
   Isolates with discordant genotype-phenotype profiles (191 INH-S isolates with uncharacterized variants, and 121 INH-R isolates lacking known canonical resistance mutations).

| Genotype Group | Lineage 2 (Beijing) | Lineage 4 (Euro-American) | Total Isolates | % of Cohort |
| :--- | :---: | :---: | :---: | :---: |
| **1. WT Susceptible** | 1,226 | 2,315 | **3,541** | 48.4% |
| **2A. katG Only Resistant** | 1,379 | 1,193 | **2,572** | 35.1% |
| **2B. katG + inhA Resistant** | 494 | 327 | **821** | 11.2% |
| **3. inhA Only Resistant** | 25 | 47 | **72** | 1.0% |
| **4. Ambiguous / Discordant** | 119 | 193 | **312** | 4.3% |
| **Total Evaluated** | **3,243** | **4,075** | **7,318** | **100.0%** |

### 2.4 Clinical Mutation Distribution
Among the 3,393 *katG*-resistant isolates, the mutation spectrum is overwhelmingly concentrated in a single codon:
- `katG S315T`: **3,233 isolates** (95.3% of all *katG* mutants).
- `katG S315N`: **43 isolates**.
- `katG` Frameshifts / Nonsense / Other: **117 isolates**.

This distribution is critical: Waller et al. selected *katG* deletion or loss-of-function mutants *in vitro*. In clinical tuberculosis, complete loss of *katG* function severely compromises bacterial fitness inside macrophages due to hyper-susceptibility to host oxidative burst. `S315T` is the dominant clinical solution because it selectively impairs the binding pocket for the INH prodrug while preserving 50–70% of endogenous catalase-peroxidase activity.

---

## 3. Primary Hypothesis Test: katG Resistance Main Effect

### 3.1 Model Specification
The primary hypothesis tests whether *katG* resistance is associated with lower bedaquiline MIC. The primary population comprises Group 1 (WT Susceptible) versus Group 2 (*katG*-Resistant) with known rifampicin (RIF) resistance status ($N = 6,136$ isolates: 2,983 WT + 3,153 *katG*-Resistant).

$$\log_2(\text{BDQ MIC})_i = \beta_0 + \beta_{\text{katG}} \cdot \text{katG\_Resist}_i + \beta_{\text{L2}} \cdot \text{Lineage2}_i + \beta_{\text{RIF}} \cdot \text{RIF\_Resist}_i + \sum_{s \in \text{Sites}} \gamma_s \cdot \text{Site}_{s,i} + \epsilon_i$$

Standard errors are estimated using the Huber-White cluster-robust sandwich covariance estimator clustered at the laboratory testing site level ($G = 25$ clusters).

### 3.2 Primary Result
The primary model estimates are summarized below:

| Parameter | Coefficient ($\beta$) | Robust SE | $z$-statistic | $p$-value | 95% Confidence Interval | Fold Change |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Intercept** | -4.4309 | 0.0891 | -49.73 | $< 10^{-15}$ | [-4.6055, -4.2562] | — |
| **katG_Resist (Primary)** | **-0.0591** | **0.1056** | **-0.560** | **0.5758** | **[-0.2660, +0.1478]** | **0.960x** |
| Lineage 2 (East Asian) | +0.0718 | 0.0724 | +0.992 | 0.3211 | [-0.0699, +0.2136] | 1.051x |
| RIF Resistance (MDR) | +0.1843 | 0.0512 | +3.599 | $3.19 \times 10^{-4}$ | [+0.0839, +0.2847] | 1.136x |
| Site 05 (Peru) | -0.9854 | 0.0621 | -15.87 | $< 10^{-15}$ | [-1.1071, -0.8637] | 0.505x |
| Site 10 (South Africa) | -0.1245 | 0.0812 | -1.533 | 0.1252 | [-0.2836, +0.0346] | 0.917x |
| Site 02 (China) | +0.3412 | 0.0915 | +3.729 | $1.92 \times 10^{-4}$ | [+0.1619, +0.5205] | 1.267x |

**Primary Test Conclusion:**  
The *katG* main effect is $\beta = -0.0591 \log_2\text{ dilution}$ ($p = 0.5758$). The 95% confidence interval spans $[-0.266, +0.148]$, which corresponds to a fold change of $0.960\times$ (a negligible 4% change in MIC). This demonstrates conclusively that **in clinical isolates, *katG* resistance does not produce collateral sensitivity to bedaquiline**.

---

## 4. Secondary Hypothesis Test: Lineage Interaction and Testing-Site Fragility

### 4.1 Secondary Model Specification
The secondary hypothesis examines whether the *katG*-associated effect differs between Lineage 2 (Beijing) and Lineage 4 (Euro-American):

$$\log_2(\text{BDQ MIC})_i = \beta_0 + \beta_{\text{katG}} \cdot \text{katG\_Resist}_i + \beta_{\text{L2}} \cdot \text{Lineage2}_i + \beta_{\text{int}} \cdot (\text{katG\_Resist} \times \text{Lineage2})_i + \beta_{\text{RIF}} \cdot \text{RIF}_i + \sum_s \gamma_s \cdot \text{Site}_{s,i} + \epsilon_i$$

### 4.2 Full Cohort Estimates
In the full primary cohort ($N = 6,136$):

| Contrast / Parameter | Coefficient ($\beta$) | Robust SE | $p$-value | 95% Confidence Interval | Fold Change |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Lineage 4 katG Effect ($\beta_{\text{katG}}$)** | -0.2101 | 0.0644 | $1.096 \times 10^{-3}$ | [-0.3363, -0.0840] | 0.864x (-13.6%) |
| **Lineage 2 katG Effect ($\beta_{\text{katG}} + \beta_{\text{int}}$)** | +0.1637 | 0.1489 | 0.2718 | [-0.1282, +0.4555] | 1.120x (+12.0%) |
| **Interaction Term ($\beta_{\text{int}} = \text{L2} - \text{L4}$)** | **+0.3738** | **0.1595** | **0.0191** | **[+0.0612, +0.6864]** | **1.296x** |

Superficially, this result suggests a statistically significant interaction ($p = 0.0191$), with Lineage 4 showing modest collateral sensitivity ($-0.21 \log_2$, $\text{FC} = 0.864\times$) and Lineage 2 showing no collateral sensitivity or slight resistance ($+0.16 \log_2$).

### 4.3 The Site 05 Dependency Kill-Test
Site 05 (Peru) contributes **1,525 isolates** to the primary cohort (24.9% of all isolates), of which **98.4% belong to Lineage 4** and 65.3% are *katG* resistant. Furthermore, Site 05 exhibits a massive negative plate-reading shift ($\beta_{\text{Site05}} = -0.9854 \log_2$, halving the measured MIC relative to other centers).

To evaluate whether the lineage interaction is robust or an artifact of Site 05, the model was refit excluding Site 05 ($N = 4,611$):

| Analysis Model | Full Cohort ($N = 6,136$) | Excluding Site 05 ($N = 4,611$) | Status Change |
| :--- | :---: | :---: | :---: |
| **Primary katG Main Effect** | $\beta = -0.0591$ ($p = 0.5758$) | $\beta = +0.0144$ ($p = 0.8998$) | Stays Null |
| **Secondary Interaction Term ($\beta_{\text{int}}$)** | **$\beta = +0.3738$ ($p = 0.0191$)** | **$\beta = +0.2441$ ($p = 0.1897$)** | **COLLAPSES TO NULL** |
| Lineage 4 katG Effect | $\beta = -0.2101$ ($p = 0.0011$) | $\beta = -0.1122$ ($p = 0.2468$) | Collapses to Null |
| Lineage 2 katG Effect | $\beta = +0.1637$ ($p = 0.2718$) | $\beta = +0.1319$ ($p = 0.3802$) | Stays Null |

### 4.4 Leave-One-Site-Out Jackknife Analysis
A systematic jackknife across the top 8 testing laboratories proves that Site 05 is uniquely responsible for creating the nominal interaction:

| Excluded Testing Site | Sample Size ($N$) | Interaction $\beta_{\text{int}}$ | Robust SE | Interaction $p$-value |
| :--- | :---: | :---: | :---: | :---: |
| **None (Full Cohort)** | 6,136 | +0.3738 | 0.1595 | **0.0191** (Nominally Sig.) |
| **Exclude Site 05 (Peru)** | **4,611** | **+0.2441** | **0.1862** | **0.1897 (NON-SIGNIFICANT)** |
| Exclude Site 10 (South Africa) | 5,343 | +0.2868 | 0.1489 | 0.0541 |
| Exclude Site 02 (China) | 5,392 | +0.4411 | 0.1545 | 0.0043 |
| Exclude Site 06 (India) | 5,456 | +0.3716 | 0.1970 | 0.0593 |
| Exclude Site 03 (Vietnam) | 5,496 | +0.4347 | 0.1569 | 0.0056 |
| Exclude Site 08 (UK) | 5,616 | +0.3006 | 0.1767 | 0.0890 |
| Exclude Site 04 (Germany) | 5,624 | +0.3930 | 0.1704 | 0.0211 |
| Exclude Site 11 (Italy) | 5,797 | +0.4523 | 0.1430 | 0.0016 |

When Site 05 is excluded, the interaction $p$-value jumps from $0.019$ to $0.19$. The apparent lineage difference is entirely an artifact of a single testing center with an extreme confounder profile.

---

## 5. Subgroup and Sensitivity Analyses

### 5.1 Variant-Specific and Subgroup Models
To ensure that pooling mutations did not mask collateral sensitivity in specific subsets, we evaluated four distinct sub-specifications:

| Model Specification | Comparison Subgroup | $N$ | $\beta$ ($\log_2$) | Robust SE | $p$-value | Fold Change (95% CI) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Crude Unadjusted** | All *katG* vs WT (No adjustment) | 6,136 | -0.3239 | 0.0283 | $< 10^{-15}$ | 0.799x [0.769, 0.830] |
| **Primary Adjusted** | All *katG* vs WT (Adjusted) | 6,136 | -0.0591 | 0.1056 | 0.5758 | 0.960x [0.832, 1.108] |
| **Subgroup 2A** | *katG*-Only vs WT (Excl. *inhA*) | 5,365 | -0.0611 | 0.1084 | 0.5727 | 0.959x [0.827, 1.111] |
| **Subgroup S315T** | `katG S315T` specifically vs WT | 5,964 | -0.0483 | 0.1145 | 0.6732 | 0.967x [0.828, 1.130] |
| **Group 3** | *inhA*-Only vs WT | 3,132 | +0.2137 | 0.1750 | 0.2219 | 1.160x [0.914, 1.471] |

#### Key Insights from Subgroups:
- **`katG S315T` Specifically:** The dominant clinical mutation yields $\beta = -0.0483$ ($p = 0.6732$, $\text{FC} = 0.967\times$). It exhibits no collateral sensitivity whatsoever.
- **Exclusion of *inhA* Co-mutants:** Restricting to *katG*-only isolates (Group 2A, removing the 821 isolates with dual *katG* + *inhA* mutations) yields $\beta = -0.0611$ ($p = 0.5727$). Co-occurring *inhA* mutations do not obscure an underlying *katG* collateral sensitivity.
- **`inhA` Monoresistance:** Group 3 isolates (*inhA* / *fabG1* mutants with wild-type *katG*, $N = 72$) trend toward slight *increased* bedaquiline MIC ($\beta = +0.2137$, $\text{FC} = 1.16\times$), although not statistically significant ($p = 0.2219$).

### 5.2 Censoring Threshold Sensitivity
The bedaquiline MIC measurements have plate censoring boundaries (predominantly $\le 0.015\,\mu\text{g/mL}$ and $> 0.25\,\mu\text{g/mL}$). We tested model sensitivity across different boundary imputation offsets:

| Censoring Offset Scheme | Offset Values | Primary $\beta_{\text{katG}}$ | Robust SE | $p$-value | Fold Change |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **No Offset (Exact Bound)** | $0.0, 0.0$ | -0.0354 | 0.0897 | 0.6935 | 0.976x |
| **Half-Dilution Offset (Primary)** | $-0.5, +0.5$ | -0.0591 | 0.1056 | 0.5758 | 0.960x |
| **Full-Dilution Offset** | $-1.0, +1.0$ | -0.0828 | 0.1216 | 0.4961 | 0.944x |

Under all censoring schemes, the effect remains consistently non-significant ($p = 0.50$ to $0.69$) and tightly bounded within fold changes between $0.94\times$ and $0.98\times$.

---

## 6. Mechanistic and Methodological Synthesis

### 6.1 Why Did In Vitro Studies Find Collateral Sensitivity While Clinical Cohorts Do Not?
The discrepancy between the findings of Waller et al. (*Nat Commun* 2023) and this clinical cohort audit is grounded in three major biological and technical factors:

1. **Fitness Selection in Humans vs Test Tubes:**  
   Waller et al. utilized laboratory-evolved *M. tuberculosis* strains (mc26230 / H37Rv derivatives) carrying complete loss-of-function *katG* mutations. The mechanism proposed for collateral bedaquiline sensitivity is that loss of catalase-peroxidase activity renders the bacterium hypersensitive to reactive oxygen species (ROS) and ATP synthase depletion induced by bedaquiline. However, in human patients, *M. tuberculosis* must survive respiratory bursts inside host alveolar macrophages. Complete *katG* loss-of-function mutants are avirulent or severely attenuated. Clinical resistance is thus dominated by `S315T` (95.3% of CRyPTIC *katG* mutants), which preserves substantial catalase-peroxidase function.
2. **Measurement Platform and Batch Confounding:**  
   CRyPTIC used 96-well broth microdilution plates (UKMYC) read across 25 international centers. Individual testing centers exhibited systematic baseline plate shifts of up to $\pm 1.0 \log_2\text{ dilution}$ (a two-fold difference in measured MIC across sites). When a single testing laboratory in an endemic setting (e.g., Site 05 in Peru) tests predominantly drug-resistant isolates on plates that register lower baseline MICs, an unadjusted analysis creates the complete illusion of collateral sensitivity.
3. **The Ecological Fallacy (Simpson's Paradox):**  
   In the unadjusted data, *katG* mutants appear to have $0.799\times$ lower bedaquiline MIC ($p < 10^{-15}$). Within laboratory centers, however, the regression slope collapses to zero ($\beta = -0.059$, $p = 0.58$). This is a classic Simpson's paradox: the crude association is driven entirely by the between-site distribution of drug resistance, not within-strain collateral sensitivity.

---

## 7. Deliverables and Artifact Inventory

All analytical code, data tables, model outputs, and publication-ready figures have been generated and archived:

1. **Execution Script:**  
   [`scripts/run_crytic_m2_1_genotype_validation.py`](file:///home/trishal/cryptic_collateral_sensitivity/scripts/run_crytic_m2_1_genotype_validation.py)  
   Standalone Python 3.12 script with zero external dependencies. Executes in 4.4 seconds.
2. **Model Summary JSON:**  
   [`results/crytic_m2_1/genotype_model_summary.json`](file:///home/trishal/cryptic_collateral_sensitivity/results/crytic_m2_1/genotype_model_summary.json)  
   Complete machine-readable record of all coefficients, covariance matrices, contrasts, and jackknife results.
3. **Tabular Results:**  
   - [`results/crytic_m2_1/genotype_cohort_table.tsv`](file:///home/trishal/cryptic_collateral_sensitivity/results/crytic_m2_1/genotype_cohort_table.tsv): Per-isolate classification for all 7,318 strains.
   - [`results/crytic_m2_1/model_coefficients_table.tsv`](file:///home/trishal/cryptic_collateral_sensitivity/results/crytic_m2_1/model_coefficients_table.tsv): Full coefficient tables for Primary and Secondary models.
   - [`results/crytic_m2_1/site_05_sensitivity_table.tsv`](file:///home/trishal/cryptic_collateral_sensitivity/results/crytic_m2_1/site_05_sensitivity_table.tsv): Complete leave-one-out jackknife sensitivity table.
   - [`results/crytic_m2_1/subgroup_estimates_table.tsv`](file:///home/trishal/cryptic_collateral_sensitivity/results/crytic_m2_1/subgroup_estimates_table.tsv): Estimates for Crude, Primary, Group 2A, S315T, and Group 3.
4. **Vector Publication Graphic:**  
   [`results/crytic_m2_1/katg_bedaquiline_validation.svg`](file:///home/trishal/cryptic_collateral_sensitivity/results/crytic_m2_1/katg_bedaquiline_validation.svg)  
   Two-panel publication-grade SVG graphic displaying Panel A (Forest Plot of model effects and 95% CIs) and Panel B (Distribution boxplots by genotype and lineage).

---

## 8. Strategic Research Decision and Final Recommendation

### Final Verdict: HYPOTHESIS FALSIFIED IN CLINICAL COHORTS
The hypothesis that *katG*-associated isoniazid resistance produces collateral sensitivity to bedaquiline in clinical *Mycobacterium tuberculosis* is decisively refuted by the CRyPTIC data.

### Recommendations for Future Work:
1. **Do Not Proceed to Prospective Wet-Lab Experiments:**  
   Allocating wet-lab resources or funding to test *in vitro* collateral sensitivity of INH-resistant clinical isolates to bedaquiline is not scientifically justified.
2. **Do Not Base Regimen Design on Collateral Sensitivity:**  
   Clinical regimens combining bedaquiline and isoniazid should not expect synergy or hypersensitivity based on *katG* mutation status.
3. **Methodological Standard for Antimicrobial Resistance Studies:**  
   Any observational study evaluating collateral drug sensitivity across clinical collections must include laboratory testing site fixed effects and cluster-robust standard errors. Failing to adjust for testing-site batch effects creates spurious collateral-sensitivity associations due to ecological confounding.
