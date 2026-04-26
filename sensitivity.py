"""
Sensitivity, Bootstrap, and Variance Decomposition Analysis
============================================================

Addresses Professor's review comments:
  #1 - Sensitivity of beta (peaking factor)
  #2 - Real uncertainty propagation through WUE, BWS, beta
  #5 - Bootstrap rank-stability for company rankings
  #8 - Variance decomposition (log PSWI = log WUE + log beta + log BWS)
  #7 - Same-operator case study
  #10 - Scope 2 robustness check

Outputs new figures (figure_7..figure_10) and analytical tables for the
revision-response section of the paper.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import spearmanr

# -----------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
DATA = ROOT / 'data'
FIG  = ROOT / 'figures'

plt.rcParams.update({
    'font.family':'DejaVu Sans','font.size':10,
    'axes.titlesize':12,'axes.labelsize':11,
    'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,
    'figure.dpi':100,'savefig.dpi':300,'savefig.bbox':'tight',
    'axes.spines.top':False,'axes.spines.right':False,
})
COLORS = {'best':'#1b9e77','good':'#66c2a5','neutral':'#888888',
          'bad':'#fc8d62','worst':'#d62728','accent':'#7570b3'}

scored = pd.read_csv(DATA / 'datacenters_scored.csv')

# -----------------------------------------------------------------------------
# Documented uncertainties from the literature
# -----------------------------------------------------------------------------
WUE_REL_UNCERTAINTY  = 0.15  # Corporate reporting precision
BWS_REL_UNCERTAINTY  = 0.25  # PCR-GLOBWB 2 / Aqueduct 4.0 model uncertainty
BETA_REL_UNCERTAINTY = 0.30  # Han et al. (2026) observed peaking factor range


# =============================================================================
# Analysis 1 -- BETA SENSITIVITY
# =============================================================================
def beta_sensitivity():
    print("\n" + "="*72)
    print("ANALYSIS 1: BETA SENSITIVITY (Reviewer point #1)")
    print("="*72)

    # Test 1: Uniform multiplier (does the climate-zone framework hold up
    # if our entire peaking-factor table is biased by a constant?).
    multipliers = {'beta_half':0.5, 'beta_base':1.0, 'beta_double':2.0}
    rt = pd.DataFrame({
        'facility': scored['facility_name'],
        'city': scored['city'],
        'company': scored['company'],
        'baseline_pswi': scored['pswi'],
    })
    rt['baseline_rank'] = scored['pswi'].rank(method='dense', ascending=False).astype(int)
    for name, m in multipliers.items():
        new_pswi = scored['annual_wue_l_per_kwh'] * (scored['peaking_factor']*m) * scored['bws_raw']
        rt[f'{name}_pswi'] = new_pswi
        rt[f'{name}_rank'] = new_pswi.rank(method='dense', ascending=False).astype(int)

    base10 = set(rt.nsmallest(10,'baseline_rank')['facility'])
    half10 = set(rt.nsmallest(10,'beta_half_rank')['facility'])
    dbl10  = set(rt.nsmallest(10,'beta_double_rank')['facility'])
    rho_h, _ = spearmanr(rt['baseline_rank'], rt['beta_half_rank'])
    rho_d, _ = spearmanr(rt['baseline_rank'], rt['beta_double_rank'])

    print("\n[Test A] Uniform multiplier (β x 0.5, x 2.0):")
    print(f"  base ∩ (β×0.5):    {len(base10 & half10)}/10")
    print(f"  base ∩ (β×2.0):    {len(base10 & dbl10)}/10")
    print(f"  Spearman ρ (uniform): {rho_h:.4f} (×0.5), {rho_d:.4f} (×2.0)")
    print("  NOTE: ρ = 1.0 by construction since β is constant within climate zones.")

    # Test 2: STRICTER -- per-facility independent perturbation. This is the
    # honest test the reviewer would actually want: if EACH facility's
    # peaking factor is misspecified by a different random amount,
    # do rankings still hold?
    rng = np.random.default_rng(42)
    n_perturbations = 1000
    n = len(scored)
    rho_per_run = np.zeros(n_perturbations)
    top10_overlap = np.zeros(n_perturbations)
    base_top10 = set(rt.nsmallest(10,'baseline_rank')['facility'])

    for r in range(n_perturbations):
        # Each facility's beta is perturbed independently by U(-50%, +50%)
        perturb = 1.0 + rng.uniform(-0.5, 0.5, n)
        perturbed_pswi = scored['annual_wue_l_per_kwh'].values * \
                        (scored['peaking_factor'].values * perturb) * \
                        scored['bws_raw'].values
        perturbed_rank = pd.Series(perturbed_pswi).rank(method='dense', ascending=False).astype(int)
        rho_per_run[r], _ = spearmanr(rt['baseline_rank'], perturbed_rank)
        top10_set = set(scored.iloc[np.argsort(-perturbed_pswi)[:10]]['facility_name'])
        top10_overlap[r] = len(base_top10 & top10_set)

    print(f"\n[Test B] Per-facility independent ±50% perturbation ({n_perturbations} runs):")
    print(f"  Spearman ρ (mean): {rho_per_run.mean():.4f}")
    print(f"  Spearman ρ (5th pctl): {np.percentile(rho_per_run, 5):.4f}")
    print(f"  Top-10 overlap (mean): {top10_overlap.mean():.1f}/10")
    print(f"  Top-10 overlap (5th pctl): {np.percentile(top10_overlap, 5):.0f}/10")

    rt.to_csv(DATA / 'sensitivity_beta.csv', index=False)
    print(f"Saved: {DATA / 'sensitivity_beta.csv'}")

    # Figure: TWO-PANEL showing both tests
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: uniform multiplier
    ax = axes[0]
    df = rt.sort_values('baseline_rank').reset_index(drop=True)
    n_total = len(df)
    worst_idx = df.nsmallest(10,'baseline_rank').index
    for i in range(n_total):
        ranks = [df.loc[i,'beta_half_rank'], df.loc[i,'baseline_rank'], df.loc[i,'beta_double_rank']]
        ax.plot([0,1,2], ranks, color='gray', alpha=0.25, lw=0.6, zorder=2)
    for i in worst_idx:
        ranks = [df.loc[i,'beta_half_rank'], df.loc[i,'baseline_rank'], df.loc[i,'beta_double_rank']]
        ax.plot([0,1,2], ranks, color=COLORS['worst'], alpha=0.85, lw=1.5, zorder=4)
    ax.set_xticks([0,1,2])
    ax.set_xticklabels([r'$\beta \times 0.5$', r'$\beta_{\,\mathrm{base}}$', r'$\beta \times 2.0$'])
    ax.set_ylabel('Facility PSWI rank (1 = worst)')
    ax.invert_yaxis()
    ax.set_title('(a) Uniform $\\beta$ rescaling\n'
                 r'Spearman $\rho = 1.000$ (constant within climate zone)',
                 fontweight='bold')
    ax.grid(True, axis='y', linestyle=':', alpha=0.4)

    # Panel B: distribution of Spearman correlations under per-facility perturbation
    ax = axes[1]
    ax.hist(rho_per_run, bins=40, color=COLORS['accent'], edgecolor='black', alpha=0.8)
    ax.axvline(rho_per_run.mean(), color=COLORS['worst'], lw=2, linestyle='--',
               label=f'Mean $\\rho$ = {rho_per_run.mean():.3f}')
    ax.axvline(np.percentile(rho_per_run, 5), color='black', lw=1.2, linestyle=':',
               label=f'5th pctl = {np.percentile(rho_per_run, 5):.3f}')
    ax.set_xlabel(r'Spearman $\rho$ (baseline rank vs. perturbed rank)')
    ax.set_ylabel('Frequency')
    ax.set_title(f'(b) Per-facility $\\beta$ perturbation, $\\pm$50%\n'
                 f'{n_perturbations} runs; mean top-10 overlap = {top10_overlap.mean():.1f}/10',
                 fontweight='bold')
    ax.legend()
    ax.grid(True, axis='y', linestyle=':', alpha=0.4)

    plt.suptitle('Rank Stability under $\\beta$ Sensitivity', fontweight='bold', y=1.02)
    out = FIG / 'figure_7_beta_sensitivity.png'
    plt.savefig(out, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out}")

    return rho_h, rho_d, len(base10 & half10), len(base10 & dbl10), \
           rho_per_run.mean(), top10_overlap.mean()


# =============================================================================
# Analysis 2 -- BOOTSTRAP RANK STABILITY
# =============================================================================
def bootstrap_ranks(n_boot=2000):
    print("\n" + "="*72)
    print("ANALYSIS 2: BOOTSTRAP RANK STABILITY (Reviewer point #5)")
    print("="*72)
    print(f"Running {n_boot} bootstrap iterations...")

    rng = np.random.default_rng(42)
    companies = sorted(scored['company'].unique())
    nc = len(companies)
    shifts = np.zeros((n_boot, nc))
    pswi_ranks = np.zeros((n_boot, nc))
    wue_ranks  = np.zeros((n_boot, nc))

    for b in range(n_boot):
        rows = []
        for c in companies:
            sub = scored[scored['company']==c]
            if len(sub)==0:
                rows.append((c, np.nan, np.nan)); continue
            samp = sub.sample(n=len(sub), replace=True, random_state=int(rng.integers(1e9)))
            rows.append((c, samp['annual_wue_l_per_kwh'].mean(), samp['pswi'].mean()))
        bdf = pd.DataFrame(rows, columns=['company','mwue','mpswi']).set_index('company').reindex(companies)
        bdf['wr']  = bdf['mwue'].rank(method='dense', ascending=True).astype(int)
        bdf['pr']  = bdf['mpswi'].rank(method='dense', ascending=True).astype(int)
        bdf['sh']  = bdf['wr'] - bdf['pr']
        shifts[b]     = bdf['sh'].values
        pswi_ranks[b] = bdf['pr'].values
        wue_ranks[b]  = bdf['wr'].values

    summary = pd.DataFrame(index=companies)
    summary['mean_shift']   = shifts.mean(axis=0)
    summary['median_shift'] = np.median(shifts, axis=0)
    summary['ci_low']       = np.percentile(shifts, 2.5, axis=0)
    summary['ci_high']      = np.percentile(shifts, 97.5, axis=0)
    summary['significant']  = (summary['ci_low']>0) | (summary['ci_high']<0)

    print("\n95% CI on company rank shifts (positive = looks worse under PSWI):")
    print(summary.round(2).to_string())

    summary.to_csv(DATA / 'bootstrap_rank_shifts.csv')
    print(f"Saved: {DATA / 'bootstrap_rank_shifts.csv'}")

    # Figure
    fig, ax = plt.subplots(figsize=(11, 6))
    order = summary['mean_shift'].sort_values().index.tolist()
    for i, c in enumerate(order):
        idx = companies.index(c)
        data = shifts[:, idx]
        parts = ax.violinplot([data], positions=[i], widths=0.7,
                              showmeans=False, showmedians=False, showextrema=False)
        sig = summary.loc[c,'significant']
        face = (COLORS['worst'] if sig and summary.loc[c,'mean_shift']>0
                else COLORS['best'] if sig else COLORS['neutral'])
        for pc in parts['bodies']:
            pc.set_facecolor(face); pc.set_alpha(0.6)
        ax.plot([i,i], [summary.loc[c,'ci_low'], summary.loc[c,'ci_high']], color='black', lw=2)
        ax.scatter([i], [summary.loc[c,'mean_shift']], s=70, color='black', zorder=5)
    ax.axhline(0, color='black', lw=0.8, ls='--', alpha=0.6)
    ax.set_xticks(np.arange(len(order)))
    ax.set_xticklabels(order, rotation=15, ha='right')
    ax.set_ylabel('Rank shift (WUE rank $-$ PSWI rank)\n$> 0$ = looks worse under PSWI')
    ax.set_title(f'Bootstrap Distribution of Company Rank Shifts ({n_boot} resamples)\n'
                 f'95% CI shown as black bars; red = significant deterioration, green = significant improvement',
                 fontweight='bold', pad=14)
    ax.grid(True, axis='y', linestyle=':', alpha=0.4)
    out = FIG / 'figure_8_bootstrap_shifts.png'
    plt.savefig(out, bbox_inches='tight'); plt.close()
    print(f"Saved: {out}")

    return summary


# =============================================================================
# Analysis 3 -- VARIANCE DECOMPOSITION
# =============================================================================
def variance_decomposition():
    print("\n" + "="*72)
    print("ANALYSIS 3: VARIANCE DECOMPOSITION (Reviewer point #8)")
    print("="*72)

    log_wue  = np.log(scored['annual_wue_l_per_kwh'].clip(lower=1e-6))
    log_beta = np.log(scored['peaking_factor'].clip(lower=1e-6))
    log_bws  = np.log(scored['bws_raw'].clip(lower=1e-6))
    log_pswi = log_wue + log_beta + log_bws

    var_p = np.var(log_pswi)
    v_w   = np.var(log_wue)
    v_b   = np.var(log_beta)
    v_s   = np.var(log_bws)
    cwb   = np.cov(log_wue,  log_beta)[0,1]
    cws   = np.cov(log_wue,  log_bws )[0,1]
    cbs   = np.cov(log_beta, log_bws )[0,1]
    cov_total = 2*cwb + 2*cws + 2*cbs

    sw = v_w  / var_p
    sb = v_b  / var_p
    ss = v_s  / var_p
    sc = cov_total / var_p

    print(f"Var(log PSWI) = {var_p:.3f}")
    print(f"  log(WUE):       Var = {v_w:.3f}  share = {sw*100:5.1f}%")
    print(f"  log(beta):      Var = {v_b:.3f}  share = {sb*100:5.1f}%")
    print(f"  log(BWS):       Var = {v_s:.3f}  share = {ss*100:5.1f}%")
    print(f"  Covariances:                 share = {sc*100:5.1f}%")
    print(f"  TOTAL share:                       = {(sw+sb+ss+sc)*100:.1f}%")

    pd.DataFrame({
        'component':['log(WUE)','log(beta)','log(BWS)','covariances'],
        'variance':[v_w, v_b, v_s, cov_total],
        'share':[sw, sb, ss, sc],
    }).to_csv(DATA / 'variance_decomposition.csv', index=False)
    print(f"Saved: {DATA / 'variance_decomposition.csv'}")

    # Figure
    fig, ax = plt.subplots(figsize=(8, 5))
    comps = ['log(WUE)\nefficiency', r'log($\beta$)' + '\npeaking', 'log(BWS)\nstress', 'covariance\nterms']
    shares = [sw, sb, ss, sc]
    cols = [COLORS['accent'], COLORS['bad'], COLORS['worst'], COLORS['neutral']]
    bars = ax.bar(comps, [s*100 for s in shares], color=cols, edgecolor='black')
    for bar, s in zip(bars, shares):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                f"{s*100:.1f}%", ha='center', fontsize=11, fontweight='bold')
    ax.set_ylabel('Share of cross-facility Var(log PSWI)  [%]')
    ax.set_title('Variance Decomposition: Where Does PSWI Variation Come From?',
                 fontweight='bold', pad=14)
    ax.grid(True, axis='y', linestyle=':', alpha=0.4)
    ax.set_ylim(min(0, min([s*100 for s in shares])-5), max([s*100 for s in shares])*1.2)
    out = FIG / 'figure_9_variance_decomposition.png'
    plt.savefig(out, bbox_inches='tight'); plt.close()
    print(f"Saved: {out}")

    return sw, sb, ss, sc


# =============================================================================
# Analysis 4 -- UNCERTAINTY-PROPAGATED COUNTERFACTUAL
# =============================================================================
def uncertainty_counterfactual(n_runs=500):
    print("\n" + "="*72)
    print("ANALYSIS 4: PROPER UNCERTAINTY PROPAGATION (Reviewer point #2)")
    print("="*72)
    print(f"WUE  ± {WUE_REL_UNCERTAINTY*100:.0f}% (corporate reporting precision)")
    print(f"BWS  ± {BWS_REL_UNCERTAINTY*100:.0f}% (Aqueduct 4.0 model uncertainty)")
    print(f"beta ± {BETA_REL_UNCERTAINTY*100:.0f}% (Han et al. 2026 observed range)")
    print(f"Running {n_runs} Monte Carlo iterations...")

    rng = np.random.default_rng(42)
    n = len(scored)
    fr = np.linspace(0, 0.50, 60)
    impacts = np.zeros((n_runs, len(fr)))
    wb = scored['annual_wue_l_per_kwh'].values
    bb = scored['peaking_factor'].values
    sb = scored['bws_raw'].values

    for run in range(n_runs):
        wue  = np.maximum(wb*(1+rng.normal(0, WUE_REL_UNCERTAINTY,  n)), 1e-4)
        beta = np.maximum(bb*(1+rng.normal(0, BETA_REL_UNCERTAINTY, n)), 1.0)
        bws  = np.maximum(sb*(1+rng.normal(0, BWS_REL_UNCERTAINTY,  n)), 1e-4)
        pswi = wue * beta * bws
        idx = np.argsort(pswi)
        third = max(1, n//3)
        worst, best = idx[-third:], idx[:third]
        for j, f in enumerate(fr):
            wl = np.ones(n)
            mig = f * n
            ws = pswi[worst] / pswi[worst].sum()
            wl[worst] -= mig * ws
            wl[worst]  = np.maximum(wl[worst], 0)
            bi = 1.0 / pswi[best]
            bsh = bi / bi.sum()
            actual = max(0, n - wl.sum())
            wl[best] += actual * bsh
            impacts[run, j] = (wl * pswi).sum()

    median = np.median(impacts, axis=0)
    base = median[0]
    pmed = 100 * (1 - median/base)
    pl95 = 100 * (1 - np.percentile(impacts, 97.5, axis=0)/base)
    ph95 = 100 * (1 - np.percentile(impacts,  2.5, axis=0)/base)
    pl50 = 100 * (1 - np.percentile(impacts, 75,   axis=0)/base)
    ph50 = 100 * (1 - np.percentile(impacts, 25,   axis=0)/base)

    idx10 = np.argmin(np.abs(fr - 0.10))
    print(f"\nAt 10% reallocation:")
    print(f"  Median:  {pmed[idx10]:.1f}%")
    print(f"  95% CI:  [{pl95[idx10]:.1f}%, {ph95[idx10]:.1f}%]")
    print(f"  50% CI:  [{pl50[idx10]:.1f}%, {ph50[idx10]:.1f}%]")

    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.fill_between(fr*100, pl95, ph95, color=COLORS['accent'], alpha=0.18, label='95% CI')
    ax.fill_between(fr*100, pl50, ph50, color=COLORS['accent'], alpha=0.35, label='Interquartile (50% CI)')
    ax.plot(fr*100, pmed, color=COLORS['accent'], lw=2.5, label='Median')
    for tgt in [10, 20, 30]:
        i = np.argmin(np.abs(fr*100 - tgt))
        ax.scatter([tgt], [pmed[i]], color=COLORS['worst'], s=80,
                   zorder=5, edgecolor='black', linewidth=1)
        ax.annotate(f'{pmed[i]:.0f}%\n95% CI [{pl95[i]:.0f}, {ph95[i]:.0f}]',
                    xy=(tgt, pmed[i]),
                    xytext=(tgt+1.5, pmed[i]-9),
                    fontsize=8, color=COLORS['worst'], fontweight='bold')
    ax.set_xlabel('% of fleet workload reallocated (worst third $\\to$ best third)')
    ax.set_ylabel('Reduction in fleet PSWI impact (%)')
    ax.set_title('Counterfactual with Full Uncertainty Propagation\n'
                 r'(WUE $\pm$15%, BWS $\pm$25%, $\beta$ $\pm$30%)',
                 fontweight='bold', pad=14)
    ax.legend(loc='lower right')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_xlim(0, 50)
    ax.set_ylim(0, max(ph95)*1.05)
    out = FIG / 'figure_10_counterfactual_uncertain.png'
    plt.savefig(out, bbox_inches='tight'); plt.close()
    print(f"Saved: {out}")

    return pmed[idx10], pl95[idx10], ph95[idx10]


# =============================================================================
# Analysis 5 -- SAME-OPERATOR CASE STUDY
# =============================================================================
def same_operator_case_study():
    print("\n" + "="*72)
    print("ANALYSIS 5: SAME-OPERATOR CASE STUDY (Reviewer point #7)")
    print("="*72)

    google = scored[scored['company']=='Google'].copy()

    # Find Google in-company pairs with BIG PSWI ratios
    pairs = []
    for i in range(len(google)):
        for j in range(i+1, len(google)):
            r1, r2 = google.iloc[i], google.iloc[j]
            if abs(r1['annual_wue_l_per_kwh']-r2['annual_wue_l_per_kwh']) < 0.5:
                ratio = max(r1['pswi'], r2['pswi']) / max(min(r1['pswi'], r2['pswi']), 1e-6)
                pairs.append((r1, r2, ratio))
    pairs.sort(key=lambda x: -x[2])

    print(f"\nGoogle in-company pairs with similar WUE, very different impact:")
    if pairs:
        for r1, r2, ratio in pairs[:3]:
            lo, hi = sorted([r1, r2], key=lambda r: r['pswi'])
            print(f"\n  LOWER IMPACT: {lo['facility_name']} ({lo['country']})")
            print(f"     WUE = {lo['annual_wue_l_per_kwh']} L/kWh, BWS = {lo['bws_raw']}, PSWI = {lo['pswi']:.4f}")
            print(f"  HIGHER IMPACT: {hi['facility_name']} ({hi['country']})")
            print(f"     WUE = {hi['annual_wue_l_per_kwh']} L/kWh, BWS = {hi['bws_raw']}, PSWI = {hi['pswi']:.4f}")
            print(f"  PSWI ratio: {ratio:.0f}× (same operator, similar self-reported WUE)")

    return pairs[:3] if pairs else []


# =============================================================================
# Analysis 6 -- SCOPE 2 SENSITIVITY
# =============================================================================
def scope2_sensitivity():
    print("\n" + "="*72)
    print("ANALYSIS 6: SCOPE 2 ROBUSTNESS (Reviewer point #10)")
    print("="*72)

    SCOPE2_AVG = 1.5  # L/kWh, EPRI/NREL US grid average
    print(f"Adding uniform Scope 2 grid water: {SCOPE2_AVG} L/kWh")

    df = scored.copy()
    df['wue_total'] = df['annual_wue_l_per_kwh'] + SCOPE2_AVG
    df['pswi_s2']  = df['wue_total'] * df['peaking_factor'] * df['bws_raw']
    df['rank0']    = df['pswi'].rank(method='dense', ascending=False).astype(int)
    df['rank2']    = df['pswi_s2'].rank(method='dense', ascending=False).astype(int)
    rho, _ = spearmanr(df['rank0'], df['rank2'])
    print(f"Spearman ρ(Scope 1 rank, Scope 1+2 rank) = {rho:.4f}")
    overlap = len(set(df.nsmallest(10,'rank0').index) & set(df.nsmallest(10,'rank2').index))
    print(f"Top-10 worst overlap: {overlap}/10")
    print(f"Mean |rank change|: {(df['rank0']-df['rank2']).abs().mean():.2f} positions")
    return rho, overlap


# =============================================================================
if __name__ == '__main__':
    rho_h, rho_d, half_overlap, dbl_overlap, perturb_rho, perturb_overlap = beta_sensitivity()
    boot_sum = bootstrap_ranks(n_boot=2000)
    sw, sb, ss, sc = variance_decomposition()
    cf_med, cf_lo, cf_hi = uncertainty_counterfactual(n_runs=500)
    case_pairs = same_operator_case_study()
    s2_rho, s2_overlap = scope2_sensitivity()

    print("\n" + "="*72)
    print("REVISION ANALYSES SUMMARY  (use these numbers in the paper)")
    print("="*72)
    print(f"BETA SENSITIVITY (uniform):    rho(β×0.5) = {rho_h:.3f}, rho(β×2.0) = {rho_d:.3f}")
    print(f"BETA SENSITIVITY (per-facility ±50%):  mean ρ = {perturb_rho:.3f}, mean top-10 overlap = {perturb_overlap:.1f}/10")
    print(f"VARIANCE SHARE:                WUE = {sw*100:.1f}%, β = {sb*100:.1f}%, BWS = {ss*100:.1f}%, cov = {sc*100:.1f}%")
    print(f"COUNTERFACTUAL (with uncertainty): median = {cf_med:.1f}%, 95% CI [{cf_lo:.1f}, {cf_hi:.1f}]")
    print(f"SCOPE 2 ROBUSTNESS:            ρ = {s2_rho:.3f}, top-10 overlap = {s2_overlap}/10")
