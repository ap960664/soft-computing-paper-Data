# A Reproducible Evaluation of On-Demand Correlation Guidance for Genetic Algorithm Feature Selection

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Format: IEEE Conference](https://img.shields.io/badge/format-IEEE%20Two--Column-red.svg)](https://www.ieee.org/)
[![Reproducibility: 100% Verified](https://img.shields.io/badge/reproducibility-100%25%20audited-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Author:** Ashish Pathak  
**Affiliation:** School of Computer Science and Engineering, Lovely Professional University, Punjab, India  
**Contact:** [ap960664@gmail.com](mailto:ap960664@gmail.com)  
**Repository:** [https://github.com/ap960664/soft-computing-paper-Data](https://github.com/ap960664/soft-computing-paper-Data)

---

## Overview

This repository provides the complete audited experimental codebase, raw metric logs, and figure/table reproduction suite for the paper:

> **"A Reproducible Evaluation of On-Demand Correlation Guidance for Genetic Algorithm Feature Selection"**

### Key Scientific Contributions & Audited Findings

1. **Exact Mathematical Equivalence ($d \le 500$):**
   * Evaluated across 72 matched outer-fold cross-validation searches on eight public benchmarks.
   * On-demand triangular key caching and incremental delta arithmetic produce **identical binary feature masks (100% agreement)**, **identical classifier predictions**, and **identical generation-by-generation fitness traces** ($\max |\Delta| = 0.0$).
2. **Extreme Cache Sparsity on Wide-Format Data ($d \ge 10,000$):**
   * On Arcene ($d = 10,000$) and RNA-seq ($d = 20,531$), on-demand search accessed only **0.144%** and **0.076%** of candidate pairs, respectively.
   * Eliminates eager allocation of an explicit $d(d - 1)/2$ matrix ($\approx 1.57\text{ GiB}$ / $1.69\text{ GB}$ of raw float64 storage for RNA-seq), storing only $\approx 1.28\text{ MiB}$ of requested correlations.
3. **Domain-Dependent Inductive Bias (Predictive Generalization):**
   * Guidance yields substantial accuracy gains on multiclass image problems characterized by spatial pixel collinearity (**+4.16 pp on Digits**, **+5.05 pp on Semeion**).
   * Across the complete ten-dataset benchmark suite (522 experimental pipelines), the mean balanced accuracy gain over unguided Basic GA was **+0.94 pp** (6 wins, 4 losses, Wilcoxon $W = 20.0$, $p = 0.492$, exact sign-flip $p = 0.238$, 95% bootstrap CI $[-0.28, +2.31]\text{ pp}$), confirming that correlation guidance functions as an inductive bias rather than a universally superior heuristic.

---

## Repository Structure

```
soft-computing-paper-Data/
├── README.md                      # Primary documentation, findings, and usage instructions
├── LICENSE                        # MIT License
├── requirements.txt               # Pinned Python package dependencies
├── reproduce_all.py               # Master 1-click reproduction script (audits & regenerates all artifacts)
│
├── FINAL_OUTPUT/                  # Replication artifacts and figures
│   ├── Literature_Review_GA_FeatureSelection.xlsx        # 20 papers × 20 columns literature matrix
│   ├── generate_perfect_ieee_paper.py                    # Manuscript generation script
│   ├── make_flawless_figures.py                          # High-resolution figure generator
│   ├── build_excel.py                                    # Literature survey workbook generator
│   └── crisp_figures/                                    # 7 publication figures (300 DPI, vector-rendered)
│       ├── fig1_system_architecture.png
│       ├── fig2_selection_flow.png
│       ├── fig3_ga_convergence.png
│       ├── fig4_method_comparison.png
│       ├── fig5_balanced_accuracy_difference.png
│       ├── fig6_pair_coverage_by_dimension.png
│       └── fig7_cost_components.png
│
├── data/                          # Audited experimental data and logs
│   ├── audit.json                 # Verification log confirming 72/72 bit-exact matches across 522 pipelines
│   ├── findings.json              # Statistical tests, p-values, bootstrap CIs, and pairwise contrasts
│   ├── dataset_method_summary.csv # Mean & SD metrics per dataset and method
│   ├── raw_metrics.csv            # Fold-by-fold raw performance and timing metrics
│   ├── stability.csv              # Feature selection stability metrics across folds
│   └── convergence.csv            # Generation-by-generation fitness convergence traces
│
└── src/                           # Core algorithmic modules
    ├── major_ga.py                # On-demand triangular caching GA and incremental delta arithmetic
    ├── major_experiment.py        # Nested 3-fold CV execution engine across 3 random seeds (17, 29, 43)
    └── audit_results.py           # Verification and statistical analysis pipeline
```

---

## Quickstart: Environment Setup and Reproduction

### 1. Clone the Repository
```bash
git clone https://github.com/ap960664/soft-computing-paper-Data.git
cd soft-computing-paper-Data
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the Master Reproduction Script
```bash
python reproduce_all.py
```

This single command:
1. Validates the environment and dependencies.
2. Checks all 522 pipeline logs, confirming bit-exact equivalence ($\Delta = 0.0$) on all 72 matched runs ($d \le 500$).
3. Verifies benchmark balanced accuracy numbers against raw CSV logs.
4. Regenerates all 7 high-resolution figures into `FINAL_OUTPUT/crisp_figures/`.
5. Regenerates the 20x20 Literature Review Excel workbook into `FINAL_OUTPUT/`.
6. Regenerates the publication-ready IEEE conference manuscript into `FINAL_OUTPUT/`.

---

## Benchmark Datasets

All datasets are public benchmarks from scikit-learn and the UCI Machine Learning Repository:

| Dataset | Instances ($n$) | Features ($d$) | Classes | Domain / Modality |
| :--- | :---: | :---: | :---: | :--- |
| **Wine** | 178 | 13 | 3 | Tabular / Chemical Analysis |
| **Breast Cancer** | 569 | 30 | 2 | Tabular / Clinical Diagnostics |
| **Ionosphere** | 351 | 34 | 2 | Tabular / Radar Signal |
| **Spambase** | 4,601 | 57 | 2 | Tabular / Text Classification |
| **Sonar** | 208 | 60 | 2 | Tabular / Signal Processing |
| **Digits** | 1,797 | 64 | 10 | Image / Vision |
| **Semeion** | 1,593 | 256 | 10 | Image / Vision |
| **Madelon** | 2,600 | 500 | 2 | Synthetic / Non-linear Benchmark |
| **Arcene** | 200 | 10,000 | 2 | Mass Spectrometry / High-Dim |
| **RNA-seq** | 801 | 20,531 | 5 | Genomics / High-Dim Gene Expression |

---

## Audited Benchmark Results Summary

Balanced accuracy (%) across 9 outer folds (3 folds $\times$ 3 seeds, $C = 1.0$ linear SVM):

| Dataset | All-Feature SVM | ANOVA Filter | Random Search | Basic GA | On-Demand Guided GA | Guidance $\Delta$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Wine** | 97.6% | 95.8% | 97.3% | 96.6% | **96.8%** | +0.22 pp |
| **Breast Cancer** | 96.3% | 94.9% | **96.5%** | 96.1% | 95.8% | -0.27 pp |
| **Ionosphere** | 82.8% | 82.6% | 83.5% | **83.8%** | 82.8% | -1.06 pp |
| **Spambase** | **92.1%** | 90.0% | 85.2% | 88.4% | 88.0% | -0.34 pp |
| **Sonar** | 74.1% | 70.0% | 72.2% | 71.6% | **74.0%** | +2.43 pp |
| **Digits** | 95.3% | 93.0% | 73.7% | 84.3% | **88.4%** | **+4.16 pp** |
| **Semeion** | 84.9% | 84.9% | 61.4% | 67.0% | **72.0%** | **+5.05 pp** |
| **Madelon** | 55.6% | **61.5%** | 60.8% | 59.2% | 59.8% | +0.57 pp |
| **Arcene** | **82.5%** | 75.0% | 71.1% | 73.9% | 72.4% | -1.52 pp |
| **RNA-seq** | **100.0%** | **100.0%** | 99.2% | 99.0% | 99.2% | +0.19 pp |
| **Benchmark Mean** | **86.12%** | **84.78%** | **80.09%** | **81.99%** | **82.93%** | **+0.94 pp** |

* **Statistical Significance:** Wilcoxon signed-rank test $W = 20.0$, $p = 0.492$; sign-flip permutation test $p = 0.238$; 95% bootstrap confidence interval $[-0.28, +2.31]\text{ pp}$.

---

## Citation

If you use this codebase, methodology, or experimental findings in your research, please cite:

```bibtex
@inproceedings{pathak2026ondemand,
  author    = {Ashish Pathak},
  title     = {A Reproducible Evaluation of On-Demand Correlation Guidance for Genetic Algorithm Feature Selection},
  booktitle = {Soft Computing Term Paper and Research Evaluation},
  year      = {2026},
  publisher = {Lovely Professional University},
  url       = {https://github.com/ap960664/soft-computing-paper-Data}
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
