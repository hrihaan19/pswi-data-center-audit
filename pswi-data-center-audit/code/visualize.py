"""
Visualization script for PSWI paper.

Produces 6 original figures:
  1. Shell Game Chart: Self-reported WUE rank vs. PSWI rank (rank-shift dumbbell)
  2. The 4000x Disparity: PSWI score distribution by company (boxplot/strip)
  3. Geographic Heatmap: Global map of facilities colored by PSWI
  4. The Hidden Cost of Annual Reporting: WUE vs PSWI scatter
  5. Climate Zone vs Water Stress: How peaking and stress combine
  6. Counterfactual Simulation: water saved under PSWI-aware workload migration
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from pathlib import Path

# ---------------------------------------------------------------------------
# Style setup - clean, professional, publication-ready
# ---------------------------------------------------------------------------
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

ROOT = Path(__file__).parent.parent
DATA = ROOT / 'data'
FIG  = ROOT / 'figures'

# Color palette - colorblind-safe
COLORS = {
    'best':   '#1b9e77',  # green
    'good':   '#66c2a5',  # light green
    'neutral':'#888888',  # gray
    'bad':    '#fc8d62',  # orange
    'worst':  '#d62728',  # red
    'accent': '#7570b3',  # purple
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
scored  = pd.read_csv(DATA / 'datacenters_scored.csv')
company = pd.read_csv(DATA / 'company_aggregates.csv')


# ---------------------------------------------------------------------------
# FIGURE 1: The Shell Game (rank-shift dumbbell chart)
# ---------------------------------------------------------------------------

def figure_1_shell_game():
    """The flagship 'Shell Game' chart: WUE vs PSWI rankings.

    A dumbbell chart showing where each company would rank by their
    self-reported WUE (industry-standard metric) versus where they rank
    under our stress-weighted PSWI. The shift exposes greenwashing.
    """
    fig, ax = plt.subplots(figsize=(11, 6.5))

    # Sort by WUE rank for cleaner visual
    df = company.sort_values('reported_rank').reset_index(drop=True)
    n  = len(df)
    y  = np.arange(n)

    # Dumbbells: line + two endpoints
    for i, row in df.iterrows():
        x0, x1 = row['reported_rank'], row['pswi_rank_company']
        line_color = (COLORS['worst'] if x1 > x0 else
                      COLORS['best']  if x1 < x0 else COLORS['neutral'])
        # Line connecting the two points
        ax.plot([x0, x1], [i, i], color=line_color, linewidth=2.5,
                alpha=0.6, zorder=2)
        # Self-reported (WUE) endpoint
        ax.scatter(x0, i, s=120, color=COLORS['neutral'],
                   edgecolor='black', linewidth=1.2, zorder=3)
        # PSWI endpoint (highlighted)
        ax.scatter(x1, i, s=180, color=line_color,
                   edgecolor='black', linewidth=1.5, zorder=4)
        # Label rank shift
        if x1 != x0:
            shift_label = f"{'↓' if x1>x0 else '↑'}{abs(x1-x0)}"
            mid_x = (x0 + x1) / 2
            ax.text(mid_x, i + 0.32, shift_label, ha='center',
                    fontsize=9, fontweight='bold', color=line_color)

    # Y-axis: company names
    ax.set_yticks(y)
    ax.set_yticklabels(df['company'], fontsize=11)
    ax.invert_yaxis()  # reported_rank = 1 at top

    ax.set_xlabel('Rank  (1 = best, 8 = worst)')
    ax.set_xticks(np.arange(1, n+1))
    ax.set_xlim(0.5, n + 0.5)

    # Custom legend
    legend_elements = [
        Line2D([0],[0], marker='o', color='w', label='Self-reported WUE rank',
               markerfacecolor=COLORS['neutral'], markeredgecolor='black',
               markersize=10),
        Line2D([0],[0], marker='o', color='w', label='PSWI rank — looks worse',
               markerfacecolor=COLORS['worst'], markeredgecolor='black',
               markersize=11),
        Line2D([0],[0], marker='o', color='w', label='PSWI rank — looks better',
               markerfacecolor=COLORS['best'], markeredgecolor='black',
               markersize=11),
    ]
    ax.legend(handles=legend_elements, loc='lower right',
              frameon=True, fancybox=True, shadow=False)

    ax.set_title('The Shell Game: Self-Reported WUE Rankings vs. Stress-Weighted PSWI Rankings',
                 fontweight='bold', pad=14)

    # Footnote
    fig.text(0.02, -0.02,
             'Source: Authors\' analysis using corporate sustainability reports (2023-2024) '
             'and WRI Aqueduct 4.0 baseline water stress data.\n'
             'PSWI = peaking-adjusted WUE × baseline water stress; lower is better.',
             fontsize=8, style='italic', color='#444')

    out = FIG / 'figure_1_shell_game.png'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 2: The 4000x Disparity
# ---------------------------------------------------------------------------

def figure_2_disparity():
    """Show the actual PSWI distribution to illustrate the massive disparity
    between best and worst facilities (4000x in our dataset)."""
    fig, ax = plt.subplots(figsize=(11, 6))

    order = (scored.groupby('company')['pswi'].median()
                   .sort_values().index.tolist())

    positions = np.arange(len(order))
    for i, comp in enumerate(order):
        d = scored.loc[scored['company'] == comp, 'pswi'].values
        # Strip plot
        jitter = (np.random.RandomState(42 + i).rand(len(d)) - 0.5) * 0.35
        ax.scatter(positions[i] + jitter, d, s=55,
                   color=COLORS['accent'], alpha=0.65,
                   edgecolor='black', linewidth=0.4, zorder=3)
        # Median bar
        med = np.median(d)
        ax.plot([positions[i] - 0.28, positions[i] + 0.28], [med, med],
                color=COLORS['worst'], lw=2.5, zorder=4)

    ax.set_yscale('log')
    ax.set_xticks(positions)
    ax.set_xticklabels(order, rotation=15, ha='right')
    ax.set_ylabel('PSWI score  (log scale)')
    ax.set_title('PSWI Distribution by Company: A 4,000× Disparity Hidden by Annual Averages',
                 fontweight='bold', pad=14)
    ax.grid(True, axis='y', linestyle=':', alpha=0.5, which='both')

    # Annotate worst and best facilities
    worst = scored.loc[scored['pswi'].idxmax()]
    best  = scored.loc[scored['pswi'].idxmin()]
    ax.annotate(f"Worst: {worst['facility_name']}, {worst['state_province']}\nPSWI = {worst['pswi']:.2f}",
                xy=(order.index(worst['company']), worst['pswi']),
                xytext=(0.65, 0.93), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color=COLORS['worst']),
                fontsize=9, color=COLORS['worst'], fontweight='bold')
    ax.annotate(f"Best: {best['facility_name']} ({best['country']})\nPSWI = {best['pswi']:.4f}",
                xy=(order.index(best['company']), best['pswi']),
                xytext=(0.05, 0.07), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color=COLORS['best']),
                fontsize=9, color=COLORS['best'], fontweight='bold')

    legend_elements = [
        Line2D([0],[0], marker='o', color='w', label='Individual facility',
               markerfacecolor=COLORS['accent'], markeredgecolor='black',
               markersize=8),
        Line2D([0],[0], color=COLORS['worst'], lw=2.5, label='Median for company'),
    ]
    ax.legend(handles=legend_elements, loc='lower right')

    out = FIG / 'figure_2_disparity.png'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 3: Geographic Map (using a basic equirectangular projection)
# ---------------------------------------------------------------------------

def figure_3_world_map():
    """A simple world map showing all facilities colored by PSWI.

    Built without GeoPandas to keep dependencies minimal. Uses raw lat/long
    on a basic equirectangular projection with hand-drawn continent outlines
    (none — we just plot points; readers know geography).
    """
    fig, ax = plt.subplots(figsize=(13, 6.5))

    # Color by PSWI (continuous scale)
    pswi_vals = scored['pswi'].values
    # Use log scale for color since PSWI spans 4 orders of magnitude
    log_pswi = np.log10(pswi_vals + 0.001)

    sc = ax.scatter(scored['longitude'], scored['latitude'],
                    c=log_pswi, cmap='RdYlGn_r',
                    s=140, edgecolor='black', linewidth=0.6,
                    alpha=0.85, zorder=3)

    # Shade approximate land regions for orientation (rough rectangles)
    land_regions = [
        (-130, -65, 25, 50, 'North America'),    # CONUS
        (-10, 30, 35, 70, 'Europe'),              # Europe
        (95, 145, -10, 45, 'East/SE Asia'),       # E. Asia
    ]
    for x0, x1, y0, y1, _label in land_regions:
        ax.add_patch(mpatches.Rectangle((x0, y0), x1-x0, y1-y0,
                     facecolor='#e9e9e9', edgecolor='none',
                     alpha=0.4, zorder=1))

    ax.set_xlim(-140, 160)
    ax.set_ylim(-15, 75)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, linestyle=':', alpha=0.3, zorder=0)
    ax.set_title('Global PSWI Distribution: Hyperscale and Major Colocation Data Centers',
                 fontweight='bold', pad=14)

    # Colorbar
    cbar = plt.colorbar(sc, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label('log\u2081\u2080(PSWI score)', rotation=270, labelpad=15)

    # Annotate the worst offenders
    worst5 = scored.nlargest(5, 'pswi')
    for _, row in worst5.iterrows():
        ax.annotate(row['facility_name'],
                    xy=(row['longitude'], row['latitude']),
                    xytext=(8, 8), textcoords='offset points',
                    fontsize=8, color=COLORS['worst'], fontweight='bold')

    out = FIG / 'figure_3_world_map.png'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 4: WUE vs PSWI scatter
# ---------------------------------------------------------------------------

def figure_4_wue_vs_pswi():
    """Reveal that there's only weak correlation between low WUE and low PSWI.

    The strongest 'green' signal in current corporate disclosure (low WUE)
    explains only a fraction of true stress-adjusted impact.
    """
    fig, ax = plt.subplots(figsize=(9.5, 7))

    # Color by climate zone for additional storytelling
    climate_colors = {
        'cool':       '#3182bd',
        'mild':       '#74c476',
        'temperate':  '#fdae6b',
        'hot_humid':  '#e6550d',
        'hot_arid':   '#a50f15',
    }

    for cz, group in scored.groupby('climate_zone'):
        ax.scatter(group['annual_wue_l_per_kwh'], group['pswi'],
                   c=climate_colors[cz], label=cz.replace('_',' ').title(),
                   s=110, alpha=0.85, edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Self-Reported Annual WUE (L/kWh)')
    ax.set_ylabel('PSWI Score (peak × stress)')
    ax.set_yscale('log')
    ax.set_title('Why Annual WUE Hides the Truth: Same WUE, Vastly Different Impact',
                 fontweight='bold', pad=14)

    # Annotate two facilities with similar WUE but very different PSWI
    # to show the dispersion explicitly
    near_wue_15 = scored[(scored['annual_wue_l_per_kwh'] >= 1.2) & 
                          (scored['annual_wue_l_per_kwh'] <= 1.6)]
    if len(near_wue_15) >= 2:
        worst_in_band = near_wue_15.loc[near_wue_15['pswi'].idxmax()]
        best_in_band  = near_wue_15.loc[near_wue_15['pswi'].idxmin()]
        ratio = worst_in_band['pswi'] / max(best_in_band['pswi'], 1e-6)
        ax.annotate('', xy=(worst_in_band['annual_wue_l_per_kwh'], worst_in_band['pswi']),
                    xytext=(best_in_band['annual_wue_l_per_kwh'], best_in_band['pswi']),
                    arrowprops=dict(arrowstyle='<->', color=COLORS['worst'], lw=1.5))
        mid_x = (worst_in_band['annual_wue_l_per_kwh'] + best_in_band['annual_wue_l_per_kwh']) / 2
        mid_y = np.sqrt(worst_in_band['pswi'] * max(best_in_band['pswi'], 1e-6))
        ax.text(mid_x * 1.05, mid_y, f'{ratio:.0f}× difference\n(same reported WUE)',
                fontsize=10, color=COLORS['worst'], fontweight='bold')

    ax.legend(title='Climate Zone', loc='upper left')
    ax.grid(True, linestyle=':', alpha=0.5, which='both')

    out = FIG / 'figure_4_wue_vs_pswi.png'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 5: Counterfactual simulation
# ---------------------------------------------------------------------------

def figure_5_counterfactual():
    """Monte Carlo simulation: how much water-stress impact would be averted
    if regulators forced PSWI-aware workload reallocation?

    Scenario: progressively reallocate workload from worst-PSWI facilities
    (ranked by stress impact) to best-PSWI facilities. The fraction X on
    the x-axis means: of the total fleet workload, X% gets shifted from
    the worst tier to the best tier, distributed proportionally.
    """
    rng = np.random.default_rng(seed=42)
    df = scored[['company','facility_name','pswi','annual_wue_l_per_kwh',
                 'peaking_factor','bws_raw']].copy().reset_index(drop=True)

    n = len(df)
    fractions = np.linspace(0, 0.50, 100)  # 0% to 50% of total workload
    n_runs = 300                            # Monte Carlo runs

    impacts_runs = np.zeros((n_runs, len(fractions)))

    for run in range(n_runs):
        # Add 10% Gaussian noise to PSWI to model uncertainty in peaking
        # factors and water-stress estimates.
        pswi_noisy = df['pswi'].values * (1 + rng.normal(0, 0.10, n))
        pswi_noisy = np.maximum(pswi_noisy, 1e-4)

        # Sort facilities by PSWI (ascending = best to worst).
        sorted_idx = np.argsort(pswi_noisy)

        # Define the source tier (worst third) and the sink tier (best third).
        # Using thirds (not deciles) creates more realistic dispersion
        # because real fleets have many medium-impact facilities.
        third = max(1, n // 3)
        worst_tier = sorted_idx[-third:]    # to be drained
        best_tier  = sorted_idx[:third]     # to absorb

        # Total fleet workload normalized to n (each facility has 1 baseline).
        total_workload = n

        for j, frac in enumerate(fractions):
            workload = np.ones(n)
            # Total workload to migrate (e.g., 20% of fleet)
            migration = frac * total_workload

            # Drain from worst tier proportionally to their PSWI
            # (worse facilities give up more workload first)
            worst_pswi = pswi_noisy[worst_tier]
            worst_share = worst_pswi / worst_pswi.sum()
            drain = migration * worst_share
            workload[worst_tier] -= drain
            workload[worst_tier] = np.maximum(workload[worst_tier], 0)

            # Calculate how much we actually drained (in case of clipping).
            actual_migration = (1.0 - workload[worst_tier]).sum() - 0
            actual_migration = migration - max(0, drain.sum() - actual_migration)
            actual_migration = max(0, total_workload - workload.sum())

            # Distribute to best tier inversely proportional to PSWI
            # (best facilities absorb the most workload).
            best_pswi = pswi_noisy[best_tier]
            best_inverse = (1.0 / best_pswi)
            best_share = best_inverse / best_inverse.sum()
            workload[best_tier] += actual_migration * best_share

            impacts_runs[run, j] = (workload * pswi_noisy).sum()

    median = np.median(impacts_runs, axis=0)
    p10    = np.percentile(impacts_runs, 10, axis=0)
    p90    = np.percentile(impacts_runs, 90, axis=0)
    baseline = median[0]

    # Convert to % reduction (positive = good).
    pct_red_med = 100 * (1 - median / baseline)
    pct_red_p10 = 100 * (1 - p90 / baseline)
    pct_red_p90 = 100 * (1 - p10 / baseline)

    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.fill_between(fractions * 100, pct_red_p10, pct_red_p90,
                    color=COLORS['accent'], alpha=0.25,
                    label='10–90% confidence band')
    ax.plot(fractions * 100, pct_red_med, color=COLORS['accent'], lw=2.5,
            label='Median impact reduction')

    # Mark policy-relevant thresholds
    for tgt in [10, 20, 30]:
        idx = np.argmin(np.abs(fractions * 100 - tgt))
        ax.axvline(tgt, ymin=0, ymax=pct_red_med[idx]/max(pct_red_med)*0.97,
                   ls=':', color='gray', alpha=0.4)
        ax.scatter([tgt], [pct_red_med[idx]], color=COLORS['worst'],
                   s=80, zorder=5, edgecolor='black', linewidth=1)
        ax.annotate(f'{pct_red_med[idx]:.0f}% reduction\nat {tgt}% reallocation',
                    xy=(tgt, pct_red_med[idx]),
                    xytext=(tgt + 1.5, pct_red_med[idx] - 4),
                    fontsize=9, color=COLORS['worst'], fontweight='bold')

    ax.set_xlabel('% of Fleet Workload Reallocated (worst third → best third by PSWI)')
    ax.set_ylabel('Reduction in Total Fleet PSWI Impact (%)')
    ax.set_title('Counterfactual: PSWI-Aware Workload Reallocation Yields Outsized Stress Reductions',
                 fontweight='bold', pad=14)
    ax.legend(loc='lower right')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_xlim(0, 50)
    ax.set_ylim(0, max(pct_red_p90.max(), 70))

    out = FIG / 'figure_5_counterfactual.png'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 6: Disclosure compliance heatmap
# ---------------------------------------------------------------------------

def figure_6_disclosure_compliance():
    """Show which companies disclose enough information to even be auditable.

    For each company we score whether they publish:
      A. Annual fleet-wide WUE
      B. Site-specific WUE (per facility)
      C. Peak / monthly WUE
      D. Per-site water source (potable vs. reclaimed)
      E. Per-site water withdrawal AND consumption (separate)
    """
    # Hand-coded based on actual review of 2024 sustainability reports
    disclosure_data = {
        'Google':         [1, 1, 0, 0.5, 0.5],
        'Microsoft':      [1, 0.5, 0, 0.5, 0],
        'Meta':           [1, 0, 0, 0.5, 0],
        'Amazon':         [1, 0, 0, 0, 0],
        'Apple':          [1, 0.5, 0, 0.5, 0.5],
        'Equinix':        [1, 0, 0, 0, 0],
        'DigitalRealty':  [1, 0, 0, 0, 0],
        'QTS':            [1, 0, 0, 0, 0],
        'CyrusOne':       [1, 0, 0, 0, 0],
        'xAI':            [0, 0, 0, 0, 0],
        'Alibaba':        [0.5, 0, 0, 0, 0],
        'Tencent':        [0.5, 0, 0, 0, 0],
    }
    categories = ['Annual fleet WUE', 'Site-specific WUE',
                  'Peak / monthly WUE', 'Water source',
                  'Withdrawal vs. consumption']

    df = pd.DataFrame(disclosure_data, index=categories).T
    # Sort companies by total disclosure score
    df['total'] = df.sum(axis=1)
    df = df.sort_values('total', ascending=False).drop(columns='total')

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(df.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(np.arange(len(categories)))
    ax.set_xticklabels(categories, rotation=22, ha='right')
    ax.set_yticks(np.arange(len(df)))
    ax.set_yticklabels(df.index)

    # Annotate each cell
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            v = df.iloc[i, j]
            label = '✓' if v == 1 else ('partial' if v == 0.5 else '✗')
            color = 'black' if v >= 0.5 else 'white'
            ax.text(j, i, label, ha='center', va='center',
                    color=color, fontsize=10, fontweight='bold')

    ax.set_title('Disclosure Compliance: Which Companies Publish Enough Data to Audit?',
                 fontweight='bold', pad=14)

    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_ticks([0, 0.5, 1.0])
    cbar.set_ticklabels(['Not disclosed', 'Partial', 'Disclosed'])

    out = FIG / 'figure_6_disclosure.png'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    FIG.mkdir(exist_ok=True)
    figure_1_shell_game()
    figure_2_disparity()
    figure_3_world_map()
    figure_4_wue_vs_pswi()
    figure_5_counterfactual()
    figure_6_disclosure_compliance()
    print(f"\nAll figures saved to: {FIG}")
