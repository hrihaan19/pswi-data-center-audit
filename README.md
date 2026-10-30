# PSWI: Peak-Stress Water Index for Data Center Sustainability

> A composite metric, dataset, and policy framework for auditing the
> water sustainability of hyperscale and colocation data centers,
> combining peak demand (Han et al. 2026) with location-specific water
> stress (Wu et al. 2025 / WRI Aqueduct 4.0).

This repository accompanies the preprint **"Hidden Currents: A Peak-Stress
Water Index for Auditing AI Data Center Sustainability and Informing
Disclosure Policy"** (version 3, October 2026), in `main_v3.pdf`.

## Headline Findings (v3)

- **48 facilities, 7 operators.** Every WUE value is published by the
  operator or derived from its published totals (`wue_basis` column).
- **~1,500× range** in PSWI, from Microsoft Dublin (0.006) to Google
  Henderson, NV (9.22).
- **267× within one operator at identical WUE:** all Google facilities
  carry the same derived fleet WUE (0.96 L/kWh), yet Henderson, NV and
  Hamina, Finland differ 267-fold in PSWI, purely from location.
- **Company rankings shift** under PSWI vs. published WUE (Spearman
  ρ = 0.71), but bootstrap 95% intervals for every company's shift
  include zero; treat company-level shifts as illustrative.
- **Location drives the results.** The climate-based peaking factor is
  correlated with water stress (r = 0.84); removing it entirely leaves
  facility and company rankings nearly unchanged (ρ = 0.96).
- **Idealized counterfactual:** frictionless reallocation of 10% of
  workload from the highest- to lowest-PSWI third lowers aggregate PSWI
  by 35% (95% interval 21–46% under assumed input uncertainty). This is
  an upper bound, not a forecast.
- **Disclosure gap:** no audited operator publishes facility-level WUE or
  peak/monthly water data.

## Repository Contents

All files sit at the top level of the repository.

| File | What it is |
|---|---|
| `main_v3.pdf` | The preprint (version 3) |
| `main.tex`, `references.bib` | LaTeX source (IEEEtran) |
| `datacenters.csv` | v3 dataset: 48 facilities, sourced WUE (`wue_basis`, `wue_source` columns) |
| `datacenters_v2.csv` | Earlier working dataset, kept for transparency |
| `dataset_changelog_v3.csv` | Every v2 → v3 change, with reasons |
| `water_stress.csv` | Baseline water stress (WRI Aqueduct 4.0) |
| `datacenters_scored.csv`, `company_aggregates.csv` | PSWI scores and company rankings |
| `sensitivity_beta.csv`, `bootstrap_rank_shifts.csv`, `variance_decomposition.csv`, `beta_null_specification.csv`, `sensitivity_output_v3.txt` | Robustness-analysis outputs |
| `figure_1` … `figure_11` (`.png`) | Figures (300 DPI) |
| `rebuild_dataset_v3.py` | Applies the documented v2 → v3 corrections |
| `pswi_calculator.py` | Core PSWI computation |
| `visualize.py` | Figures 1–6 |
| `sensitivity.py` | Figures 7–11: β sensitivity, bootstrap, variance decomposition, counterfactual, Scope 2, β = 1 null specification |

## Reproducing the Results

From the repository folder:

```bash
pip install pandas numpy scipy matplotlib

python rebuild_dataset_v3.py   # v2 -> v3 dataset (logs every change)
python pswi_calculator.py      # PSWI scores and company rankings
python visualize.py            # Figures 1-6
python sensitivity.py          # Figures 7-11 and robustness numbers
```

## Data Provenance and the v3 Correction

An earlier working version (v2) assigned facility-specific WUE values to
Google and Microsoft facilities that do not appear in those companies'
reports: Google publishes per-site water volumes but no WUE, and Microsoft
publishes WUE only by region. v2 also included five facilities that could
not be verified or did not meet the inclusion criteria (a duplicate Google
site, Meta Richland Parish, AWS Coffeen IL, Digital Realty Salt Lake City,
and xAI Memphis, for which no WUE is published). v3 replaces every WUE with
a published or published-derived value and removes those five facilities.
All 52 changes are logged in `dataset_changelog_v3.csv`.

| Operator | WUE (L/kWh) | Year | Basis | Source |
|---|---|---|---|---|
| Google | 0.96 | 2023 | Derived: 6.1 bn gal ÷ 24 TWh | Google 2024 Environmental Report |
| Meta | 0.19 | 2024 | Fleet (withdrawal basis) | Meta 2025 Environmental Data Index |
| Amazon Web Services | 0.18 | 2023 | Fleet | AWS 2023 sustainability summary |
| Microsoft (Americas / EMEA / APAC) | 0.38 / 0.03 / 0.03 | FY24 | Regional | Microsoft datacenter efficiency page |
| Equinix | 0.95 | 2024 | Fleet | Equinix 2024 Sustainability Data Summary |
| Digital Realty | 0.59 | 2025 | Fleet | Digital Realty 2025 Impact Report |
| QTS | 0.82 | 2024 | Fleet | QTS 2024 Sustainability Report |

## How PSWI Is Calculated

```
PSWI = WUE_annual × β × BWS_raw
```

- `WUE_annual`: operator-published WUE (L/kWh), fleet or regional
- `β`: peaking factor (peak-day ÷ average-day water use), *assumed* by
  climate class (1.8–8.0); not disclosed by any operator
- `BWS_raw`: Aqueduct 4.0 baseline water stress ratio (demand ÷ supply)

## Limitations

1. No operator publishes facility-level WUE, so within-operator variation
   reflects location only, not facility efficiency.
2. Peaking factors are assumed by climate class and correlated with BWS.
3. BWS values are annual, rounded, and assigned manually by metro area; a
   geospatial join to Aqueduct catchments is a planned improvement.
4. Scope 2 (electricity-related) water is excluded from the main
   specification; a crude stress test adding 3.14 L/kWh gives ρ = 0.88.

## Citation

```bibtex
@misc{bhutani2026pswi,
  title  = {Hidden Currents: A Peak-Stress Water Index for Auditing AI Data
            Center Sustainability and Informing Disclosure Policy},
  author = {Bhutani, Hrihaan},
  year   = {2026},
  note   = {Preprint, version 3}
}
```

## License

Code: MIT. Data: CC BY 4.0. WRI Aqueduct data are CC BY 4.0.

## Contact

Hrihaan Bhutani (hribhu19@gmail.com)
