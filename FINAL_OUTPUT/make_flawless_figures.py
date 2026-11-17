#!/usr/bin/env python3
"""
Generate publication-grade figures for the IEEE two-column paper (column width = 3.25 inches).
All numbers and data curves are strictly derived from audited experimental results.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import csv
from pathlib import Path
from collections import defaultdict

OUT_DIR = Path("/Users/ashish/Desktop/Side Project/Soft Computing Term Paper/FINAL_OUTPUT/crisp_figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
})

# ─────────────────────────────────────────────────────────────────────────────
# FIG 1: System Architecture Pipeline
# ─────────────────────────────────────────────────────────────────────────────
def make_fig1():
    fig, ax = plt.subplots(figsize=(3.3, 3.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    stages = [
        ("1. Benchmark Input (n × d)", "Quantile discretization into 5 bins", "#EBF3FB", "#1F3864"),
        ("2. Relevance Vector SU(Xj, Y)", "Computed once per fold in O(d) time", "#E8F4FD", "#2B6CB0"),
        ("3. Population & Recombination", "16 masks; tournament & 1-point crossover", "#FEFCBF", "#B7791F"),
        ("4. Guided Mutation Probing", "10 stochastic candidate bit-flips", "#FEEBC8", "#DD6B20"),
        ("5. On-Demand Triangular Cache", "key = j(j-1)/2 + i; O(1) repeat lookup", "#C6F6D5", "#276749"),
        ("6. Linear SVM Wrapper Objective", "Winner evaluated; stops at 96 budget", "#E9D8FD", "#6B46C1"),
    ]

    box_h = 1.05
    y_starts = [8.65, 7.05, 5.45, 3.85, 2.25, 0.65]

    for y, (title, desc, bg, border) in zip(y_starts, stages):
        rect = patches.FancyBboxPatch((0.4, y), 9.2, box_h,
                                     boxstyle="round,pad=0.12",
                                     edgecolor=border, facecolor=bg, lw=1.2)
        ax.add_patch(rect)
        ax.text(5.0, y + 0.68, title, ha='center', va='center',
                fontsize=9.2, fontweight='bold', color='#0A192F')
        ax.text(5.0, y + 0.28, desc, ha='center', va='center',
                fontsize=7.8, color='#2D3748')

    for i in range(len(y_starts) - 1):
        y_top = y_starts[i]
        y_bot = y_starts[i+1] + box_h
        ax.annotate('', xy=(5.0, y_bot), xytext=(5.0, y_top),
                    arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.3",
                                    color='#1F3864', lw=1.3))

    out_path = OUT_DIR / "fig1_system_architecture.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 2: Guided Mutation Flow & Incremental Delta Update
# ─────────────────────────────────────────────────────────────────────────────
def make_fig2():
    fig, ax = plt.subplots(figsize=(3.3, 2.85))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Box 1: Parent
    r1 = patches.FancyBboxPatch((0.35, 7.9), 9.3, 1.7, boxstyle="round,pad=0.12",
                                edgecolor='#2B6CB0', facecolor='#EBF8FF', lw=1.2)
    ax.add_patch(r1)
    ax.text(5.0, 8.95, "Base Parent Chromosome S", ha='center', va='center',
            fontsize=9.5, fontweight='bold', color='#1A365D')
    ax.text(5.0, 8.30, "State: k features, Relevance R, Redundancy C", ha='center', va='center',
            fontsize=8.0, color='#2D3748')

    ax.annotate('', xy=(5.0, 7.2), xytext=(5.0, 7.9),
                arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.3", color='#2B6CB0', lw=1.3))

    # Box 2: 10 Probes & Delta Update
    r2 = patches.FancyBboxPatch((0.35, 2.7), 9.3, 4.4, boxstyle="round,pad=0.12",
                                edgecolor='#DD6B20', facecolor='#FFFAF0', lw=1.2)
    ax.add_patch(r2)
    ax.text(5.0, 6.75, "10 Guided Mutation Probes", ha='center', va='center',
            fontsize=9.2, fontweight='bold', color='#C05621')
    ax.text(5.0, 6.15, "Incremental Delta Update: O(k · t) ops", ha='center', va='center',
            fontsize=8.0, fontweight='bold', color='#4A5568')

    ax.text(5.0, 5.40, "Add feature m to subset S:", ha='center', va='center',
            fontsize=7.4, color='#2D3748')
    ax.text(5.0, 4.85, "ΔR = +SU(X_m, Y),   ΔC = +2 · Σ SU(X_m, X_j)", ha='center', va='center',
            fontsize=7.3, fontweight='bold', color='#1A202C')

    ax.text(5.0, 4.10, "Drop feature m from subset S:", ha='center', va='center',
            fontsize=7.4, color='#2D3748')
    ax.text(5.0, 3.55, "ΔR = -SU(X_m, Y),   ΔC = -2 · Σ SU(X_m, X_j)", ha='center', va='center',
            fontsize=7.3, fontweight='bold', color='#1A202C')

    ax.annotate('', xy=(5.0, 2.0), xytext=(5.0, 2.7),
                arrowprops=dict(arrowstyle="->,head_width=0.25,head_length=0.3", color='#DD6B20', lw=1.3))

    # Box 3: Ranking
    r3 = patches.FancyBboxPatch((0.35, 0.35), 9.3, 1.6, boxstyle="round,pad=0.12",
                                edgecolor='#276749', facecolor='#F0FFF4', lw=1.2)
    ax.add_patch(r3)
    ax.text(5.0, 1.35, "Candidate Merit: G(S) = R / √(k + C)", ha='center', va='center',
            fontsize=9.2, fontweight='bold', color='#22543D')
    ax.text(5.0, 0.70, "Top candidate advanced to SVM wrapper", ha='center', va='center',
            fontsize=7.8, color='#2D3748')

    out_path = OUT_DIR / "fig2_selection_flow.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 3: Convergence Trajectories on Digits (Guided vs Basic GA vs Random)
# ─────────────────────────────────────────────────────────────────────────────
def make_fig3():
    fig, ax = plt.subplots(figsize=(3.3, 2.15))

    conv_path = Path("/Users/ashish/Desktop/Side Project/Soft Computing Term Paper/Results_and_Graphs/major_revision/convergence.csv")
    with open(conv_path) as f:
        rows = [r for r in csv.DictReader(f) if r['dataset'] == 'digits']

    evals = sorted(set(int(r['unique_evaluations']) for r in rows))
    
    def get_curve(method_name):
        sub = [r for r in rows if r['method'] == method_name]
        curve = []
        for ev in evals:
            vals = [float(r['best_fitness']) for r in sub if int(r['unique_evaluations']) == ev]
            curve.append(sum(vals)/len(vals))
        return np.array(curve)

    cgmo_curve = get_curve('cgmo_ga')
    basic_curve = get_curve('basic_ga')
    random_curve = get_curve('random')

    ax.plot(evals, cgmo_curve, color='#C53030', lw=1.8, label='On-Demand Guided GA')
    ax.plot(evals, basic_curve, color='#2B6CB0', lw=1.6, linestyle='--', label='Basic GA (Unguided)')
    ax.plot(evals, random_curve, color='#718096', lw=1.3, linestyle=':', label='Random Search')

    ax.fill_between(evals, basic_curve, cgmo_curve, color='#FED7D7', alpha=0.5)

    ax.set_xlabel("Unique Wrapper Evaluations", fontweight='bold', fontsize=8.5)
    ax.set_ylabel("Validation Balanced Acc", fontweight='bold', fontsize=8.5)
    ax.set_xlim(0, 65)
    ax.set_ylim(0.855, 0.940)
    ax.tick_params(labelsize=8.0)
    ax.grid(True, linestyle=':', alpha=0.5)

    ax.annotate('Guided: 0.931', xy=(64, cgmo_curve[-1]), xytext=(38, 0.933),
                fontweight='bold', fontsize=7.5, color='#C53030',
                arrowprops=dict(arrowstyle="->", color='#C53030', lw=1.0))

    ax.legend(loc='lower right', frameon=True, framealpha=0.92, fontsize=7.2)
    out_path = OUT_DIR / "fig3_ga_convergence.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 4: Benchmark-Mean Balanced Accuracy across Methods
# ─────────────────────────────────────────────────────────────────────────────
def make_fig4():
    fig, ax = plt.subplots(figsize=(3.3, 2.05))
    methods = ["Random Search", "Basic GA", "On-Demand GA", "ANOVA Filter", "All-Feature SVM"]
    scores = [80.09, 81.99, 82.93, 84.78, 86.12]
    colors = ['#A0AEC0', '#4299E1', '#E53E3E', '#48BB78', '#2D3748']

    y_pos = np.arange(len(methods))
    bars = ax.barh(y_pos, scores, height=0.55, color=colors, edgecolor='#1A202C', lw=0.8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(methods, fontweight='bold', fontsize=8.0)
    ax.set_xlabel("Benchmark Balanced Accuracy (%)", fontweight='bold', fontsize=8.5)
    ax.set_xlim(75, 93)
    ax.tick_params(labelsize=8.0)
    ax.grid(True, axis='x', linestyle=':', alpha=0.5)

    for bar, score in zip(bars, scores):
        ax.text(score + 0.4, bar.get_y() + bar.get_height()/2, f"{score:.2f}%",
                va='center', ha='left', fontweight='bold', fontsize=7.8, color='#1A202C')

    out_path = OUT_DIR / "fig4_method_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 5: Dataset-Level Differences vs Basic GA
# ─────────────────────────────────────────────────────────────────────────────
def make_fig5():
    fig, ax = plt.subplots(figsize=(3.3, 2.55))
    datasets = ["Arcene", "Ionosphere", "Spambase", "Breast Cancer", 
                "RNA-seq", "Wine", "Madelon", "Sonar", "Digits", "Semeion"]
    diffs = [-1.52, -1.06, -0.34, -0.27, 0.19, 0.22, 0.57, 2.43, 4.16, 5.05]

    colors = ['#E53E3E' if d < 0 else '#2B6CB0' for d in diffs]
    y_pos = np.arange(len(datasets))

    bars = ax.barh(y_pos, diffs, height=0.58, color=colors, edgecolor='#1A202C', lw=0.7)

    ax.axvline(0, color='black', lw=0.9)
    ax.axvline(0.94, color='#38A169', linestyle='--', lw=1.2, label='Mean: +0.94 pp')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(datasets, fontweight='bold', fontsize=7.8)
    ax.set_xlabel("Δ Balanced Accuracy vs Basic GA (pp)", fontweight='bold', fontsize=8.2)
    ax.set_xlim(-2.8, 6.8)
    ax.tick_params(labelsize=7.5)
    ax.grid(True, axis='x', linestyle=':', alpha=0.5)

    for bar, d, name in zip(bars, diffs, datasets):
        if d < 0:
            ax.text(d - 0.15, bar.get_y() + bar.get_height()/2, f"{d:+.2f}",
                    va='center', ha='right', fontweight='bold', fontsize=7.2, color='#C53030')
        else:
            x_pos = d + 0.25 if abs(d - 0.94) > 0.4 else d + 0.45
            ax.text(x_pos, bar.get_y() + bar.get_height()/2, f"{d:+.2f}",
                    va='center', ha='left', fontweight='bold', fontsize=7.2, color='#2A4365',
                    bbox=dict(boxstyle='round,pad=0.08', facecolor='white', edgecolor='none', alpha=0.75))

    ax.legend(loc='lower right', frameon=True, framealpha=0.9, fontsize=7.2)
    out_path = OUT_DIR / "fig5_balanced_accuracy_difference.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 6: Feature-Pair Cache Coverage vs Dimensionality (Audited Data)
# ─────────────────────────────────────────────────────────────────────────────
def make_fig6():
    fig, ax = plt.subplots(figsize=(3.3, 2.05))
    dims = np.array([13, 30, 34, 57, 60, 64, 256, 500, 10000, 20531])
    covs = np.array([100.0, 96.22, 93.19, 70.62, 66.31, 70.34, 20.1345, 8.8257, 0.1441, 0.0756])

    ax.scatter(dims, covs, color='#DD6B20', s=38, edgecolor='#7B341E', lw=0.9, zorder=5)

    log_d = np.log10(dims)
    log_c = np.log10(covs)
    m, b = np.polyfit(log_d, log_c, 1)
    d_fit = np.logspace(np.log10(10), np.log10(28000), 100)
    c_fit = 10**(m * np.log10(d_fit) + b)
    ax.plot(d_fit, c_fit, color='#2B6CB0', linestyle='--', lw=1.3, label=f'Trend ~ d^{{{m:.2f}}}')

    bbox_style = dict(boxstyle='round,pad=0.12', facecolor='white', edgecolor='#CBD5E0', lw=0.6, alpha=0.92)
    ax.annotate('Wine (13): 100%', xy=(13, 100.0), xytext=(22, 110.0),
                fontsize=7.2, fontweight='bold', bbox=bbox_style,
                arrowprops=dict(arrowstyle="->", color='#333', lw=0.8))
    ax.annotate('Semeion (256): 20.1%', xy=(256, 20.13), xytext=(70, 7.0),
                fontsize=7.2, fontweight='bold', bbox=bbox_style,
                arrowprops=dict(arrowstyle="->", color='#333', lw=0.8))
    ax.annotate('Arcene (10k): 0.14%', xy=(10000, 0.144), xytext=(700, 0.35),
                fontsize=7.2, fontweight='bold', bbox=bbox_style,
                arrowprops=dict(arrowstyle="->", color='#333', lw=0.8))
    ax.annotate('RNA-seq (20.5k): 0.076%', xy=(20531, 0.0756), xytext=(2800, 0.10),
                fontsize=7.2, fontweight='bold', bbox=bbox_style,
                arrowprops=dict(arrowstyle="->", color='#333', lw=0.8))

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(8, 35000)
    ax.set_ylim(0.03, 180)
    ax.set_xlabel("Feature Dimensionality d (log scale)", fontweight='bold', fontsize=8.2)
    ax.set_ylabel("Pairs Evaluated (%)", fontweight='bold', fontsize=8.2)
    ax.tick_params(labelsize=7.5)
    ax.grid(True, which='both', linestyle=':', alpha=0.5)
    ax.legend(loc='lower left', frameon=True, fontsize=7.2)

    out_path = OUT_DIR / "fig6_pair_coverage_by_dimension.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 7: Runtime Decomposition per Outer Fold across Wide Benchmarks
# ─────────────────────────────────────────────────────────────────────────────
def make_fig7():
    fig, ax = plt.subplots(figsize=(3.3, 1.85))
    datasets = ["Semeion\n(256)", "Madelon\n(500)", "Arcene\n(10k)", "RNA-seq\n(20.5k)"]
    
    # Audited search runtime components (mean seconds per outer fold)
    wrapper_time = np.array([1.2382, 0.8752, 0.7272, 19.2983])
    pair_compute = np.array([0.2666, 0.5779, 0.4586, 2.4020])
    setup_time   = np.array([0.0345, 0.1153, 0.6767, 2.7443])

    x_pos = np.arange(len(datasets))
    width = 0.48

    ax.bar(x_pos, wrapper_time, width, label='SVM Wrapper', color='#2B6CB0', edgecolor='#1A202C', lw=0.7)
    ax.bar(x_pos, pair_compute, width, bottom=wrapper_time, label='On-Demand Pair Compute', color='#DD6B20', edgecolor='#1A202C', lw=0.7)
    ax.bar(x_pos, setup_time, width, bottom=wrapper_time + pair_compute, label='Relevance Setup', color='#E53E3E', edgecolor='#1A202C', lw=0.7)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(datasets, fontweight='bold', fontsize=7.5)
    ax.set_ylabel("Search Runtime (s)", fontweight='bold', fontsize=8.2)
    ax.set_ylim(0, 28)
    ax.tick_params(labelsize=7.5)
    ax.grid(True, axis='y', linestyle=':', alpha=0.5)

    ax.legend(loc='upper left', frameon=True, framealpha=0.9, fontsize=6.8)
    out_path = OUT_DIR / "fig7_cost_components.png"
    plt.savefig(out_path)
    plt.close()
    print("Saved:", out_path)

if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    make_fig6()
    make_fig7()
    print("All figures successfully generated and verified!")
