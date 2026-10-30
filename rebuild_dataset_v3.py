"""
Rebuild datacenters.csv (v3) so every WUE value traces to a published source.

Run once from the repository root:  python code/rebuild_dataset_v3.py
It reads data/datacenters_v2.csv (the earlier working version, kept for
transparency), applies the documented corrections below, and writes
data/datacenters.csv. A human-readable log is written to
data/dataset_changelog_v3.csv.

Why: in v2, per-facility WUE values for Google (16 sites) and Microsoft
(8 sites) were attributed to company reports that do not contain them.
Google publishes per-site water volumes (gallons) but no WUE; Microsoft
publishes WUE only by region. v3 replaces every WUE with a value that is
either published directly or derived arithmetically from published totals.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'

dc = pd.read_csv(DATA / 'datacenters_v2.csv')
log = []

def note(fid, field, old, new, reason):
    log.append(dict(facility_id=fid, field=field, old=old, new=new, reason=reason))

# ---------------------------------------------------------------------------
# 1. Remove rows that fail the inclusion criteria or could not be verified
# ---------------------------------------------------------------------------
DROP = {
    'GOOG-DAL': 'Duplicate of GOOG-DLS (same city, same catchment, same source); '
                'Google reports The Dalles as one location.',
    'META-RIC': 'Richland Parish, LA was under construction during the '
                'reporting years; absent from Meta facility-level water tables.',
    'AMZN-TX':  'No public evidence of an AWS data center in Coffeen, IL; '
                'location could not be verified.',
    'DRT-SLC':  'No Digital Realty data center in Salt Lake City could be '
                'verified (SLC operators are DataBank, Aligned, EdgeConneX).',
    'XAI-MEM':  'xAI publishes no WUE; v2 value (1.5 L/kWh) was an unsourced '
                'estimate. Fails inclusion criterion (ii).',
}
for fid, why in DROP.items():
    note(fid, 'row', 'present', 'removed', why)
dc = dc[~dc['facility_id'].isin(DROP)].copy()

# ---------------------------------------------------------------------------
# 2. Fix location / naming errors
# ---------------------------------------------------------------------------
def setv(fid, col, val, why):
    i = dc.index[dc['facility_id'] == fid][0]
    note(fid, col, dc.at[i, col], val, why)
    dc.at[i, col] = val

setv('GOOG-MON', 'city', 'Clarksville',
     'v2 city "Pryor" (Oklahoma) caused the Tennessee site to receive '
     "Oklahoma's water stress value; Google's Montgomery County site is in Clarksville, TN.")
setv('GOOG-MON', 'facility_name', 'Montgomery County',
     'Name retained; city corrected.')
setv('AMZN-CA', 'facility_name', 'Columbus area (CMH)',
     'v2 name "Loudoun (CMH)" mislabelled an Ohio site with a Virginia county.')
setv('AMZN-CA', 'facility_id', 'AMZN-OH', 'ID matched to state.')
setv('AMZN-IA', 'facility_id', 'AMZN-OR', 'ID matched to state (Boardman, OR).')

# ---------------------------------------------------------------------------
# 3. Replace WUE with published (or published-derived) values
# ---------------------------------------------------------------------------
GAL_TO_L = 3.785411784
GOOGLE_WUE = round(6.1e9 * GAL_TO_L / 24e9, 2)   # 23.09e9 L / 24e9 kWh = 0.96

MSFT_AMERICAS, MSFT_EMEA, MSFT_APAC = 0.38, 0.03, 0.03   # FY24 regional WUE
MSFT_REGION = {'USA': MSFT_AMERICAS, 'Ireland': MSFT_EMEA,
               'Netherlands': MSFT_EMEA, 'Singapore': MSFT_APAC}

SRC = {
    'Google': (GOOGLE_WUE, 2023, 'derived_fleet',
               'Derived: Google 2024 Environmental Report, 2023 data-center water '
               'consumption (6.1 billion gal) / data-center electricity (24 TWh)'),
    'Meta': (0.19, 2024, 'reported_fleet',
             'Meta 2025 Environmental Data Index, annual data center WUE (2024; '
             'withdrawal basis)'),
    'Amazon': (0.18, 2023, 'reported_fleet',
               'AWS 2023 sustainability summary, global data center WUE'),
    'Equinix': (0.95, 2024, 'reported_fleet',
                'Equinix 2024 Sustainability Data Summary, global portfolio WUE'),
    'DigitalRealty': (0.59, 2025, 'reported_fleet',
                      'Digital Realty 2025 Impact Report, global portfolio WUE'),
    'QTS': (0.82, 2024, 'reported_fleet',
            'QTS 2024 Sustainability Report, portfolio WUE'),
}

dc['wue_basis'] = ''
for i, r in dc.iterrows():
    old = r['annual_wue_l_per_kwh']
    if r['company'] == 'Microsoft':
        wue, yr, basis = MSFT_REGION[r['country']], 2024, 'reported_regional'
        region = {'USA': 'Americas', 'Singapore': 'Asia Pacific'}.get(r['country'], 'EMEA')
        src = f'Microsoft Datacenters efficiency page, FY24 regional WUE ({region})'
    else:
        wue, yr, basis, src = SRC[r['company']]
    if abs(old - wue) > 1e-9:
        note(r['facility_id'], 'annual_wue_l_per_kwh', old, wue,
             'Replaced with published value: ' + src)
    dc.at[i, 'annual_wue_l_per_kwh'] = wue
    dc.at[i, 'reported_year'] = yr
    dc.at[i, 'wue_basis'] = basis
    dc.at[i, 'wue_source'] = src
    if r['notes'] == 'Site-specific WUE disclosed':
        dc.at[i, 'notes'] = 'Google publishes site-level water volume, not site-level WUE'

dc.to_csv(DATA / 'datacenters.csv', index=False)
pd.DataFrame(log).to_csv(DATA / 'dataset_changelog_v3.csv', index=False)
print(f'v3 dataset: {len(dc)} facilities, {dc.company.nunique()} operators; '
      f'{len(log)} logged changes. Google derived WUE = {GOOGLE_WUE}')
