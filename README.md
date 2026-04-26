# PSWI: Peak-Stress Water Index for Data Center Sustainability

> A composite metric, dataset, and policy framework for auditing the
> water sustainability of hyperscale and colocation data centers,
> integrating peak demand intensity (Han et al. 2026) with location-specific
> water stress (Wu et al. 2025 / WRI Aqueduct 4.0).

---

## What this repository contains

This repository accompanies the paper **"Hidden Currents: A Peak-Stress
Water Index for Auditing AI Data Center Sustainability"**, which proposes
a new metric (PSWI) for assessing the water sustainability of data
centers and analyzes 53 hyperscale and major colocation facilities
worldwide.

### Headline findings

- **4,100× disparity** in PSWI score between best and worst facility in
  the dataset (Hamina, Finland: 0.004; Phoenix, AZ: 14.78).
- **Microsoft drops 4 ranks** when the industry-standard WUE metric is
  replaced with PSWI, and **Digital Realty has the highest mean PSWI**
  of any audited company.
- **15× difference in real water-stress impact** between facilities
  reporting the same annual WUE.
- A counterfactual simulation suggests that reallocating just **10% of
  fleet workload** from worst-PSWI to best-PSWI facilities would yield a
  **33% reduction** in fleet-wide water-stress impact.

### Structure

```
.
├── data/
│   ├── datacenters.csv           # 53 audited facilities (location, WUE, source)
│   ├── water_stress.csv          # Baseline water stress (WRI Aqueduct 4.0)
│   ├── datacenters_scored.csv    # Facilities + computed PSWI scores
│   └── company_aggregates.csv    # Company-level rankings
├── code/
│   ├── pswi_calculator.py        # Core metric implementation
│   └── visualize.py              # All figures in the paper
├── figures/                      # Generated PNGs (300 DPI)
├── paper/
│   ├── section_1_introduction.tex
│   ├── ... (additional sections)
│   └── references.bib            # 47 citations
└── README.md
```

## Reproducing the results

### Requirements

```bash
pip install pandas numpy matplotlib
```

That's it. We deliberately depend only on stable, widely-available
libraries to maximize reproducibility.

### Run

```bash
# 1. Compute PSWI scores for all facilities
python code/pswi_calculator.py

# 2. Generate all six figures
python code/visualize.py
```

Both scripts print their key findings to stdout and write outputs to
`data/` and `figures/` respectively.

## Data sources

Every datum in `data/datacenters.csv` is traceable to a public source:

| Source | What we pulled |
|---|---|
| Google 2024 Environmental Report | Site-specific WUE for Google's 16 facilities |
| Microsoft 2024 Sustainability Report | Fleet-average WUE (site-level inferred where unavailable) |
| Meta 2025 Sustainability Report | Fleet-average WUE |
| Amazon 2024 Sustainability Report | Fleet-average WUE |
| Equinix, Digital Realty, QTS, etc. | Company-wide WUE from each company's 2024 sustainability report |
| WRI Aqueduct 4.0 ([wri.org/aqueduct](https://www.wri.org/aqueduct)) | Baseline Water Stress (BWS) by catchment |
| LBNL 2024 Data Center Energy Report | Fleet-share weighting (where applicable) |

## How PSWI is calculated

```
PSWI(facility)  =  pWUE(facility)  ×  BWS(facility's location)
                =  WUE_annual × peaking_factor × BWS_raw
```

where:
- `WUE_annual` is the annual Water Usage Effectiveness in L/kWh as
  reported by the operator
- `peaking_factor` is the ratio of peak-day to average-day water demand,
  here estimated by Köppen climate zone (1.8 for cool/subarctic to 8.0
  for hot-arid; see `code/pswi_calculator.py` for full mapping)
- `BWS_raw` is the dimensionless baseline water-stress ratio
  (water demand / supply) from WRI Aqueduct 4.0

A higher PSWI means the facility's water consumption falls
disproportionately on a water-stressed region during peak demand
periods.

## Limitations

We document our assumptions transparently. Notable caveats:

1. **Peaking factors are estimated, not observed.** Operators rarely
   disclose peak water demand. We use climate-zone-conditional defaults
   below the typical range documented by Han et al. (2026) (peaking
   factors of 6–10), so our findings are conservative.
2. **Annualized BWS averages out seasonal stress.** The Aqueduct 4.0
   monthly dataset would refine this; a future version of this work
   will integrate it.
3. **Company-wide WUE is sometimes the only public figure.** Where
   site-specific WUE is unavailable, we apply the company's reported
   fleet average. This biases against companies that disclose more.
4. **Scope 2 (off-site electricity-related water) is not included** in
   this version, consistent with the framing of Han et al. (2026).

## Citation

If you use this dataset or code, please cite:

```bibtex
@article{pswi2026,
  title  = {Hidden Currents: A Peak-Stress Water Index for Auditing AI Data Center Sustainability},
  author = {[Your Name]},
  year   = {2026},
  note   = {Working paper}
}
```

## License

Code: MIT License. Data: CC BY 4.0. WRI Aqueduct data is also CC BY 4.0;
sustainability-report values are public-domain factual statements.
