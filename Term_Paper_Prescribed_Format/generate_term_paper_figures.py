#!/usr/bin/env python3
"""
Generate figures for the Prescribed University Format Term Paper:
Figure 1: Benchmark Feature Dimensionality (vertical bar chart)
Figure 2: PRISMA Methodology Flowchart (structured flowchart)
Figure 3: Literature Review Observations (horizontal bar chart)
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUT_DIR = Path("/Users/ashish/Desktop/Side Project/Soft Computing Term Paper/Term_Paper_Prescribed_Format/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "figure.dpi": 300,
    "savefig.dpi": 300,
})

def make_fig1():
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    datasets = ["Wine", "Breast\nCancer", "Ionosphere", "Spambase", "Sonar", "Digits", "Semeion", "Madelon", "Arcene", "RNA-seq"]
    dims = [13, 30, 34, 57, 60, 64, 256, 500, 10000, 20531]
    
    # Use grayscale / dark slate bars like the sample PDF
    bars = ax.bar(np.arange(len(datasets)), dims, color="#718096", edgecolor="#2D3748", width=0.55, lw=0.8)
    
    ax.set_yscale("log")
    ax.set_ylim(5, 60000)
    ax.set_ylabel("Number of Features (d, log scale)", fontsize=10.5, fontweight="bold")
    ax.set_xlabel("Benchmark Datasets", fontsize=10.5, fontweight="bold")
    ax.set_xticks(np.arange(len(datasets)))
    ax.set_xticklabels(datasets, fontsize=8.8)
    ax.tick_params(labelsize=9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    
    for bar, val in zip(bars, dims):
        label = f"{val:,}" if val >= 1000 else str(val)
        ax.text(bar.get_x() + bar.get_width()/2, val * 1.25, label,
                ha="center", va="bottom", fontsize=8.2, fontweight="bold", color="#1A202C")
        
    plt.tight_layout()
    out = OUT_DIR / "fig1_benchmark_dimensions.png"
    plt.savefig(out)
    plt.close()
    print("Saved:", out)

def make_fig2():
    # Figure 2: PRISMA Flow Diagram styled after sample PDF Fig 2
    fig, ax = plt.subplots(figsize=(6.8, 6.2))
    ax.axis("off")
    
    steps = [
        ("Define research objectives: Analyze scalability, memory limits, and guidance efficacy in GA feature selection", 0.90),
        ("Develop review protocol: Establish eligibility criteria and outline electronic database sources", 0.79),
        ("Employ search strategy: Keywords ('genetic algorithm', 'feature selection', 'correlation guidance', 'symmetric uncertainty')", 0.68),
        ("Initial search identified 100 papers across IEEE Xplore, ScienceDirect, Springer, and Scopus", 0.57),
        ("Remove duplicates and non-English entries: 80 records remain", 0.46),
        ("Screen titles and abstracts against inclusion criteria: Exclude 30 papers", 0.35),
        ("Full-text screening of 50 papers: Exclude 30 studies lacking rigorous validation or complete metrics", 0.24),
        ("20 papers selected for qualitative synthesis, systematic taxonomy, and empirical benchmarking", 0.13),
        ("Data extraction: Extract author, year, domain, GA variant, classifier, validation protocol, and performance metrics", 0.02),
    ]
    
    box_w = 0.88
    box_h = 0.075
    center_x = 0.5
    
    for i, (text, y_pos) in enumerate(steps):
        # Lavender box like sample PDF
        rect = patches.FancyBboxPatch(
            (center_x - box_w/2, y_pos - box_h/2), box_w, box_h,
            boxstyle="round,pad=0.015",
            facecolor="#E9D8FD", edgecolor="#9F7AEA", lw=1.2, zorder=2
        )
        ax.add_patch(rect)
        ax.text(center_x, y_pos, text, ha="center", va="center", fontsize=8.2, color="#322659", zorder=3, wrap=True)
        
        # Downward arrow to next step
        if i < len(steps) - 1:
            next_y = steps[i+1][1]
            ax.annotate("", xy=(center_x, next_y + box_h/2), xytext=(center_x, y_pos - box_h/2),
                        arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.2), zorder=4)
            
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.04, 0.96)
    plt.tight_layout()
    out = OUT_DIR / "fig2_prisma_flow.png"
    plt.savefig(out)
    plt.close()
    print("Saved:", out)

def make_fig3():
    # Figure 3: Observations from review based on number of studies (horizontal bar chart)
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    
    themes = [
        "High Predictive Accuracy of GA Wrappers",
        "Diverse Filter-Wrapper Hybrid Strategies",
        "Mutual Information and Symmetric Uncertainty Guidance",
        "Multi-Objective Pareto Trade-Off Optimization",
        "Dynamic Programming and Memoization Approaches",
        "Synthetic and Domain-Specific Benchmark Testing",
        "Computational Runtime Dominated by Classifier Wrappers",
        "Scalability and Memory Bottleneck on Wide Data (d > 1,000)",
        "Absence of Strict Nested Cross-Validation Protocol",
        "Empirical Equivalence Between Dense and On-Demand Caching"
    ]
    # Reverse so top theme appears at top
    themes = themes[::-1]
    counts = [10, 9, 8, 7, 6, 5, 4, 3, 2, 2][::-1]
    
    y_pos = np.arange(len(themes))
    bars = ax.barh(y_pos, counts, height=0.6, color="#63B3ED", edgecolor="#2B6CB0", lw=0.8)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(themes, fontsize=8.6)
    ax.set_xlabel("Number of Studies", fontsize=9.5, fontweight="bold")
    ax.set_xlim(0, 11)
    ax.tick_params(labelsize=8.8)
    ax.grid(True, axis="x", linestyle=":", alpha=0.5)
    
    for bar, val in zip(bars, counts):
        ax.text(val + 0.15, bar.get_y() + bar.get_height()/2, str(val),
                ha="left", va="center", fontsize=8.5, fontweight="bold", color="#1A365D")
        
    plt.tight_layout()
    out = OUT_DIR / "fig3_literature_observations.png"
    plt.savefig(out)
    plt.close()
    print("Saved:", out)

if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    print("All term paper figures generated successfully!")
