"""
PSWI (Peak-Stress Water Index) Calculator
==========================================

A novel composite metric for assessing data center water sustainability that
combines:
  (1) Peak water demand intensity  (from Han et al. 2026's pWUE concept)
  (2) Local water stress           (from WRI Aqueduct 4.0 / SCARF approach)

PSWI = pWUE x BWS_raw

where:
  pWUE  = peak Water Usage Effectiveness (L/kWh) = WUE_annual * peaking_factor
  BWS   = Baseline Water Stress (raw demand/supply ratio from WRI Aqueduct)

A higher PSWI score means a data center's water consumption falls
disproportionately on a water-stressed region during peak demand periods.

Author: [Your Name]
Affiliation: [Your School]
License: MIT
Repository: https://github.com/[your-username]/pswi-data-center-audit
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants and Defaults
# ---------------------------------------------------------------------------

# Default peaking factor when not disclosed by the operator.
# Han et al. (2026) document peaking factors of 6-10 for evaporative cooling
# during the hottest summer days. We use a conservative default of 4.0,
# which is below their average and biases AGAINST our hypothesis (i.e., makes
# our findings more conservative, not less).
DEFAULT_PEAKING_FACTOR = 4.0

# Climate-zone-adjusted peaking factors based on cooling-degree-day variance.
# Hot/arid climates need much more peak cooling water than mild climates.
PEAKING_FACTOR_BY_CLIMATE = {
    'hot_arid':       8.0,   # Phoenix, Las Vegas, Saudi Arabia
    'hot_humid':      6.0,   # Texas, Georgia, Singapore, Florida
    'temperate':      4.0,   # Virginia, Iowa, most US Midwest
    'mild':           2.5,   # Pacific Northwest, Ireland, UK
    'cool':           1.8,   # Sweden, Finland, Norway, subarctic
}

# Mapping locations to climate zones (based on Koppen-Geiger classification
# and on-the-record cooling profiles of these specific facilities).
# Sources: NOAA climate normals, ASHRAE climate zone designations.
CLIMATE_ZONES = {
    'Council Bluffs':'temperate', 'The Dalles':'mild', 'Pryor OK':'temperate',
    'Douglasville':'hot_humid', 'Lenoir':'temperate', 'Tennessee':'temperate',
    'Goose Creek SC':'hot_humid', 'Henderson NV':'hot_arid',
    'Ashburn VA':'temperate', 'Eemshaven':'cool', 'Hamina':'cool',
    'Dublin Ireland':'mild', 'Saint-Ghislain':'mild', 'Changhua Taiwan':'hot_humid',
    'Singapore':'hot_humid', 'Quincy WA':'mild', 'San Antonio':'hot_humid',
    'Goodyear AZ':'hot_arid', 'Boydton VA':'temperate', 'West Des Moines':'temperate',
    'Amsterdam':'mild', 'Tuas SG':'hot_humid', 'Prineville OR':'mild',
    'Fort Worth':'hot_humid', 'Lulea':'cool', 'Clonee':'mild',
    'Newton County':'hot_humid', 'Los Lunas':'hot_arid', 'Eagle Mountain UT':'hot_arid',
    'Mesa AZ':'hot_arid', 'Richland Parish':'hot_humid', 'Boardman':'mild',
    'Hilliard':'temperate', 'Coffeen IL':'temperate', 'Frankfurt':'mild',
    'San Jose CA':'temperate', 'El Segundo CA':'temperate', 'Dallas TX':'hot_humid',
    'London UK':'mild', 'Manassas VA':'temperate', 'Garland TX':'hot_humid',
    'Chandler AZ':'hot_arid', 'Salt Lake City':'hot_arid', 'Suwanee GA':'hot_humid',
    'Richmond VA':'temperate', 'Memphis':'hot_humid',
}


# ---------------------------------------------------------------------------
# Mapping data centers to water-stress lookup keys
# ---------------------------------------------------------------------------

def _location_key(row):
    """Map a data center row to a key in the water_stress table.

    We do this manually rather than by lat/long because Aqueduct values are
    catchment-level, and our locations are already mapped to known catchments.
    """
    city = row['city']
    state = row['state_province']

    # Map cities to lookup keys (this is our hand-curated mapping)
    direct = {
        'Council Bluffs':'Council Bluffs', 'The Dalles':'The Dalles',
        'Pryor':'Pryor OK', 'Douglasville':'Douglasville', 'Lenoir':'Lenoir',
        'Goose Creek':'Goose Creek SC', 'Henderson':'Henderson NV',
        'Ashburn':'Ashburn VA', 'Eemshaven':'Eemshaven', 'Hamina':'Hamina',
        'Dublin':'Dublin Ireland', 'Saint-Ghislain':'Saint-Ghislain',
        'Changhua':'Changhua Taiwan', 'Jurong':'Singapore', 'Quincy':'Quincy WA',
        'San Antonio':'San Antonio', 'Goodyear':'Goodyear AZ',
        'Boydton':'Boydton VA', 'West Des Moines':'West Des Moines',
        'Amsterdam':'Amsterdam', 'Tuas':'Tuas SG', 'Prineville':'Prineville OR',
        'Fort Worth':'Fort Worth', 'Lulea':'Lulea', 'Clonee':'Clonee',
        'Newton County':'Newton County', 'Los Lunas':'Los Lunas',
        'Eagle Mountain':'Eagle Mountain UT', 'Mesa':'Mesa AZ',
        'Richland Parish':'Richland Parish', 'Boardman':'Boardman',
        'Hilliard':'Hilliard', 'Coffeen':'Coffeen IL',
        'Frankfurt am Main':'Frankfurt', 'San Jose':'San Jose CA',
        'El Segundo':'El Segundo CA', 'Dallas':'Dallas TX', 'London':'London UK',
        'Manassas':'Manassas VA', 'Garland':'Garland TX',
        'Chandler':'Chandler AZ', 'Salt Lake City':'Salt Lake City',
        'Suwanee':'Suwanee GA', 'Richmond':'Richmond VA', 'Memphis':'Memphis',
        'Singapore':'Singapore'
    }
    if city in direct:
        return direct[city]

    # Tennessee fallback
    if state == 'Tennessee':
        return 'Tennessee'
    return city


# ---------------------------------------------------------------------------
# Core PSWI calculation
# ---------------------------------------------------------------------------

def compute_pswi(datacenter_df, water_stress_df,
                 peaking_factor_strategy='climate_zone',
                 default_peaking=DEFAULT_PEAKING_FACTOR):
    """Compute PSWI scores for every data center in our dataset.

    Parameters
    ----------
    datacenter_df : pandas.DataFrame
        Master data center dataset with WUE values.
    water_stress_df : pandas.DataFrame
        Water stress lookup table (BWS values from WRI Aqueduct 4.0).
    peaking_factor_strategy : {'climate_zone', 'fixed', 'conservative'}
        How we estimate peaking factors when undisclosed.
        - 'climate_zone' : differentiated by Koppen climate zone
        - 'fixed'        : use `default_peaking` for every facility
        - 'conservative' : use 2.0 (the absolute minimum from Han et al.)
    default_peaking : float
        Peaking factor to use under 'fixed' strategy.

    Returns
    -------
    pandas.DataFrame
        Original data center rows enriched with:
          location_key, bws_raw, climate_zone, peaking_factor,
          pwue, pswi, pswi_rank
    """
    df = datacenter_df.copy()

    # Map each facility to its water stress lookup key.
    df['location_key'] = df.apply(_location_key, axis=1)

    # Merge in water stress data.
    stress_lookup = water_stress_df.set_index('location_key')['bws_raw'].to_dict()
    df['bws_raw'] = df['location_key'].map(stress_lookup)

    # Flag any unmatched locations (data quality check).
    if df['bws_raw'].isna().any():
        unmatched = df[df['bws_raw'].isna()]['location_key'].unique()
        print(f"Warning: unmatched locations: {unmatched}")

    # Assign climate zone and peaking factor.
    df['climate_zone'] = df['location_key'].map(CLIMATE_ZONES).fillna('temperate')

    if peaking_factor_strategy == 'climate_zone':
        df['peaking_factor'] = df['climate_zone'].map(PEAKING_FACTOR_BY_CLIMATE)
    elif peaking_factor_strategy == 'conservative':
        df['peaking_factor'] = 2.0
    else:
        df['peaking_factor'] = default_peaking

    # Compute pWUE (peak Water Usage Effectiveness, in L/kWh).
    df['pwue'] = df['annual_wue_l_per_kwh'] * df['peaking_factor']

    # Compute PSWI = pWUE * BWS_raw (water stress weighting).
    df['pswi'] = df['pwue'] * df['bws_raw']

    # Rank facilities (higher PSWI = worse).
    df['pswi_rank'] = df['pswi'].rank(method='dense', ascending=False).astype(int)

    return df


# ---------------------------------------------------------------------------
# Helper: company-level aggregation
# ---------------------------------------------------------------------------

def company_aggregate(scored_df):
    """Compute company-level PSWI aggregates.

    Returns a DataFrame indexed by company with:
      - mean_wue           : self-reported fleet-average WUE (industry metric)
      - mean_pswi          : average PSWI across this company's facilities
      - max_pswi           : the company's worst-PSWI facility
      - n_facilities       : how many of this company's facilities we audited
      - reported_rank      : ranking by mean WUE (low = "looks good")
      - pswi_rank_company  : ranking by mean PSWI (low = "actually good")
      - rank_shift         : reported_rank - pswi_rank_company
                             (positive = company looks worse under PSWI;
                              negative = company looks better)
    """
    g = scored_df.groupby('company').agg(
        mean_wue       =('annual_wue_l_per_kwh','mean'),
        mean_pswi      =('pswi','mean'),
        max_pswi       =('pswi','max'),
        n_facilities   =('facility_id','count'),
    ).reset_index()

    g['reported_rank']     = g['mean_wue'].rank(method='dense', ascending=True).astype(int)
    g['pswi_rank_company'] = g['mean_pswi'].rank(method='dense', ascending=True).astype(int)
    g['rank_shift']        = g['reported_rank'] - g['pswi_rank_company']
    return g.sort_values('mean_pswi')


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    DATA = Path(__file__).parent.parent / 'data'

    # Load datasets.
    dc      = pd.read_csv(DATA / 'datacenters.csv')
    stress  = pd.read_csv(DATA / 'water_stress.csv', comment='#')

    print(f"Loaded {len(dc)} data centers across {dc['company'].nunique()} companies")
    print(f"Loaded {len(stress)} water stress records\n")

    # Compute PSWI for all facilities.
    scored = compute_pswi(dc, stress, peaking_factor_strategy='climate_zone')

    # Save the scored dataset for downstream use.
    scored.to_csv(DATA / 'datacenters_scored.csv', index=False)

    # ------------------------------------------------------------------
    # Print key findings
    # ------------------------------------------------------------------
    print("=" * 72)
    print("TOP 10 WORST PSWI FACILITIES (most water-stressed peak impact)")
    print("=" * 72)
    print(scored.nlargest(10, 'pswi')[
        ['company','facility_name','city','state_province',
         'annual_wue_l_per_kwh','peaking_factor','bws_raw','pswi']
    ].to_string(index=False))

    print()
    print("=" * 72)
    print("TOP 10 BEST PSWI FACILITIES")
    print("=" * 72)
    print(scored.nsmallest(10, 'pswi')[
        ['company','facility_name','city','state_province',
         'annual_wue_l_per_kwh','peaking_factor','bws_raw','pswi']
    ].to_string(index=False))

    # ------------------------------------------------------------------
    # The Shell Game: company-level rank shifts
    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("THE SHELL GAME: Company Rankings under WUE vs PSWI")
    print("=" * 72)
    company = company_aggregate(scored)
    print(company.to_string(index=False))

    # Save company aggregates
    company.to_csv(DATA / 'company_aggregates.csv', index=False)

    print(f"\nResults saved to {DATA}")
