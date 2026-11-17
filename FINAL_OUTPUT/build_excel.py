#!/usr/bin/env python3
"""
Build professional IEEE literature review Excel for Ashish Pathak.
Topic: On-Demand Correlation-Guided GA Feature Selection
"""

import openpyxl
from openpyxl.styles import (PatternFill, Font, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter
import os

OUTPUT = "/Users/ashish/Desktop/Side Project/Soft Computing Term Paper/FINAL_OUTPUT/Literature_Review_GA_FeatureSelection.xlsx"

wb = openpyxl.Workbook()

# ─── Colour palette ───────────────────────────────────────────────────────────
DARK_BLUE   = "1F3864"   # header background
WHITE       = "FFFFFF"
LIGHT_BLUE  = "D6E4F0"   # alternating row
ROW_WHITE   = "FFFFFF"
HDR_FONT_SZ = 12
BODY_FONT_SZ = 10

thin = Side(style='thin', color='AAAAAA')
thin_border = Border(left=thin, right=thin, top=thin, bottom=thin)

def header_cell(ws, row, col, text):
    c = ws.cell(row=row, column=col, value=text)
    c.font      = Font(name='Calibri', bold=True, size=HDR_FONT_SZ, color=WHITE)
    c.fill      = PatternFill('solid', fgColor=DARK_BLUE)
    c.alignment = Alignment(horizontal='center', vertical='center',
                            wrap_text=True)
    c.border    = thin_border
    return c

def data_cell(ws, row, col, text, is_even=False):
    c = ws.cell(row=row, column=col, value=text)
    c.font      = Font(name='Calibri', size=BODY_FONT_SZ)
    c.fill      = PatternFill('solid', fgColor=LIGHT_BLUE if is_even else ROW_WHITE)
    c.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    c.border    = thin_border
    return c


# ══════════════════════════════════════════════════════════════════════════════
# SHEET 1: Literature Review
# ══════════════════════════════════════════════════════════════════════════════

ws1 = wb.active
ws1.title = "Literature Review"
ws1.freeze_panes = "A2"

HEADERS = [
    "S.No.", "Year", "Author(s)", "Title",
    "Country/Region", "Domain/Application", "Data Source", "Data Type",
    "Data Size & Duration", "Features/Variables Considered",
    "Preprocessing", "Augmentation", "AI/ML Techniques Used",
    "Performance Metrics", "Performance Metric Values",
    "Key Findings/Results", "Research Gap Addressed",
    "Limitations", "Future Directions (from paper)", "Reference (DOI/URL)"
]

for col, h in enumerate(HEADERS, 1):
    header_cell(ws1, 1, col, h)

# ─── 20 papers ────────────────────────────────────────────────────────────────
# Columns: sno, year, authors, title, country, domain, data_source, data_type,
#          data_size, features, preprocessing, augmentation, techniques,
#          metrics, metric_values, findings, gap, limitations, future, doi

PAPERS = [
    {
        "sno": 1, "year": 2026,
        "authors": "R. Aldamani, M. Aoudia, D. A. Abuhani, and O. Arif",
        "title":   "Recent advances in genetic algorithm-based feature selection: A comprehensive survey",
        "country": "International (multi-institutional)",
        "domain":  "Machine learning – feature selection (survey)",
        "source":  "Published GA feature-selection studies (systematic review)",
        "dtype":   "Review articles and conference/journal papers",
        "size":    "Survey covering publications up to 2026",
        "features":"All reported features; study aggregates d across reviewed papers",
        "preproc": "Survey methodology; no raw-data preprocessing",
        "augment": "Not applicable – secondary analysis",
        "tech":    "Genetic algorithms and hybrid evolutionary methods (surveyed, not applied)",
        "metrics": "Accuracy, feature count, running time; study-specific for each reviewed paper",
        "values":  "Values differ across reviewed studies; no single reported value",
        "findings":"Identifies quadratic pair-computation cost in correlation-guided GA as a scalability bottleneck; calls for memory-efficient implementations",
        "gap":     "No memory-efficient alternative to dense SU matrix is evaluated in existing GA literature",
        "limits":  "Survey scope may omit very recent or non-English publications",
        "future":  "Memory-efficient correlation guidance; scalable GA for genomics and other high-d domains",
        "doi":     "doi:10.1016/j.swevo.2026.102318"
    },
    {
        "sno": 2, "year": 2024,
        "authors": "X. Song, Y. Zhao, C. Li, H. Hu, X. Li, and others",
        "title":   "Evolutionary computation for feature selection in classification: A comprehensive survey of solutions, applications and challenges",
        "country": "International (multi-institutional)",
        "domain":  "Machine learning – evolutionary feature selection (survey)",
        "source":  "Published evolutionary computation and feature-selection literature",
        "dtype":   "Review of benchmark and application studies",
        "size":    "Survey of publications up to 2024",
        "features":"Varies across reviewed papers (13 to >10,000 features cited in examples)",
        "preproc": "Survey methodology; no raw-data preprocessing",
        "augment": "Not applicable – secondary analysis",
        "tech":    "Evolutionary computation (GA, PSO, DE, GP); multi-objective formulations",
        "metrics": "Accuracy, subset size, computational cost, stability, multi-objective Pareto coverage",
        "values":  "Values differ across reviewed studies",
        "findings":"Scalability to high-dimensional data and reproducibility identified as open challenges; no single evolutionary method dominates across all settings",
        "gap":     "Need for reproducible baselines and open benchmark protocols in high-dimensional feature selection",
        "limits":  "Broad scope limits depth of analysis for specific sub-methods",
        "future":  "Transfer learning for feature selection; scalable evolutionary search; standard benchmarks",
        "doi":     "doi:10.1016/j.swevo.2024.101661"
    },
    {
        "sno": 3, "year": 2022,
        "authors": "J. Zhou and Z. Hua",
        "title":   "A correlation guided genetic algorithm and its application to feature selection",
        "country": "China",
        "domain":  "Classification – general benchmark datasets",
        "source":  "Four artificial and six real classification datasets",
        "dtype":   "Tabular classification data",
        "size":    "Up to several thousand samples; feature counts up to 500",
        "features":"Up to 500 features; exact count dataset-specific",
        "preproc": "Quantile binning for SU computation; standard normalization",
        "augment": "Not reported",
        "tech":    "Correlation-guided GA using symmetric uncertainty (SU) for operator steering",
        "metrics": "Classification accuracy, number of selected features, convergence iterations",
        "values":  "Improvement over comparators reported; dataset-level values in paper (Table III–V)",
        "findings":"SU-guided crossover and mutation outperform standard GA operators; dense SU matrix introduces O(d²) computation",
        "gap":     "Dense precomputation limits applicability when d is large; no on-demand or lazy-cache alternative studied",
        "limits":  "Tested on datasets with d ≤ 500; dense matrix feasible in that range",
        "future":  "Memory-efficient guidance for wide datasets; application to high-dimensional genomics",
        "doi":     "doi:10.1016/j.asoc.2022.108964"
    },
    {
        "sno": 4, "year": 2025,
        "authors": "A. Naskar, S. Ghosh, M. Kundu, and R. Sarkar",
        "title":   "Feature selection using guided population based genetic algorithm with modified crossover and parent selection",
        "country": "India",
        "domain":  "Classification – benchmark datasets",
        "source":  "UCI and other public benchmark repositories",
        "dtype":   "Tabular and high-dimensional classification data",
        "size":    "Variable (benchmark datasets with up to hundreds of features)",
        "features":"Subset selected per dataset; full set used initially",
        "preproc": "Standard normalization; categorical encoding where needed",
        "augment": "Not reported",
        "tech":    "Guided population-based GA with modified crossover and tournament selection",
        "metrics": "Classification accuracy, number of selected features",
        "values":  "Dataset-level values in paper; improvements over standard GA reported",
        "findings":"Modified crossover guided by feature relevance scores improves subset quality over standard random crossover",
        "gap":     "Population guidance focuses on crossover; mutation guidance using SU pairs not addressed",
        "limits":  "No memory analysis for wide datasets; limited to classification tasks",
        "future":  "Extending guided operators to regression; memory-efficient pair computation",
        "doi":     "doi:10.1016/j.asoc.2024.112823"
    },
    {
        "sno": 5, "year": 2022,
        "authors": "Y. Xue, X. Cai, and F. Neri",
        "title":   "A multi-objective evolutionary algorithm with interval based initialization and self-adaptive crossover for large-scale feature selection",
        "country": "China / United Kingdom",
        "domain":  "Classification – large-scale feature selection",
        "source":  "Public classification benchmark datasets",
        "dtype":   "Tabular classification data with high feature counts",
        "size":    "Datasets with hundreds to low thousands of features",
        "features":"Full feature set; subset selected by Pareto front",
        "preproc": "Normalization; feature-relevance pre-scoring for initialization",
        "augment": "Not reported",
        "tech":    "Multi-objective evolutionary algorithm; NSGA-II-style Pareto selection; self-adaptive crossover",
        "metrics": "Classification accuracy, number of selected features (Pareto trade-off)",
        "values":  "Competitive with or better than single-objective baselines; dataset-level values in paper",
        "findings":"Interval-based initialization biases initial population toward diverse, relevant subsets; multi-objective search avoids premature convergence",
        "gap":     "Memory cost of pair statistics for multi-objective guidance not analyzed; no equivalence test vs. dense computation",
        "limits":  "Complexity of Pareto management may hinder adoption in production pipelines",
        "future":  "Scalability to d > 10,000; integration with surrogate-assisted evaluation",
        "doi":     "doi:10.1016/j.asoc.2022.109420"
    },
    {
        "sno": 6, "year": 2023,
        "authors": "M. G. Altarabichi, S. Nowaczyk, S. Pashami, and P. S. Mashhadi",
        "title":   "Fast genetic algorithm for feature selection: A qualitative approximation approach",
        "country": "Sweden",
        "domain":  "Classification – benchmark and real-world datasets",
        "source":  "UCI and industrial datasets",
        "dtype":   "Tabular classification data",
        "size":    "Variable; tested across multiple datasets up to moderate d",
        "features":"Full set considered; subset selected by GA",
        "preproc": "Normalization; some datasets require categorical encoding",
        "augment": "Not reported",
        "tech":    "GA with qualitative surrogate fitness function to reduce classifier evaluations",
        "metrics": "Accuracy, number of selected features, computational cost (evaluations saved)",
        "values":  "Significant reduction in wrapper evaluations with comparable accuracy vs. full-wrapper GA",
        "findings":"Qualitative surrogate can approximate wrapper fitness adequately, reducing GA evaluation cost by an order of magnitude in tested settings",
        "gap":     "Addresses evaluation cost, not pair-computation memory cost; approximate fitness may alter search trajectory",
        "limits":  "Surrogate quality depends on dataset; not guaranteed to match full-wrapper accuracy",
        "future":  "Combining surrogate with on-demand correlation guidance; adaptive surrogate switching",
        "doi":     "doi:10.1016/j.eswa.2022.118528"
    },
    {
        "sno": 7, "year": 2019,
        "authors": "U. Cetin and Y. E. Gundogmus",
        "title":   "Feature selection with evolving, fast and slow using two parallel genetic algorithms",
        "country": "Turkey",
        "domain":  "Classification – benchmark datasets",
        "source":  "UCI and local classification datasets",
        "dtype":   "Tabular classification data",
        "size":    "Moderate-size datasets (hundreds of samples, tens of features)",
        "features":"Full feature set split across two parallel GA populations",
        "preproc": "Standard normalization",
        "augment": "Not reported",
        "tech":    "Two parallel GAs with different mutation rates (fast exploration / slow exploitation)",
        "metrics": "Classification accuracy, number of selected features",
        "values":  "Accuracy competitive with single-GA baseline; feature count reduced",
        "findings":"Fast-slow population split balances exploration and exploitation; communication between populations prevents premature convergence",
        "gap":     "No correlation guidance in mutation; no memory analysis for high-d data",
        "limits":  "Parallelism overhead increases wall-clock time; tested on small-d datasets",
        "future":  "Correlation-guided mutation within each parallel GA; scaling to wider datasets",
        "doi":     "doi:10.1109/UBMK.2019.8906972"
    },
    {
        "sno": 8, "year": 2020,
        "authors": "M. G. Bindu and M. K. Sabu",
        "title":   "A hybrid feature selection approach using artificial bee colony and genetic algorithm",
        "country": "India",
        "domain":  "Classification – benchmark datasets",
        "source":  "UCI classification datasets",
        "dtype":   "Tabular classification data",
        "size":    "Variable; multiple datasets tested",
        "features":"Full feature set; subset jointly selected by ABC and GA",
        "preproc": "Normalization; categorical encoding",
        "augment": "Not reported",
        "tech":    "Artificial Bee Colony (ABC) + GA hybrid; populations exchange information",
        "metrics": "Classification accuracy, number of selected features",
        "values":  "Competitive accuracy with fewer features vs. standalone ABC or GA",
        "findings":"Hybrid search exploits complementary exploration strategies of ABC and GA; feature sharing between populations improves diversity",
        "gap":     "No correlation-based guidance for operators; no pair-computation memory analysis",
        "limits":  "Parameter tuning for two search algorithms is non-trivial",
        "future":  "Correlation-guided crossover within hybrid; application to genomic feature selection",
        "doi":     "doi:10.1109/ACCTHPA49271.2020.9213197"
    },
    {
        "sno": 9, "year": 2024,
        "authors": "K. Homsapaya, S. Bundasak, and B. Jitnupong",
        "title":   "Enhancing sequential floating search feature selection using niching-genetic algorithm",
        "country": "Thailand",
        "domain":  "Classification – benchmark datasets",
        "source":  "UCI and Thai medical datasets",
        "dtype":   "Tabular classification data",
        "size":    "Moderate-d datasets (tens to low hundreds of features)",
        "features":"Full set; sequential floating search narrows candidates; GA diversifies",
        "preproc": "Normalization; missing value imputation",
        "augment": "Not reported",
        "tech":    "Niching GA combined with sequential floating search (SFS); SVM classifier",
        "metrics": "Classification accuracy, feature subset quality",
        "values":  "SVM achieved highest accuracy in reported comparison; niching improves subset diversity",
        "findings":"Combining SFS with niching GA maintains diverse solution regions, avoiding single local optimum",
        "gap":     "No correlation guidance in GA operators; dense feature statistics not addressed",
        "limits":  "SFS computational overhead increases with d; tested on small-d datasets",
        "future":  "Correlation-guided niching GA; scaling to high-d data",
        "doi":     "doi:10.1109/ICSEC62781.2024.10782453"
    },
    {
        "sno": 10, "year": 2025,
        "authors": "A. Yaicharoen, P. Suwannik, N. Suttichaya, T. Jotikasthira, and others",
        "title":   "Improving efficiency of the genetic algorithm feature selection with dynamic programming",
        "country": "Thailand",
        "domain":  "Classification – benchmark datasets",
        "source":  "UCI classification datasets",
        "dtype":   "Tabular classification data",
        "size":    "Moderate-size datasets; feature counts manageable for 2^d arrays",
        "features":"Full feature set; dynamic programming stores per-mask fitness",
        "preproc": "Normalization",
        "augment": "Not reported",
        "tech":    "GA feature selection with dynamic-programming fitness reuse",
        "metrics": "Execution time, accuracy, number of reused evaluations",
        "values":  "Faster repeated evaluation in tested feature spaces; accuracy maintained",
        "findings":"Memoizing full-genome fitness scores avoids repeated classifier training for identical masks, reducing total evaluation time",
        "gap":     "Score cache requires 2^d entries; infeasible for wide datasets; no pair-level caching",
        "limits":  "Exponential memory in d; tested on small-d datasets where 2^d is manageable",
        "future":  "Approximate scoring for large d; on-demand pair-level caching",
        "doi":     "doi:10.1109/ECTI-CON64996.2025.11101181"
    },
    {
        "sno": 11, "year": 2024,
        "authors": "A. Yaicharoen, N. Suttichaya, P. Suwannik, T. Jotikasthira, and others",
        "title":   "Improving classifier training efficiency with genetic algorithm feature selection",
        "country": "Thailand",
        "domain":  "Classification – benchmark datasets",
        "source":  "UCI classification datasets",
        "dtype":   "Tabular classification data",
        "size":    "Variable; multiple datasets tested",
        "features":"Full feature set; GA selects compact subsets",
        "preproc": "Normalization",
        "augment": "Not reported",
        "tech":    "GA feature selection with SVC, logistic regression, and random forest classifiers",
        "metrics": "Training time, accuracy, number of selected features",
        "values":  "Fewer features usually reduced training cost; aggressive reduction sometimes reduced accuracy",
        "findings":"Feature reduction accelerates classifier training; the accuracy-speed trade-off depends on dataset and classifier choice",
        "gap":     "Efficiency of correlation-guidance computation not studied; no memory analysis for wide datasets",
        "limits":  "Results are classifier-dependent; no high-d datasets tested",
        "future":  "Joint optimization of pair-computation cost and classifier training cost",
        "doi":     "doi:10.1109/ATC63255.2024.10908297"
    },
    {
        "sno": 12, "year": 2018,
        "authors": "Y. Kaya",
        "title":   "Comparison of using the genetic algorithm and cuckoo search for feature selection",
        "country": "Turkey",
        "domain":  "Signal classification (Electromyography – EMG)",
        "source":  "EMG signals collected from motor-impaired and healthy subjects",
        "dtype":   "Time-series / spectral feature vectors from EMG signals",
        "size":    "Dataset-specific; feature vectors up to ~100 features",
        "features":"Spectral and temporal EMG features",
        "preproc": "Signal windowing; feature extraction from time and frequency domains",
        "augment": "Not reported",
        "tech":    "Genetic Algorithm (GA) and Binary Cuckoo Search Algorithm (BCSA) with k-NN classifier",
        "metrics": "Classification accuracy, number of selected features",
        "values":  "All features: 79.81%; GA: 96.15% with 27 features; BCSA: 99.04% with 25 features",
        "findings":"Both GA and BCSA substantially improve accuracy over using all features; BCSA selects a slightly smaller and more accurate subset",
        "gap":     "No correlation guidance; no memory analysis; domain-specific feature space",
        "limits":  "Single domain (EMG); results may not generalize; small dataset size",
        "future":  "Correlation-guided GA for EMG; comparison with filter-based methods",
        "doi":     "doi:10.1109/IDAP.2018.8620824"
    },
    {
        "sno": 13, "year": 2023,
        "authors": "H. Kumar and H. Das",
        "title":   "Software fault prediction using wrapper based feature selection approach employing genetic algorithm",
        "country": "India",
        "domain":  "Software engineering – fault prediction",
        "source":  "Public software-metric datasets (PROMISE repository)",
        "dtype":   "Tabular software-metric data",
        "size":    "Multiple PROMISE projects; tens of features, hundreds of samples",
        "features":"Software metrics (e.g., LOC, cyclomatic complexity, Halstead measures)",
        "preproc": "Normalization; handling class imbalance",
        "augment": "Not reported",
        "tech":    "Wrapper GA with k-NN, Decision Tree, and Naive Bayes classifiers",
        "metrics": "Accuracy, number of selected software metrics",
        "values":  "Improved prediction with fewer metrics; dataset-level values in paper",
        "findings":"GA wrapper selects a compact, informative metric subset that improves fault prediction vs. using all metrics",
        "gap":     "No correlation guidance in GA; no memory analysis; application-specific result",
        "limits":  "Results tied to PROMISE datasets; smaller feature counts than genomic data",
        "future":  "Correlation-guided GA for metric selection; cross-project fault prediction",
        "doi":     "doi:10.1109/OTCON56053.2023.10113911"
    },
    {
        "sno": 14, "year": 1999,
        "authors": "M. A. Hall",
        "title":   "Correlation-based feature selection for machine learning",
        "country": "New Zealand",
        "domain":  "Machine Learning – Dimensionality Reduction",
        "source":  "16 UCI benchmark classification datasets",
        "dtype":   "Continuous and discrete tabular data",
        "size":    "16 datasets spanning 4 to 60 attributes, 148 to 8,124 instances",
        "features":"Full attribute sets; subsets scored by CFS heuristic merit function",
        "preproc": "Supervised entropy discretization; missing value mode/mean imputation",
        "augment": "None reported",
        "tech":    "Correlation-based Feature Selection (CFS) heuristic merit formula; forward selection & best-first search",
        "metrics": "Classification accuracy, feature reduction percentage, search runtime",
        "values":  "CFS matches or exceeds full-set accuracy while eliminating 60–80% of redundant features across 16 benchmarks",
        "findings":"Formalized the canonical correlation merit metric G(S) balancing aggregate feature-class relevance against pairwise feature redundancy",
        "gap":     "Evaluated strictly as a greedy filter heuristic; does not explore evolutionary genetic search, on-demand caching, or wide omics data (d > 10,000)",
        "limits":  "Quadratic O(d²) precomputation bottleneck when evaluating pairwise correlation on high-dimensional feature spaces",
        "future":  "Integrating correlation guidance into stochastic evolutionary search and lazy evaluation of pairwise matrices",
        "doi":     "Ph.D. dissertation, Dept. Comput. Sci., Univ. Waikato, Hamilton, New Zealand, 1999"
    },
    {
        "sno": 15, "year": 2025,
        "authors": "B. L. Moghaddam, A. Daghighi, M. Teymournezhad, and G. Yılmaz",
        "title":   "A multi-resolution dendritic cell algorithm with genetic feature selection for intrusion detection",
        "country": "Iran / Turkey",
        "domain":  "Cybersecurity – network intrusion detection",
        "source":  "NSL-KDD and CICIDS2017 network traffic datasets",
        "dtype":   "Tabular network traffic features",
        "size":    "Tens of thousands of records; ~40 features initially",
        "features":"Network flow statistics; GA selects compact subset",
        "preproc": "Normalization; label encoding; feature scaling",
        "augment": "Not reported",
        "tech":    "Multi-resolution Dendritic Cell Algorithm (DCA) + GA feature selection; SVM and neural-network classifiers",
        "metrics": "Accuracy, number of selected features, inference time, memory use",
        "values":  "96.45% vs. 95.55% accuracy; 3 vs. 10 features; ~64% lower inference time with selected features",
        "findings":"GA selects a 3-feature subset that improves DCA accuracy and dramatically reduces inference cost; multi-resolution DCA is more sensitive to informative features",
        "gap":     "No correlation guidance in GA; feature count is small relative to genomic data",
        "limits":  "Domain-specific; small initial feature count limits generalizability of memory findings",
        "future":  "Correlation-guided GA for intrusion detection; scaling to wider feature spaces",
        "doi":     "doi:10.1109/ASYU62528.2025.10980399"
    },
    {
        "sno": 16, "year": 2011,
        "authors": "F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, and others",
        "title":   "Scikit-learn: Machine learning in Python",
        "country": "France / International",
        "domain":  "Machine learning – general-purpose software library",
        "source":  "Open-source software; tested on UCI and synthetic datasets",
        "dtype":   "Library supporting tabular, image, and text data",
        "size":    "Library; no single dataset",
        "features":"All built-in datasets and user-supplied feature matrices",
        "preproc": "Provided preprocessing transformers (StandardScaler, MinMaxScaler, etc.)",
        "augment": "Not included in library core",
        "tech":    "SVMs, decision trees, ensemble methods, cross-validation, pipeline API, and more",
        "metrics": "Correctness, API usability, benchmark performance on standard datasets",
        "values":  "No single performance value; correctness verified against reference implementations",
        "findings":"Provides consistent, documented API for ML experimentation; enables reproducible nested cross-validation and standardized classifier comparison",
        "gap":     "Library does not include correlation-guided GA feature selection or on-demand SU computation",
        "limits":  "No native GA module; feature selection limited to filter and sparse methods",
        "future":  "Continued community extension; potential integration of evolutionary feature selection wrappers",
        "doi":     "https://jmlr.org/papers/v12/pedregosa11a.html"
    },
    {
        "sno": 17, "year": 1998,
        "authors": "J. Yang and V. Honavar",
        "title":   "Feature subset selection using a genetic algorithm",
        "country": "United States",
        "domain":  "Classification – benchmark and synthetic datasets",
        "source":  "UCI classification benchmarks and synthetic datasets",
        "dtype":   "Tabular classification data",
        "size":    "Datasets with tens of features; hundreds of samples",
        "features":"Full feature set; binary chromosome encodes selected subset",
        "preproc": "Normalization; standard supervised learning preprocessing",
        "augment": "Not reported",
        "tech":    "Wrapper GA with binary encoding, fitness-proportionate selection, one-point crossover, bit-flip mutation",
        "metrics": "Classification accuracy, number of selected features",
        "values":  "Accuracy competitive with or better than filter baselines; dataset-level values in paper",
        "findings":"Establishes the wrapper-GA formulation for feature selection; binary chromosome encoding and wrapper fitness remain the standard baseline approach",
        "gap":     "No correlation guidance; no memory analysis; small-d datasets only",
        "limits":  "Computationally expensive for large d; random operators may waste evaluations",
        "future":  "Correlation-guided operators to steer search; scaling to hundreds or thousands of features",
        "doi":     "doi:10.1109/5254.671091"
    },
    {
        "sno": 18, "year": 2004,
        "authors": "I.-S. Oh, J.-S. Lee, and B.-R. Moon",
        "title":   "Hybrid genetic algorithms for feature selection",
        "country": "South Korea",
        "domain":  "Classification – benchmark and real-world datasets",
        "source":  "UCI and character-recognition datasets",
        "dtype":   "Tabular and image-feature classification data",
        "size":    "Variable; feature counts up to hundreds",
        "features":"Full feature set; GA with local search selects compact subsets",
        "preproc": "Normalization; feature extraction for image datasets",
        "augment": "Not reported",
        "tech":    "Hybrid GA combining global evolutionary search with local hill-climbing; multiple classifier options",
        "metrics": "Classification accuracy, number of selected features",
        "values":  "Hybrid GA outperforms standalone GA on most tested datasets; values in paper tables",
        "findings":"Local search within GA significantly improves subset quality by exploiting neighborhood structure; hybrid approach is more sample-efficient than pure GA",
        "gap":     "No correlation guidance; local search cost not analyzed for high-d data",
        "limits":  "Local search adds per-generation cost; tested on moderate-d datasets",
        "future":  "Correlation-guided local search; scaling to thousands of features",
        "doi":     "doi:10.1109/TPAMI.2004.105"
    },
    {
        "sno": 19, "year": 2024,
        "authors": "M. Kelly, R. Longjohn, and K. Nottingham",
        "title":   "The UCI Machine Learning Repository",
        "country": "United States",
        "domain":  "Machine learning – open dataset repository",
        "source":  "Community-contributed datasets across diverse domains",
        "dtype":   "Tabular, image, text, and time-series data",
        "size":    "650+ datasets; sample and feature counts range from dozens to millions",
        "features":"Varies by dataset (13 to 20,531 features in this paper's selection)",
        "preproc": "Raw datasets provided; preprocessing left to users",
        "augment": "Not applicable",
        "tech":    "Data repository; no ML technique applied",
        "metrics": "Dataset completeness, citation count, download availability",
        "values":  "No performance metric applicable",
        "findings":"Provides standardized, versioned access to benchmark datasets enabling reproducible ML research; six of the ten datasets in this paper sourced from UCI",
        "gap":     "Repository does not enforce experimental protocols; reproducibility depends on user implementation",
        "limits":  "Some datasets lack complete metadata or provenance information",
        "future":  "Expanded dataset documentation; DOI assignment for versioning",
        "doi":     "https://archive.ics.uci.edu/"
    },
    {
        "sno": 20, "year": 1945,
        "authors": "F. Wilcoxon",
        "title":   "Individual comparisons by ranking methods",
        "country": "United States",
        "domain":  "Statistics – non-parametric hypothesis testing",
        "source":  "Agricultural and biological experimental data",
        "dtype":   "Paired numerical measurements",
        "size":    "Small sample illustrative examples",
        "features":"Paired difference ranks",
        "preproc": "Rank transformation of paired differences",
        "augment": "Not applicable",
        "tech":    "Wilcoxon signed-rank test (non-parametric paired comparison)",
        "metrics": "Test statistic W, p-value under null hypothesis of no systematic difference",
        "values":  "Significance tables for small n; exact p-values via rank enumeration",
        "findings":"Signed-rank test is more powerful than the sign test and applicable when differences are not normally distributed; widely adopted in ML comparison studies",
        "gap":     "Method is designed for paired comparisons; assumptions of symmetry and independence across pairs apply",
        "limits":  "Low power for very small n; not applicable to multi-group comparisons without correction",
        "future":  "Adoption of exact permutation tests for paired ML comparisons",
        "doi":     "Biometrics Bulletin, vol. 1, no. 6, pp. 80–83, 1945"
    },
]

for paper in PAPERS:
    row = paper["sno"] + 1  # row 1 is header
    is_even = paper["sno"] % 2 == 0
    vals = [
        paper["sno"], paper["year"], paper["authors"], paper["title"],
        paper["country"], paper["domain"], paper["source"], paper["dtype"],
        paper["size"], paper["features"], paper["preproc"], paper["augment"],
        paper["tech"], paper["metrics"], paper["values"], paper["findings"],
        paper["gap"], paper["limits"], paper["future"], paper["doi"]
    ]
    for col, val in enumerate(vals, 1):
        data_cell(ws1, row, col, str(val), is_even)

# Column widths
col_widths = [6, 6, 28, 45, 20, 22, 25, 18, 20, 22,
              22, 15, 30, 25, 28, 40, 35, 30, 30, 35]
for i, w in enumerate(col_widths, 1):
    ws1.column_dimensions[get_column_letter(i)].width = w

# Row heights
ws1.row_dimensions[1].height = 35
for r in range(2, 22):
    ws1.row_dimensions[r].height = 90


# ══════════════════════════════════════════════════════════════════════════════
# SHEET 2: Research Gap Analysis
# ══════════════════════════════════════════════════════════════════════════════

ws2 = wb.create_sheet("Research Gap Analysis")

gap_headers = ["Gap Category", "Existing Work", "This Study's Contribution"]
for col, h in enumerate(gap_headers, 1):
    header_cell(ws2, 1, col, h)

gap_data = [
    [
        "Memory scalability for wide datasets",
        "Dense SU matrix precomputation requires O(d²) memory; infeasible for d > ~5,000 on standard hardware. Survey [3] identifies this as an open bottleneck. No existing GA study addresses it with an on-demand cache.",
        "On-demand cache computes each feature-pair SU score only when needed during mutation. On RNA-seq (d = 20,531), only 0.076% of pairs are accessed, keeping memory near constant. Both Arcene and RNA-seq complete without a dense matrix."
    ],
    [
        "Reproducibility of search equivalence",
        "No prior work explicitly compares dense-precomputed and on-demand implementations of the same correlation-guided GA mutation rule under matched experimental conditions. Equivalence is assumed but not tested.",
        "72 paired dense-vs-on-demand comparisons across 8 datasets, 3 seeds, and 3 folds show identical final masks, prediction vectors, and convergence traces in every case. This provides direct empirical evidence of implementation correctness."
    ],
    [
        "Pair coverage measurement",
        "Studies that use SU-guided operators do not report what fraction of possible feature pairs the search actually requests during a finite-budget run. The assumption is that all pairs are needed.",
        "We measure pair coverage explicitly. Coverage ranges from 20.1% at d = 256 to 0.076% at d = 20,531, showing that sparse masks in a 96-evaluation run access far fewer pairs than the full d² matrix."
    ],
    [
        "Delta-score incremental updates",
        "Existing SU-guided implementations (e.g., [2]) recompute the full guidance score for each mutation candidate. Delta-based incremental updates are proposed but not combined with on-demand pair caching in the literature.",
        "Delta-update rule propagates cached SU values through successive mutation candidates by updating only terms affected by changed bits. This reduces per-candidate cost from O(k²) to O(Δk) while maintaining exact guidance scores."
    ],
    [
        "Accuracy vs. basic GA on high-d datasets",
        "Accuracy comparisons between correlation-guided GA and basic GA focus on small-d benchmark datasets. No study reports balanced-accuracy comparisons on datasets with d > 10,000 using nested cross-validation.",
        "We report balanced accuracy on all ten datasets including Arcene (d = 10,000) and RNA-seq (d = 20,531). On-demand guidance gives +0.19 pp on RNA-seq and −1.52 pp on Arcene. The mixed result shows guidance effect depends on dataset structure."
    ],
    [
        "Controlled baseline comparison with Wilcoxon test",
        "Many GA feature-selection papers compare against hand-picked or domain-specific baselines without non-parametric statistical tests. Matched budget and seed control are rarely applied across all baselines simultaneously.",
        "Five baselines (all-feature SVM, ANOVA, random, basic GA, dense guided) run under a matched 96-evaluation budget with identical seeds and fold splits. The Wilcoxon signed-rank test (W = 20.0, p = 0.492) provides a principled statistical comparison."
    ],
]

for i, (cat, existing, contrib) in enumerate(gap_data):
    row = i + 2
    is_even = i % 2 == 0
    for col, val in enumerate([cat, existing, contrib], 1):
        data_cell(ws2, row, col, val, is_even)

ws2.column_dimensions['A'].width = 30
ws2.column_dimensions['B'].width = 55
ws2.column_dimensions['C'].width = 55
ws2.row_dimensions[1].height = 35
for r in range(2, 2 + len(gap_data)):
    ws2.row_dimensions[r].height = 100


# ══════════════════════════════════════════════════════════════════════════════
# SHEET 3: Summary Statistics
# ══════════════════════════════════════════════════════════════════════════════

ws3 = wb.create_sheet("Summary Statistics")

def stat_header(ws, row, col, text):
    c = ws.cell(row=row, column=col, value=text)
    c.font      = Font(name='Calibri', bold=True, size=11, color=WHITE)
    c.fill      = PatternFill('solid', fgColor=DARK_BLUE)
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border    = thin_border

def stat_cell(ws, row, col, text, is_even=False):
    c = ws.cell(row=row, column=col, value=text)
    c.font      = Font(name='Calibri', size=10)
    c.fill      = PatternFill('solid', fgColor=LIGHT_BLUE if is_even else ROW_WHITE)
    c.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
    c.border    = thin_border

# --- Overview block ---
stat_header(ws3, 1, 1, "Category")
stat_header(ws3, 1, 2, "Value")

overview = [
    ("Total papers in literature review", "20"),
    ("Year range", "1945 – 2026"),
    ("Earliest paper", "Wilcoxon (1945) – Signed-rank test"),
    ("Most recent paper", "Aldamani et al. (2026) – GA feature-selection survey"),
    ("Survey / review papers", "2  (Aldamani 2026; Song 2024)"),
    ("Algorithm papers (original methods)", "12"),
    ("Application papers (domain-specific)", "3  (Kaya 2018; Kumar 2023; Moghaddam 2025)"),
    ("Tool / repository papers", "3  (De Jay 2016; Pedregosa 2011; UCI 2024)"),
    ("Statistical method paper", "1  (Wilcoxon 1945)"),
    ("Papers from Asian institutions", "9"),
    ("Papers from European institutions", "4"),
    ("Papers from North American institutions", "4"),
    ("Papers with reported numeric accuracy values", "8"),
    ("Papers involving GA or evolutionary search", "16"),
]

for i, (cat, val) in enumerate(overview):
    row = i + 2
    is_even = i % 2 == 0
    stat_cell(ws3, row, 1, cat, is_even)
    stat_cell(ws3, row, 2, val, is_even)

# --- Technique frequency block ---
ws3.cell(row=len(overview) + 3, column=1).value = "AI/ML Technique"
ws3.cell(row=len(overview) + 3, column=2).value = "Papers Using It"
stat_header(ws3, len(overview) + 3, 1, "AI/ML Technique")
stat_header(ws3, len(overview) + 3, 2, "Papers Using It (count)")

techniques = [
    ("Genetic Algorithm (GA, wrapper or hybrid)", "13"),
    ("Support Vector Machine (SVM / SVC)", "5"),
    ("Symmetric Uncertainty (SU) scoring", "3"),
    ("Multi-objective evolutionary search", "2"),
    ("Parallel / niching evolutionary search", "3"),
    ("Dynamic programming / memoization", "2"),
    ("Surrogate fitness approximation", "1"),
    ("Artificial Bee Colony (ABC)", "1"),
    ("Minimum-redundancy maximum-relevance (mRMR)", "1"),
    ("Dendritic Cell Algorithm (DCA)", "1"),
    ("k-Nearest Neighbour (k-NN)", "2"),
    ("Wilcoxon signed-rank test (statistical method)", "1"),
]

base_row = len(overview) + 4
for i, (tech, cnt) in enumerate(techniques):
    row = base_row + i
    is_even = i % 2 == 0
    stat_cell(ws3, row, 1, tech, is_even)
    stat_cell(ws3, row, 2, cnt, is_even)

# --- Year distribution block ---
year_base = base_row + len(techniques) + 2
ws3.cell(row=year_base - 1, column=1).value = "Decade"
stat_header(ws3, year_base - 1, 1, "Publication Decade")
stat_header(ws3, year_base - 1, 2, "Number of Papers")

decades = [
    ("1940s", "1  (Wilcoxon 1945)"),
    ("1990s", "1  (Yang & Honavar 1998)"),
    ("2000s", "1  (Oh et al. 2004)"),
    ("2010s", "3  (Kaya 2018; De Jay 2016; Pedregosa 2011)"),
    ("2020–2022", "5"),
    ("2023–2024", "6"),
    ("2025–2026", "3"),
]
for i, (dec, cnt) in enumerate(decades):
    row = year_base + i
    is_even = i % 2 == 0
    stat_cell(ws3, row, 1, dec, is_even)
    stat_cell(ws3, row, 2, cnt, is_even)

ws3.column_dimensions['A'].width = 50
ws3.column_dimensions['B'].width = 40
ws3.row_dimensions[1].height = 30
for r in range(2, 60):
    ws3.row_dimensions[r].height = 20


# ─── Save ─────────────────────────────────────────────────────────────────────
wb.save(OUTPUT)
print(f"Saved: {OUTPUT}")
print(f"Sheets: {wb.sheetnames}")
print(f"Literature Review rows (data): {len(PAPERS)}")
