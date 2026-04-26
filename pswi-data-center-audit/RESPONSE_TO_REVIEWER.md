# Response to Reviewer

**Paper:** *Hidden Currents: A Peak-Stress Water Index for Auditing AI Data Center Sustainability and Informing Mandatory Disclosure Policy*
**Author:** Hrihaan Bhutani
**Status:** Revised in response to professor's review

---

## Cover Note

I am deeply grateful for your detailed and rigorous review. The critique was the single most useful input I have received on this work, and I have spent the past several days revising substantially. The revised paper integrates new analyses for nine of your fourteen points; below I respond to each in detail, marking the points addressed in the revision (✅), partially addressed (◐), and explicitly deferred to future work with justification (○).

I have aimed to be transparent about my limitations as a high school student researcher with a one-week revision timeline: where I cannot achieve the gold-standard fix (e.g., obtaining real monthly water data), I have implemented the strongest available substitute and explicitly documented the gap.

---

## Critical Fixes

### #1 — Validate the peaking factor table ✅ (substantial revision)

**Your concern:** β is estimated from climate zones rather than measured; lacks justification.

**My response:** I implemented a two-part sensitivity analysis (new Section VI.E and Figure 6):

1. **Uniform rescaling test:** Spearman ρ(baseline rank, β×0.5 rank) = ρ(baseline, β×2.0) = 1.000. By construction, since β is constant within climate zones, uniform rescaling preserves rankings exactly. I now state this explicitly in the paper.

2. **Per-facility independent perturbation:** This is the stricter test you implicitly asked for. Each facility's β is independently perturbed by U(–50%, +50%) over 1,000 Monte Carlo runs. **Results: mean Spearman ρ = 0.982; 5th percentile ρ = 0.975; mean top-10 worst overlap = 7.9/10.** Rankings are robust to plausibly large per-facility β misspecification.

**What I did NOT do (and why):** I did not obtain real monthly water consumption data because Google's monthly data is fleet-aggregated (not per-facility) and other operators publish nothing. A real measurement-based β table is the highest-priority extension and is now flagged as such in Section VIII.

### #2 — Add proper uncertainty propagation ✅

**Your concern:** The Monte Carlo only added ±10% noise to the output; not real uncertainty propagation.

**My response:** Section VII.A now propagates documented relative uncertainty through all three inputs simultaneously:
- WUE ± 15% (corporate reporting precision, consistent with one-significant-figure reporting)
- BWS ± 25% (PCR-GLOBWB 2 model uncertainty per Aqueduct 4.0 technical note)
- β ± 30% (Han et al. 2026 observed range of 6–10 against our default of 8.0)

**Updated headline finding:** At 10% reallocation, median impact reduction = 36.7%, **95% CI [26.1%, 47.0%]**, 50% CI [33.3%, 40.5%]. Confidence intervals are now reported alongside every counterfactual claim. The lower 95% bound of 26% remains substantial.

### #3 — Justify the sampling frame ✅

**Your concern:** No defense of the n=53 sample.

**My response:** New Section V.A adds explicit inclusion criteria: (i) hyperscale or major colocation operator at MW-scale IT load; (ii) operator publishes either site-specific or fleet WUE for 2023 or 2024; (iii) physical location publicly known to the metropolitan-area level; (iv) catchment covered by Aqueduct 4.0. I also estimate the sample covers approximately **35–45% of total U.S. hyperscale IT capacity** reported in LBNL 2024, and explicitly note that coverage is best for U.S. and Northern European hyperscalers; weakest for South / Southeast Asia; entirely absent for mainland China.

---

## Important Fixes

### #4 — Justify the multiplicative functional form ✅

**Your concern:** Why PSWI = A × B × C and not A × B + C or a weighted geometric mean?

**My response:** Two-part justification in new Section IV.B:

1. **Theoretical:** Stressed water systems exhibit threshold behavior: an additional liter in an unstressed basin produces marginal harm; an additional liter in a basin where demand exceeds renewable supply produces nonlinearly greater harm. Peak consumption similarly compounds in stressed systems. Multiplication captures this; addition does not.

2. **Empirical (the strongest argument):** A formal variance decomposition of log(PSWI) across our 53 facilities (new Section VI.D and Figure 5) shows that **covariance terms account for 46.7% of cross-facility variance**, dominating the 22.1% (WUE), 27.2% (BWS), and 4.9% (β) marginal contributions. The dominance of covariance is the empirical signature of compounding harm: an additive composite would discard this information.

This was the single highest-leverage analysis you suggested, and it strengthens the paper substantially.

### #5 — Replace n=8 company ranking with something statistically defensible ✅ (with honest reframing)

**Your concern:** n=8 companies is too few to make rank-shift claims.

**My response:** I implemented bootstrap resampling (2,000 iterations, resampling within-company facilities with replacement) and report 95% CIs on every company-level rank shift (new Section VI.A and Figure 2):

- **xAI's 5-position improvement is statistically significant** (95% CI: [+3, +5], excludes zero)
- **Microsoft's 3-position deterioration is suggestive but not significant** (95% CI: [-5, +1])
- **Equinix and Digital Realty similarly suggestive** (95% CIs: [-4, 0])

I now describe these as "**suggestive directional evidence**" and explicitly identify the **facility-level findings (n=53) as the primary statistical contribution**. The n=8 company-level ranking is downgraded to illustrative; the n=53 facility-level analysis (4,100× disparity, same-operator case study, variance decomposition) carries the empirical weight.

### #6 — Use monthly BWS not annual ○ (deferred with justification)

**Your concern:** Annual BWS is conceptually inconsistent with PSWI's peak-day numerator.

**My response:** You are correct. This is the single most important conceptual extension I am unable to complete in the revision window because Aqueduct 4.0 monthly data is supplied as raster GIS files at 5-arcminute resolution and requires GIS tooling I cannot access in this timeframe. I have flagged this prominently in Box 1 (limitations) and in Section VIII as the "highest-priority extension." The current annual-BWS result should therefore be read as a conservative lower bound: switching to July/August BWS would amplify findings in the U.S. Southwest, since their annual averaging dilutes peak-summer stress.

### #7 — Same-operator case study ✅

**Your concern:** Cross-company "same WUE, different impact" comparison confounds reporting methodology with location.

**My response:** New Section VI.C presents an in-Google comparison that controls for methodology completely:
- **Google Lenoir, NC:** WUE = 0.7 L/kWh, BWS = 0.18, β = 4.0, PSWI = 0.504
- **Google Henderson, NV:** WUE = 0.9 L/kWh, BWS = 1.20, β = 8.0, PSWI = 8.64

Same operator, similar self-reported WUE (within 0.2 L/kWh), **17× PSWI ratio**. Methodology cannot explain this; only location and climate can.

---

## Moderate Fixes

### #8 — Variance decomposition ✅

**Your concern:** Decomposing variance in log(PSWI) would tell you which input drives variation.

**My response:** Implemented in new Section VI.D and Figure 5. Findings:
- log(BWS): 27.2%
- log(WUE): 22.1%
- log(β): 4.9%
- Covariance terms: 46.7%

This is now both a finding (location stress and efficiency dominate marginal variation) and a methodological justification (covariance dominance justifies multiplication; #4).

### #9 — Expand international coverage ○ (acknowledged, deferred)

**Your concern:** Zero coverage of Chinese hyperscalers.

**My response:** I was unable to add Chinese hyperscalers responsibly within the revision window. Alibaba and Tencent publish only partial fleet-aggregated WUE; their facility locations exist in industry databases but linking facility to disclosed WUE requires negotiation with industry sources. I have prominently flagged this gap in Section V.A (sampling frame) and Section VIII (limitations).

### #10 — Scope 2 robustness check ✅

**Your concern:** Excluding Scope 2 may bias findings; preempt this.

**My response:** New Section VI.F adds the test using a uniform US grid average of 1.5 L/kWh (EPRI/NREL benchmark). Results: Spearman ρ(Scope 1 rank, Scope 1+2 rank) = **0.946**; **7 of 10 worst-PSWI facilities preserved**; mean absolute rank change 3.32 positions. **Findings are robust to Scope 2 inclusion at the rank level.** A future revision will use state-specific grid mix data.

### #11 — Stress-test SEC Reg S-K analogy ◐ (partial)

**Your concern:** The SEC analogy is underdeveloped.

**My response:** Section VII.B now explicitly engages with the SEC's actual climate disclosure rules (final March 2024, partially stayed) and proposes how the same architecture (tiered phase-in by issuer size, graduated assurance requirements, materiality thresholds) maps to a PSWI disclosure regime: hyperscale operators (>50 MW IT) phase in first; >5 MW second; below threshold exempt. I have not done a full regulatory law review, which would warrant a separate paper.

---

## Presentation Fixes

### #12 — Formal propositions ✅

**Your concern:** Cosmetic formality of the metric properties.

**My response:** Section IV.C now presents three properties as Proposition 1 (Monotonicity, with proof), Proposition 2 (Decomposability), and Proposition 3 (Edge-case correctness).

### #13 — Move limitations earlier and quantify ✅

**Your concern:** Limitations are at the end; not quantified.

**My response:** New Box 1 (yellow-bordered, immediately after the metric definition in Section IV.D) summarizes known limitations with **specific numerical bounds**: β estimation ±30% (with sensitivity result Spearman ρ=0.982), BWS ±25%, annual-vs-monthly BWS averaging, and Scope 2 omission. Readers calibrate before reading the results section.

### #14 — Split metric paper from policy paper ○ (declined)

**Your concern:** Two papers in one; cut to develop one fully.

**My response:** I appreciate the principle (focus is better than breadth) but respectfully disagree about its application here. The metric is the policy's intervention point; without the policy framing the metric is technically interesting but actionably empty. Conversely, a policy proposal without the metric is hand-wavy. The two halves reinforce each other in one paper. The policy section is now condensed (one page vs. v1's two pages) so the methodological core gets the room it needs. If the venue requires further compression I would cut Section VII.B's SEC discussion to a footnote.

---

## Summary of Changes

| Section | What changed |
|---|---|
| Abstract | Added all new robustness numbers (37%, 95% CI, 17× same-operator, ρ=0.982) |
| §I Introduction | Five contributions clearly stated; new contribution (3) on robustness testing |
| §IV Metric | Added Box 1 (quantified limitations), Section IV.B (multiplicative justification), three formal propositions |
| §V Methodology | Explicit sampling-frame defense, coverage estimate vs. LBNL 2024 |
| §VI Results | Six new analyses: bootstrap (B), same-operator (C), variance decomposition (D), β sensitivity (E), Scope 2 (F) |
| §VII Policy | Counterfactual reports full uncertainty propagation; SEC analogy expanded with phase-in design |
| §VIII Limitations | Now explicitly references the new sensitivity analyses; flags monthly BWS as #1 priority |
| Figures | 4 new figures (7, 8, 9, 10); existing 6 retained |
| Code | New `code/sensitivity.py` (450 lines); reproduces all new analyses |
| Bibliography | 35 cited references unchanged; bib file holds 47 |

---

## Asks of the Reviewer

If you have time, I would value your view on:

1. **Whether the bootstrap reframing of company rankings is satisfactory.** I am downgrading those claims rather than abandoning them; honest reviewers may disagree on the right move.
2. **Whether the variance decomposition argument is sufficient to justify multiplication.** I find the 46.7% covariance share compelling but a stricter formal test (e.g., AIC comparison vs. additive composite) might be warranted.
3. **Whether the coverage estimate (35–45% of LBNL hyperscale capacity) is defensible** given the disclosure gaps.

Thank you again for the time you put into this. I hope to be working in this space for years and your review materially improved both the paper and my understanding of how to do this work.

Sincerely,
Hrihaan Bhutani
Emerald High School
hribhu19@gmail.com
