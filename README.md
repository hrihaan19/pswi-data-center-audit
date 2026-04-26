# PSWI: Peak-Stress Water Index for Data Center Sustainability

> A composite metric, dataset, and policy framework for auditing the
> water sustainability of hyperscale and colocation data centers,
> integrating peak demand intensity (Han et al. 2026) with location-
> specific water stress (Wu et al. 2025 / WRI Aqueduct 4.0).

---

## What This Repository Contains

This repository accompanies the paper **"Hidden Currents: A Peak-Stress
Water Index for Auditing AI Data Center Sustainability and Informing
Mandatory Disclosure Policy"**, which proposes a new metric (PSWI) for
assessing the water sustainability of AI data centers and analyzes 53
hyperscale and major colocation facilities worldwide.

## Headline Findings

- **4,100× disparity** between the best and worst PSWI facility in the
  dataset (Hamina, Finland: 0.0036; Phoenix, AZ: 14.78).
- **Same-operator 17× ratio:** Google's Lenoir, NC (PSWI 0.504) and
  Henderson, NV (PSWI 8.64) report similar self-reported WUE but
  differ 17× in real water-stress impact, controlling for reporting
  methodology.
- **Variance decomposition:** location stress accounts for 27.2% and
  efficiency for 22.1% of cross-facility variation in log(PSWI), while
  covariance terms account for 46.7% — the empirical signature of
  compounding harm and the justification for the metric's
  multiplicative form.
- **β robustness:** under per-facility ±50% perturbation of the
  peaking factor (1,000 Monte Carlo runs), facility rankings remain
  highly stable (mean Spearman ρ = 0.982; mean top-10 worst overlap
  7.9/10).
- **Policy counterfactual:** with full uncertainty propagated through
  WUE (±15%), BWS (±25%), and β (±30%), reallocating just **10% of
  fleet workload** from worst-PSWI to best-PSWI facilities yields a
  fleet-wide impact reduction of **36.7%** (95% CI [26.1%, 47.0%]).

## Repository Structure

```
.
├── paper/
│   ├── main_v2.tex               # LaTeX source (revised paper)
│   ├── main_v2.pdf               # Compiled paper (8 pages, IEEE format)
│   └── references.bib            # 47 citations
├── code/
│   ├── pswi_calculator.py        # Core PSWI metric implementation
│   ├── visualize.py              # Generates figures 1–6
│   └── sensitivity.py            # Generates figures 7–10 (revisions)
├── data/
│   ├── datacenters.csv           # 53 audited facilities (location, WUE, source)
│   ├── water_stress.csv          # Baseline water stress (WRI Aqueduct 4.0)
│   ├── datacenters_scored.csv    # Facilities with computed PSWI scores
│   ├── company_aggregates.csv    # Company-level rankings
│   ├── sensitivity_beta.csv      # β sensitivity analysis output
│   ├── bootstrap_rank_shifts.csv # Bootstrap company-rank CIs
│   └── variance_decomposition.csv# Variance decomposition output
├── figures/                       # 10 publication-quality PNGs (300 DPI)
├── RESPONSE_TO_REVIEWER.md        # Formal response to peer review
└── README.md
```

## Reproducing the Results

### Requirements

```bash
pip install pandas numpy matplotlib scipy
```

That's it. We deliberately depend only on stable, widely-available
libraries to maximize reproducibility.

### Running the Full Pipeline

```bash
# 1. Compute PSWI scores for all facilities
python code/pswi_calculator.py

# 2. Generate the original 6 figures
python code/visualize.py

# 3. Run sensitivity, bootstrap, variance decomposition (figures 7–10)
python code/sensitivity.py
```

Each script prints its key findings to stdout and writes outputs to
`data/` and `figures/`.

## Data Sources

Every datum in `data/datacenters.csv` is traceable to a public source:

| Source | What we pulled |
|---|---|
| Google 2024–25 Environmental Reports | Site-specific WUE for Google's facilities |
| Microsoft 2024 Sustainability Report | Fleet-average WUE |
| Meta 2025 Sustainability Report | Fleet-average WUE |
| Amazon 2024 Sustainability Report | Fleet-average WUE |
| Equinix, Digital Realty, QTS sustainability reports | Company-wide WUE |
| WRI Aqueduct 4.0 ([wri.org/aqueduct](https://www.wri.org/aqueduct)) | Baseline Water Stress (BWS) by catchment |
| LBNL 2024 Data Center Energy Report | Fleet-share weighting |

## How PSWI Is Calculated

```
PSWI(facility) = pWUE(facility) × BWS(facility's location)
              = WUE_annual × β × BWS_raw
```

where:
- `WUE_annual` is the annual Water Usage Effectiveness in L/kWh as
  reported by the operator
- `β` is the peaking factor (ratio of peak-day to average-day water
  demand), here estimated by Köppen climate zone (range 1.8–8.0)
- `BWS_raw` is the dimensionless baseline water-stress ratio (water
  demand / supply) from WRI Aqueduct 4.0

A higher PSWI means the facility's water consumption falls
disproportionately on a water-stressed region during peak demand
periods.

See `paper/main_v2.pdf` Section IV for the formal definition,
properties (with proofs), and justification of the multiplicative form.

## Limitations

We document our assumptions transparently:

1. **Peaking factors are estimated, not observed.** Operators rarely
   disclose peak water demand. We use climate-zone-conditional defaults
   set at or below the lower end of Han et al.'s observed range.
   Sensitivity analysis (`code/sensitivity.py`) shows rankings remain
   stable under ±50% per-facility β perturbation (mean ρ = 0.982).
2. **Annualized BWS averages out seasonal stress.** Aqueduct 4.0
   monthly data would refine this; switching to monthly BWS is the
   highest-priority extension and is flagged in the paper.
3. **Company-wide WUE used where site-specific is unavailable.**
   Where site-specific WUE is unavailable, we apply the company's
   fleet average. This biases against more transparent companies.
4. **Scope 2 (off-site electricity-related) water excluded.** A
   robustness check (Section VI.F) shows findings are preserved when
   1.5 L/kWh of estimated grid water is added uniformly (Spearman ρ =
   0.946).

## Citation

If you use this dataset or code, please cite:

```bibtex
@article{bhutani2026pswi,
  title  = {Hidden Currents: A Peak-Stress Water Index for Auditing
            AI Data Center Sustainability and Informing Mandatory
            Disclosure Policy},
  author = {Bhutani, Hrihaan},
  year   = {2026},
  note   = {Working paper}
}
```

## License

Code: MIT License. Data: CC BY 4.0. WRI Aqueduct data is also CC BY
4.0; sustainability-report values are public-domain factual statements.

## Contact

Hrihaan Bhutani — hribhu19@gmail.com
