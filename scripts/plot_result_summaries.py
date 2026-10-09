"""Render closed-study summaries from committed JSON only; no fitting or simulation.

Run: python -m scripts.plot_result_summaries
Figures use the shared style in scripts/figstyle.py; the CSV views and tables keep their values.
"""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
import numpy as np

from scripts import figstyle

plt = figstyle.setup(style=False)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/sim/summary'
INPUTS = [f'data/sim/phaseD/{name}.json' for name in
          ('matched_clock_audit', 'study3_results', 'study4_results')]
C = figstyle.COLOR


def save(fig, name):
    figstyle.save(fig, OUT / name, formats=('png', 'svg'))
    plt.close(fig)


def header(fig, ax, title, status, pad=8):
    """Figure title and evidence line, left-aligned with the first panel, ``pad`` points above it."""
    box = ax.get_position()
    pt = 1 / 72 / fig.get_figheight()
    fig.text(box.x0, box.y1 + pad * pt, status, ha='left', va='bottom', fontsize=figstyle.SIZE['note'],
             color=C['muted'])
    fig.text(box.x0, box.y1 + (pad + 12) * pt, title, ha='left', va='bottom', fontsize=figstyle.SIZE['label'])


def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def replace_table(path, table):
    start, end = '<!-- policy-summary:start -->', '<!-- policy-summary:end -->'
    text = path.read_text()
    before, tail = text.split(start)
    _, after = tail.split(end)
    path.write_text(before + start + '\n' + table + '\n' + end + after)


def policies(audit, study):
    # Keep the audited policies together, and retain original context policies.
    rows = []
    for key, label in [('fixed', 'Initial calibration only'),
                       ('clock_2700', f"Clock: {audit['period_star_reported']:,.0f} cycles (train-selected)"),
                       ('clock_2400', f"Clock: {audit['clock_periods_matching_trigger_schedule_on_all_actuators'][0]:,.0f} cycles (matched cost)"),
                       ('trigger', f"P-V trigger: τ = {audit['tau_star']:.2f}"),
                       ('always', 'Calibration at every stage')]:
        if key in audit['heldout']:
            val = audit['heldout'][key]
            error, count = val['error_mm'], val['recalibrations']
        else:
            val = study['policies_on_heldout'][key]
            error, count = val['mean_pose_rmse_mm'], val['recal_per_actuator']
        rows.append(dict(policy=key, label=label, mean_pose_rmse_mm=error,
                         recalibrations_per_actuator=count))
    return rows


def policy_figure(rows, audit, study):
    styles = [(C['fixed'], 'o'), (C['clock'], '^'), (C['clock'], 's'), (C['pv'], 'D'), (C['always'], 'X')]
    fig, axes = plt.subplots(1, 2, figsize=(figstyle.FULL, 2.3), sharey=True,
                             gridspec_kw={'width_ratios': [1.5, 1], 'wspace': 0.08})
    fig.subplots_adjust(left=.30, right=.97, top=.86, bottom=.2)
    for ax, field, label, xmax in zip(axes, ['mean_pose_rmse_mm', 'recalibrations_per_actuator'],
                                      ['Mean pose RMSE (mm)', 'Calibrations per actuator'], [.50, 6.1]):
        for y, (row, (color, marker)) in enumerate(zip(rows, styles)):
            value = row[field]
            ax.plot(value, y, marker=marker, color=color, markersize=6, linestyle='none')
            ax.annotate(f'{value:.3f}' if field.endswith('_mm') else f'{value:.1f}', (value, y), xytext=(7, 0),
                        textcoords='offset points', va='center', fontsize=figstyle.SIZE['note'],
                        color=figstyle.ink(color))
        ax.set_xlim(0, xmax)
        ax.set_ylim(len(rows) - .5, -.9)
        ax.set_xlabel(label)
        ax.grid(axis='x')
        ax.set_axisbelow(True)
        ax.tick_params(axis='y', length=0)
    axes[1].spines['left'].set_visible(False)
    axes[0].set_yticks(range(len(rows)), [r['label'] for r in rows])
    for tick, (color, _) in zip(axes[0].get_yticklabels(), styles):
        tick.set_color(figstyle.ink(color) if color != C['fixed'] else '#222222')
        tick.set_fontsize(figstyle.SIZE['label'])
    axes[0].axvline(audit['budget_mm'], color=C['ref'], ls='--', lw=.8)
    axes[0].text(audit['budget_mm'] + .006, -.62, f"error budget {audit['budget_mm']:.3f} mm", ha='left',
                 va='center', fontsize=figstyle.SIZE['note'], color=C['ref'])
    header(fig, axes[0], 'At matched cost the cycle-count clock ties the P-V trigger',
           f"Simulation · {len(study['test_actuators'])} held-out actuators · point summaries, no uncertainty bars · "
           "left is better in both panels")
    figstyle.footnote(fig, 'Counts include the initial calibration. Error averages life stages, then actuators. '
                      'Sources: matched_clock_audit.json and study3_results.json; no physical measurements.')
    save(fig, 'policy_comparison')


def lead_figure(study):
    rows = study['lead_time_heldout']['per_actuator']
    n_late = sum(r['lead_life'] < 0 for r in rows)
    fig, (timing, lead) = plt.subplots(1, 2, figsize=(figstyle.FULL, 2.4), sharey=True,
                                       gridspec_kw={'wspace': 0.12})
    fig.subplots_adjust(left=.12, right=.97, top=.76, bottom=.2)
    for y, row in enumerate(rows):
        a, b = row['budget_violation_life'], row['trigger_life']
        timing.plot([a, b], [y, y], color='#BDBDBD', lw=1.2, zorder=1)
        timing.plot(a, y, '^', color=C['ref'], ms=5.5, zorder=2)
        timing.plot(b, y, 'D', color=C['pv'], ms=5, zorder=2)
        lead.plot([0, row['lead_life']], [y, y], color=C['pv'], lw=1.2)
        lead.plot(row['lead_life'], y, 'D', color=C['pv'], ms=5)
        lead.text(row['lead_life'] - .012, y, f"{row['lead_life']:.3f}".replace('-', '\u2212'), ha='right', va='center',
                  fontsize=figstyle.SIZE['note'], color=figstyle.ink(C['pv']))
    first = rows[0]
    timing.annotate('budget crossed', (first['budget_violation_life'], 0), xytext=(-4, 7), textcoords='offset points',
                    ha='right', va='bottom', fontsize=figstyle.SIZE['note'], color=C['ref'])
    timing.annotate('trigger fires', (first['trigger_life'], 0), xytext=(4, 7), textcoords='offset points',
                    ha='left', va='bottom', fontsize=figstyle.SIZE['note'], color=figstyle.ink(C['pv']))
    timing.set_xlim(0, 1)
    timing.set_xlabel('Normalized life (fraction)')
    timing.set_yticks(range(len(rows)), [f"Actuator {r['actuator_id']}" for r in rows])
    timing.set_title('Life at the budget crossing and at the trigger')
    lead.set_xlim(-.36, .05)
    lead.axvline(0, color=C['ref'], ls='--', lw=.8)
    lead.set_title('Lead: below zero means a late trigger')
    lead.set_xlabel('Budget crossing − trigger (life fraction)')
    lead.spines['left'].set_visible(False)
    for ax in (timing, lead):
        ax.set_ylim(len(rows) - .5, -.9)
        ax.grid(axis='x')
        ax.set_axisbelow(True)
        ax.tick_params(axis='y', length=0)
    figstyle.panel_letter(timing, 'a', dx=-58)
    figstyle.panel_letter(lead, 'b', dx=-16)
    late = 'every held-out actuator' if n_late == len(rows) else f'{n_late} of {len(rows)} held-out actuators'
    header(fig, timing, f'The deployed P-V trigger fires after the error budget is crossed on {late}',
           f"Simulation · τ = {study['tau_selected']:.2f} · {len(rows)} held-out actuators; "
           f"{study['lead_time_heldout']['n_excluded']} excluded", pad=22)
    figstyle.footnote(fig, 'Crossings are interpolated estimates from the saved life-stage analysis. Connectors join '
                      'paired values and are not confidence intervals. Source: study3_results.json.')
    save(fig, 'trigger_timing')
    write_csv('trigger_timing.csv', rows)


def coupling_figure(study):
    fig, ax = plt.subplots(figsize=(figstyle.WIDE, 2.7))
    fig.subplots_adjust(left=.13, right=.80, top=.80, bottom=.2)
    x = study['sweep_multiplier']
    for threshold in study['thresholds']:
        ax.axhline(threshold * 100, color=C['ref'], ls=':', lw=.8)
        ax.text(x[-1], threshold * 100 + .8, f'{threshold:.0%} reference', ha='right', va='bottom',
                fontsize=figstyle.SIZE['note'], color=C['ref'])
    curves = [('R_s', 'supply resistance', C['supply'], 'o', '-'),
              ('C_m', 'manifold compliance', C['compliance'], 's', '--')]
    for key, label, color, marker, ls in curves:
        y = np.asarray(study['coupling_vs_multiplier'][key]) * 100
        ax.plot(x, y, color=color, marker=marker, markevery=3, ms=3.5, ls=ls)
        figstyle.end_label(ax, x[-1], y[-1], label, color)
    ax.plot(1, study['default_coupling'] * 100, 'D', color='#222222', ms=5, zorder=5)
    ax.annotate('default network', (1, study['default_coupling'] * 100), xytext=(-6, 26), textcoords='offset points',
                ha='right', va='bottom', fontsize=figstyle.SIZE['note'], color='#222222',
                arrowprops=dict(arrowstyle='-', lw=.6, color='#222222', shrinkB=3))
    ax.set_xscale('log', base=2)
    ax.set_xlim(min(x) / 1.08, max(x) * 1.08)
    ticks = [.25, .5, 1, 2, 4, 8, 16, 32]
    ax.set_xticks(ticks, [f'{v:g}' for v in ticks])
    ax.minorticks_off()
    ax.set_ylim(0, 45)
    ax.set_xlabel('Varied parameter / default (ratio, log scale)')
    ax.set_ylabel('Neighbour / driven pressure\namplitude (%)')
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    header(fig, ax, 'Cross-talk depends on the assumed supply network',
           f"Simulation · one parameter varied at a time · probe {study['probe']['freq_hz']:g} Hz")
    figstyle.footnote(fig, 'Saved deterministic sweep; reference levels are not confidence limits. Other parameters '
                      'stay fixed; no physical gripper tested. Source: study4_results.json.')
    save(fig, 'cross_talk')
    write_csv('cross_talk.csv', [dict(multiplier=m, R_s_coupling_ratio=a, C_m_coupling_ratio=b)
              for m, a, b in zip(x, study['coupling_vs_multiplier']['R_s'], study['coupling_vs_multiplier']['C_m'])])


def main():
    figstyle.apply()
    OUT.mkdir(parents=True,exist_ok=True)
    audit, study3, study4 = [json.loads((ROOT/p).read_text()) for p in INPUTS]
    rows=policies(audit,study3)
    policy_figure(rows,audit,study3)
    lead_figure(study3)
    coupling_figure(study4)
    write_csv('policy_comparison.csv',rows)
    table='| Policy | Mean pose error, RMSE (mm) | Calibrations per actuator |\n|:---|---:|---:|\n'
    table+='\n'.join(f"| {r['label']} | {r['mean_pose_rmse_mm']:.3f} | {r['recalibrations_per_actuator']:.1f} |" for r in rows)
    for path in ('README.md','docs/results.md'):
        replace_table(ROOT/path,table)
    provenance={'evidence':'Saved simulation outputs only; no new evaluation or physical data',
                'inputs_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS},
                'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'matplotlib_version':matplotlib.__version__,
                'visual_reference':{'repository':'500ft/sensor-enclosure-thermal-design',
                                    'commit':'bad572fc0902437445a5446bb5bc43098cc6211f'},
                'csv_note':'Generated views; original JSON remains the numeric source of truth.'}
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(OUT)


if __name__=='__main__':
    main()
