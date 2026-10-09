"""Render closed-study summaries from committed JSON only; no fitting or simulation.

Run: python -m scripts.plot_result_summaries
Original manuscript figures and their generators are intentionally untouched.
"""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/sim/summary'
INPUTS = [f'data/sim/phaseD/{name}.json' for name in
          ('matched_clock_audit', 'study3_results', 'study4_results')]
BLUE, RED, GREEN, GRAY = '#2980b9', '#c0392b', '#27ae60', '#66717e'


def save(fig, name):
    fig.savefig(OUT / f'{name}.png', dpi=180, facecolor='white')
    fig.savefig(OUT / f'{name}.svg', metadata={'Date': None}, facecolor='white')
    svg = OUT / f'{name}.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(fig)


def axes_style(ax, grid='x'):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis=grid, alpha=.18, linewidth=.7)
    ax.set_axisbelow(True)


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
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharey=True,
                             gridspec_kw={'width_ratios': [1.5, 1]})
    fig.subplots_adjust(left=.32, right=.96, top=.77, bottom=.28, wspace=.17)
    fig.suptitle('Matched-cost clock and P-V trigger tie', fontsize=15, y=.97)
    fig.text(.5, .875, f"SIMULATION • {len(study['test_actuators'])} held-out actuators • point summaries, no uncertainty bars", ha='center', fontsize=11)
    styles = [(GRAY, 'o'), (BLUE, '^'), (BLUE, 's'), (RED, 'D'), (GRAY, 'x')]
    for ax, field, title, xmax in zip(axes, ['mean_pose_rmse_mm','recalibrations_per_actuator'],
                                     ['Mean pose RMSE [mm]', 'Calibrations / actuator'], [.50, 6.1]):
        for y, (row, (color, marker)) in enumerate(zip(rows, styles)):
            value = row[field]
            ax.plot(value, y, marker=marker, color=color, markersize=8, linestyle='none')
            ax.text(value+xmax*.028, y, f'{value:.3f}' if field.endswith('_mm') else f'{value:.1f}', va='center', fontsize=11)
        ax.set_xlim(0, xmax)
        ax.set_ylim(len(rows)-.5, -.8)
        ax.set_xlabel(title)
        axes_style(ax)
    axes[0].set_yticks(range(len(rows)), [r['label'] for r in rows])
    axes[0].axvline(audit['budget_mm'], color='#222222', ls='--', lw=1)
    axes[0].text(audit['budget_mm'], -.55, f"Budget {audit['budget_mm']:.3f}", ha='center', fontsize=10)
    fig.text(.5, .075, 'Counts include the initial calibration. Error averages life stages, then actuators.\nSources: matched_clock_audit.json and study3_results.json; no physical measurements.', ha='center', fontsize=10)
    save(fig, 'policy_comparison')


def lead_figure(study):
    rows = study['lead_time_heldout']['per_actuator']
    fig, (timing, lead) = plt.subplots(1, 2, figsize=(10.5, 5), sharey=True)
    fig.subplots_adjust(left=.12, right=.96, top=.76, bottom=.28, wspace=.25)
    fig.suptitle('The deployed trigger follows the budget crossing', fontsize=15, y=.97)
    fig.text(.5, .885, f"SIMULATION • τ = {study['tau_selected']:.2f} • {len(rows)} held-out actuators; {study['lead_time_heldout']['n_excluded']} excluded", ha='center', fontsize=11)
    for y, row in enumerate(rows):
        a,b = row['budget_violation_life'],row['trigger_life']
        timing.plot([a,b],[y,y],color='#b9bdc4',lw=1.5)
        timing.plot(a,y,'^',color=GRAY,ms=7,label='Budget crossing' if y==0 else None)
        timing.plot(b,y,'D',color=RED,ms=7,label='P-V trigger' if y==0 else None)
        lead.plot([0,row['lead_life']],[y,y],color=RED,lw=1.5)
        lead.plot(row['lead_life'],y,'D',color=RED,ms=6)
        lead.text(row['lead_life']-.009,y,f"{row['lead_life']:.3f}",ha='right',va='center',fontsize=10)
    timing.set_xlim(0,1)
    timing.set_xlabel('Normalized life [fraction]')
    timing.set_yticks(range(len(rows)), [f"Actuator {r['actuator_id']}" for r in rows])
    timing.legend(loc='lower left',bbox_to_anchor=(0,1.02),ncol=2,fontsize=10,frameon=False)
    lead.set_xlim(-.36,.05)
    lead.axvline(0,color='#222222',ls='--',lw=1)
    lead.set_title('Negative lead = late trigger',fontsize=12)
    lead.set_xlabel('Budget crossing − trigger [life fraction]')
    for ax in (timing,lead):
        ax.set_ylim(len(rows)-.5,-.5)
        axes_style(ax)
    fig.text(.5,.075,'Crossings are interpolated estimates from the saved life-stage analysis.\nSource: study3_results.json; connectors are paired values, not confidence intervals.',ha='center',fontsize=10)
    save(fig, 'trigger_timing')
    write_csv('trigger_timing.csv', rows)


def coupling_figure(study):
    fig, ax = plt.subplots(figsize=(9.5,5.1))
    fig.subplots_adjust(left=.11,right=.96,top=.76,bottom=.28)
    fig.suptitle('Cross-talk depends on the assumed supply network',fontsize=15,y=.97)
    fig.text(.5,.875,f"SIMULATION • one parameter varied at a time • probe {study['probe']['freq_hz']:g} Hz",ha='center',fontsize=11)
    x = study['sweep_multiplier']
    for key, label, color, marker, ls in [('R_s','Supply resistance',BLUE,'o','-'),
                                         ('C_m','Manifold compliance',GREEN,'s','--')]:
        ax.plot(x,np.asarray(study['coupling_vs_multiplier'][key])*100,
                color=color,marker=marker,markevery=3,ms=5,lw=2,ls=ls,label=label)
    for threshold in study['thresholds']:
        ax.axhline(threshold*100,color=GRAY,ls=':',lw=1)
        ax.text(x[-1],threshold*100+.9,f'{threshold:.0%} reference',ha='right',fontsize=10,color=GRAY)
    ax.plot(1,study['default_coupling']*100,'D',color='#222222',ms=7,label='Default network')
    ax.axvline(1,color='#222222',ls=':',lw=.7)
    ax.set_xscale('log',base=2)
    ax.set_xlim(min(x)/1.08,max(x)*1.08)
    ticks=[.25,.5,1,2,4,8,16,32]
    ax.set_xticks(ticks,[f'{v:g}' for v in ticks])
    ax.set_ylim(0,45)
    ax.set_xlabel('Varied parameter / default [ratio, logarithmic scale]')
    ax.set_ylabel('Neighbor / driven pressure amplitude [%]')
    ax.legend(frameon=False,loc='upper left',fontsize=11)
    axes_style(ax,'y')
    fig.text(.5,.065,'Saved deterministic sweep; reference levels are not confidence limits.\nSource: study4_results.json. Other parameters stay fixed; no physical gripper tested.',ha='center',fontsize=10)
    save(fig,'cross_talk')
    write_csv('cross_talk.csv',[dict(multiplier=m,R_s_coupling_ratio=a,C_m_coupling_ratio=b)
              for m,a,b in zip(x,study['coupling_vs_multiplier']['R_s'],study['coupling_vs_multiplier']['C_m'])])


def main():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelsize':11,
                         'axes.titlesize':12,'svg.fonttype':'none','svg.hashsalt':'soft-summary',
                         'figure.facecolor':'white','axes.facecolor':'white'})
    OUT.mkdir(parents=True,exist_ok=True)
    audit, study3, study4 = [json.loads((ROOT/p).read_text()) for p in INPUTS]
    rows=policies(audit,study3)
    policy_figure(rows,audit,study3)
    lead_figure(study3)
    coupling_figure(study4)
    write_csv('policy_comparison.csv',rows)
    table='| Policy | Mean pose RMSE [mm] | Calibrations / actuator |\n|:---|---:|---:|\n'
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
